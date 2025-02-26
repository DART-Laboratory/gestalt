import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import torch
from torch_geometric.data import Data
import os
import torch.nn.functional as F
import json 
import warnings
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from torch_geometric.loader import NeighborLoader
import multiprocessing
from pprint import pprint
import gzip
from torch_geometric.nn import GCNConv, SAGEConv, GATConv
import torch.nn as nn
from gensim.models.callbacks import CallbackAny2Vec
from gensim.models import Word2Vec
from itertools import compress
from tqdm import tqdm
import time
from sklearn.utils import class_weight
from torch.nn import CrossEntropyLoss
from torch_geometric import utils
from collections import Counter
from elasticsearch import Elasticsearch, helpers
import re
import concurrent.futures

# Suppress warnings
warnings.filterwarnings('ignore')