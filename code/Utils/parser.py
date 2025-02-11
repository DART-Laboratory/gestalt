import pandas as pd
import numpy as np
import os
import json
import tarfile
import argparse

def extract_json_from_tar_gz(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        if filename.endswith('.json.tar.gz'):
            try:
                with tarfile.open(file_path, 'r:gz') as tar:
                    tar.extractall(path=directory)
            except Exception as e:
                print(f"Failed to extract {filename}: {str(e)}")
        else:
            pass


def json_file_iterator(folder_path):
    for file_name in sorted(os.listdir(folder_path)):
        if file_name.endswith('.json') or '.json.' in file_name:
            file_path = os.path.join(folder_path, file_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    for line in file:
                        try:
                            record = json.loads(line.strip())
                            yield record
                        except json.JSONDecodeError as e:
                            print(f"Error decoding JSON from {file_name}: {e}")
            except FileNotFoundError:
                print(f"File not found: {file_path}")
            except IOError as e:
                print(f"Error opening file {file_path}: {e}")

def prepare_id_files(folder_path):
    global title, scene, cdm

    id_to_type_file = f'{directory}/{title}_data/{scene}_id_to_type.json'
    net2prop_file = f'{directory}/{title}_data/{scene}_net2prop.json'

    os.makedirs(f'{directory}/{title}_data/', exist_ok=True) 

    net2prop_buffer = []
    id_to_type_buffer = []
    buffer_size = 100000  

    def append_to_file(file_path, data):
        with open(file_path, 'a') as file:
            for item in data:
                file.write(json.dumps(item) + '\n')

    def check_and_flush_buffer():
        nonlocal net2prop_buffer, id_to_type_buffer
        if len(net2prop_buffer) >= buffer_size:
            append_to_file(net2prop_file, net2prop_buffer)
            net2prop_buffer = []
        if len(id_to_type_buffer) >= buffer_size:
            append_to_file(id_to_type_file, id_to_type_buffer)
            id_to_type_buffer = []

    for line in json_file_iterator(folder_path):
        str_line = json.dumps(line)
        
        if f"avro.cdm{cdm}.NetFlowObject" in str_line:
            net_flow_object = line['datum'][f'com.bbn.tc.schema.avro.cdm{cdm}.NetFlowObject']
            try:
                nodeid = net_flow_object['uuid']
                srcaddr = net_flow_object['localAddress'].get('string')
                srcport = net_flow_object['localPort'].get('int')
                dstaddr = net_flow_object['remoteAddress'].get('string')
                dstport = net_flow_object['remotePort'].get('int')

                net2prop_data = {nodeid: [srcaddr, srcport, dstaddr, dstport]}
                id_to_type_data = {nodeid: 'NETFLOW'}
                net2prop_buffer.append(net2prop_data)
                id_to_type_buffer.append(id_to_type_data)
            except: 
                pass

        if f"schema.avro.cdm{cdm}.Subject" in str_line:
            subject = line['datum'][f'com.bbn.tc.schema.avro.cdm{cdm}.Subject']
            uuid = subject['uuid']
            record_type = subject['type'] 
            id_to_type_data = {uuid: record_type}
            id_to_type_buffer.append(id_to_type_data)

        if f"schema.avro.cdm{cdm}.FileObject" in str_line:
            file_object = line['datum'][f'com.bbn.tc.schema.avro.cdm{cdm}.FileObject']
            uuid = file_object['uuid']
            file_type = file_object['type']
            id_to_type_data = {uuid: file_type}
            id_to_type_buffer.append(id_to_type_data)
        
        check_and_flush_buffer()
            
    append_to_file(net2prop_file, net2prop_buffer)
    append_to_file(id_to_type_file, id_to_type_buffer)

def load_dict_from_jsonl(file_path):
    result = {}
    with open(file_path, 'r') as file:
        for line in file:
            data = json.loads(line)
            result.update(data)
    return result

def stitch(data_buffer):
    global title, scene, cdm, output_dir 

    id_to_type_file = f'{directory}/{title}_data/{scene}_id_to_type.json'
    net2prop_file = f'{directory}/{title}_data/{scene}_net2prop.json' 
    
    id_to_type = load_dict_from_jsonl(id_to_type_file)
    net2prop = load_dict_from_jsonl(net2prop_file)
    info = data_buffer
    
    for i in range(len(info)):
        try:
            typ = id_to_type[info[i]['objectID']]
            info[i]['object'] = typ
            info[i]['actor_type'] = id_to_type[info[i]['actorID']]
            if typ == 'NETFLOW':
                attr = net2prop[info[i]['objectID']]
                info[i]['path'] = attr[0]+' '+str(attr[1])+' '+attr[2]+' '+str(attr[3])
        except:
            info[i]['object'] = None
            info[i]['actor_type'] = None
            
    df = pd.DataFrame.from_records(info)
    df = df.dropna()

    output_file = os.path.join(output_dir, f"{title}_{scene}.json")
    df.to_json(output_file, orient='records', lines=True)  

def query_json(folder_path):
    global title, scene, cdm 

    edge_types = set([
        'EVENT_CLOSE', 'EVENT_OPEN', 'EVENT_READ', 'EVENT_WRITE', 'EVENT_EXECUTE',
        'EVENT_RECVFROM', 'EVENT_RECVMSG', 'EVENT_SENDMSG', 'EVENT_SENDTO',
    ])

    info_buffer = []

    for line in json_file_iterator(folder_path):
        
        x = line            

        try:
            action = x['datum'][f'com.bbn.tc.schema.avro.cdm{cdm}.Event']['type']
        except:
            action = ''

        try:
            hostid = x['datum'][f'com.bbn.tc.schema.avro.cdm{cdm}.Event']['hostId']
        except:
            hostid = ''

        try:
            actor = x['datum'][f'com.bbn.tc.schema.avro.cdm{cdm}.Event']['subject'][f'com.bbn.tc.schema.avro.cdm{cdm}.UUID']
        except:
            actor = ''

        try:
            obj = x['datum'][f'com.bbn.tc.schema.avro.cdm{cdm}.Event']['predicateObject'][f'com.bbn.tc.schema.avro.cdm{cdm}.UUID']
        except:
            obj = ''

        try:
            cmd = x['datum'][f'com.bbn.tc.schema.avro.cdm{cdm}.Event']['properties']['map']['exec']
        except:
            cmd = ''

        try:
            path = x['datum'][f'com.bbn.tc.schema.avro.cdm{cdm}.Event']['predicateObjectPath']['string']
        except:
            path = ''

        try:
            timestampnano = x['datum'][f'com.bbn.tc.schema.avro.cdm{cdm}.Event']['timestampNanos']
            timestamp = x['@timestamp']
        except:
            timestamp = ''
            timestampnano = ''

        if action in edge_types:
            info_data = {
                'actorID': actor,
                'objectID': obj,
                'action': action,
                'timestampNanos': timestampnano,
                'timestamp': timestamp,
                'exec': cmd,
                'path': path,
                'hostid': hostid
            }
            info_buffer.append(info_data)
    
    if info_buffer:
        stitch(info_buffer)

def main():
    parser = argparse.ArgumentParser(description="Process JSON.tar.gz CDM files and generate JSON output.")
    parser.add_argument('--directory', required=True, help="Directory containing the .json.tar.gz files.")
    parser.add_argument('--title', required=True, help="Title name (e.g., E3 or E5).")
    parser.add_argument('--scene', required=True, help="Scene name (e.g., theia, cadets, etc.).")
    parser.add_argument('--output_dir', required=True, help="Directory where the final JSON results will be stored.")

    args = parser.parse_args()

    global directory, title, scene, cdm, output_dir  # <-- output_dir global
    directory = args.directory
    title = args.title
    scene = args.scene
    output_dir = args.output_dir  
    os.makedirs(output_dir, exist_ok=True) 

    cdm = "18" if title == 'E3' else "20"

    try:
        extract_json_from_tar_gz(directory)
    except ValueError as ve:
        print(ve)

    prepare_id_files(directory)
    query_json(directory)

if __name__ == '__main__':
    main()
