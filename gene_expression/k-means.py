import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

# Put into repository
# - practice documenting
# - specify format of data input well, to be able to use it externally

path = "/home/ikharitonov/Desktop/data/ish/postsynaptic_receptor_list/antisense/"

density = np.array(pd.read_excel(path+"expression_density_data.xlsx")['expression_density'])
intensity = np.array(pd.read_excel(path+"expression_intensity_data.xlsx")['expression_intensity'])
density = density[~np.isnan(density)]
intensity = intensity[~np.isnan(intensity)]
density = density.reshape((-1, 1))
intensity = intensity.reshape((-1, 1))
X = np.concatenate((density,intensity),axis=1)
print(X.shape)

X = np.array(pd.read_excel(path+"expression_energy_data.xlsx")['expression_energy'])
X = X[~np.isnan(X)]
X = X.reshape((-1, 1))

kmeans = KMeans(n_clusters=2)
kmeans.fit(X)

print(kmeans.labels_)

plt.figure(figsize=(10,3))

plt.scatter(X[:,0],kmeans.labels_)
plt.xlabel('energy')
plt.ylabel('cluster')
plt.yticks([0,1])
plt.tight_layout()
plt.show()
# plt.scatter(X[:,0],X[:,1],c=kmeans.labels_)
# plt.xlabel('density')
# plt.ylabel('intensity')
# plt.show()