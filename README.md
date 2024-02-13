# AOMIC-ID1000
Here I will post the 1) Data downloader and the 2) Data preprocessor for the AOMIC-ID1000 dataset, available at: https://openneuro.org/datasets/ds003097/versions/1.2.1.

### To read the Output.npy use this code: 

To open file:


import numpy as np
outputfile = 'Output.npy'
loadarray = []

    #open the output file and check the data
    with open(outputfile,'rb') as f:
        while (True):
            try:
                file = np.load(f)[0]
                adjacency_matrix = np.load(f)


                loadarray.append([file,adjacency_matrix])

                print(f"{file} - LOADED-----------------------")
                print (adjacency_matrix)
                print(f"-------------------------------------------------------------------------")
                print("")

            except:
                break

As graphs:

!pip install torch_geometric
import torch
from torch_geometric.data import Data
import numpy as np

loadarray = []
with open('Output.npy', 'rb') as f:
    while True:
        try:
            file_name = np.load(f)[0]
            adjacency_matrix = np.load(f)

            edge_index = torch.tensor(np.nonzero(adjacency_matrix), dtype=torch.long)

            graph = Data(edge_index=edge_index)
            loadarray.append([file_name, graph])

            print(f"{file_name} - LOADED-----------------------")
            print(adjacency_matrix)
            print(f"-------------------------------------------------------------------------")
            print("")

        except Exception as e:
            break

for _, graph in loadarray:
    num_nodes = graph.num_nodes
    graph.x = torch.eye(num_nodes)  # one-hot encoded

from torch_geometric.data import DataLoader

graphs = [item[1] for item in loadarray]  # Extract graph objects
loader = DataLoader(graphs, batch_size=32)
