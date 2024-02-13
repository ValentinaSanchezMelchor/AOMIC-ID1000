from ast import Pass
from math import e
from re import L
import nibabel as nib
import numpy as np
import sklearn
from nilearn import image, datasets
from nilearn.input_data import NiftiLabelsMasker
from nilearn.connectome import ConnectivityMeasure
from nilearn.plotting import plot_matrix, plot_epi
from sklearn.covariance import GraphicalLassoCV
import matplotlib.pylab as plt
import os

#settings
directorypath = "../DatasetDownloader/Unzipped/"
# directorypath = "Unzipped/"
outputfile = "Output.npy"
deleteoutatstart = 1

#statistics
starttime = 0
processed = 0
totalfiles = 0
started = 0

def main():
    
    if deleteoutatstart:
    ##@Valentina - Added one line here to check if it exists first before trying to delete.    
        if os.path.exists(outputfile):
            os.remove(outputfile)
        
    global starttime,processed,totalfiles,started    

    #get Atlas
    atlas = datasets.fetch_atlas_harvard_oxford("cort-maxprob-thr25-2mm")
    atlas_filename = atlas.maps
    labels = atlas.labels
    
    ##@Valentina - Commented out this because it was throwing an error
    # adjusted_labels = atlas.labels[1:] if len(atlas.labels) == len(estimator.covariance_) + 1 else atlas.labels
    # The first label correspond to the background
    print(f"The atlas contains {len(atlas.labels) - 1} non-overlapping regions")
    

    #iterate all the files
    directory = os.fsencode(directorypath)
    for dirpath,_,filenames in os.walk(directory):
        totalfiles = len(filenames)
        for f in filenames:
            try:
                
                path = os.fsdecode(os.path.join(dirpath, f))
                filenam = f
            
                # Preprocessing
                fmri_img = nib.load(path)

                # 1. Stracting time-series data

                # Initialize the masker object
                masker = NiftiLabelsMasker(labels_img=atlas_filename, standardize=True)

                # Apply the masker to fMRI data
                time_series = masker.fit_transform(fmri_img)

                # 2. Calculating correlation matrix
                estimator = GraphicalLassoCV()
                estimator.fit(time_series)
                precision_matrix = estimator.precision_
                adjacency_matrix = np.abs(precision_matrix) > 0.0
            
                processed+=1
            
                with open(outputfile,'ab') as f:
                
                    np.save(f, np.array([os.fsdecode(filenam)]))
                    np.save(f, adjacency_matrix)

            
                print(f"{processed}/{totalfiles} - Files Processed")
            except Exception as e:
                 print(f"{processed}/{totalfiles} - Failed to Process File.")


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


    #[[filename,adjacency_matrix,correlation_matrix],...]
    print (loadarray)

    # plot_matrix(correlation_matrix, figure=(10, 8), vmax=0.8, vmin=-0.8, title='Correlation matrix')
    # plot_matrix(adjacency_matrix, figure=(10, 8), vmax=0.8, vmin=-0.8, title='Adjacency matrix')


main()