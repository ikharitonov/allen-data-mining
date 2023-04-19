import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def NormalizeData(data):
    return (data - np.min(data)) / (np.max(data) - np.min(data))

def get_arr(path):
    families = os.listdir(path)

    grouped_arr = np.load(path+families[0])
    for f in families[1:]: grouped_arr = np.concatenate((grouped_arr, np.load(path+f)), axis=0)

    print(grouped_arr.shape)

    grouped_arr = grouped_arr[~np.isnan(grouped_arr)]
    grouped_arr = NormalizeData(grouped_arr)
    return grouped_arr

path = "/home/ikharitonov/Desktop/data/ish/postsynaptic_receptor_list_histograms/"

density = get_arr(path+"density/")
intensity = get_arr(path+"intensity/")
energy = get_arr(path+"energy/")

plt.figure(figsize=(12,4))
bins = 30

plt.subplot(1,3,1)
plt.gca().set_title('density',fontsize=10)
plt.hist(density,bins=bins)
plt.xlabel('density')
plt.ylabel('frequency')

plt.subplot(1,3,2)
plt.gca().set_title('intensity',fontsize=10)
plt.hist(intensity,bins=bins)
plt.xlabel('intensity')
plt.ylabel('frequency')

plt.subplot(1,3,3)
plt.gca().set_title('energy',fontsize=10)
plt.hist(energy,bins=bins)
plt.xlabel('energy')
plt.ylabel('frequency')

plt.tight_layout()
plt.show()