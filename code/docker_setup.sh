#!/bin/bash

# Check for correct number of arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <port_number> <working_dir>"
    exit 1
fi

# Extract arguments
port_number=$1
working_dir=$2

# Check if the specified directory exists, create if it doesn't
if [ ! -d "$working_dir" ]; then
    echo "Directory $working_dir does not exist. Creating now..."
    mkdir -p "$working_dir"
    if [ $? -ne 0 ]; then
        echo "Failed to create directory $working_dir. Exiting."
        exit 1
    fi
fi

# Run Docker command
docker run -it -p ${port_number}:8888 --user root -e GRANT_SUDO=yes --group-add users \
-v /bigdisk/Trustwatch:/home/jovyan/Trustwatch:ro \
-v ${working_dir}:/home/jovyan/${working_dir} \
jupyter/base-notebook start.sh jupyter notebook --NotebookApp.token=''
