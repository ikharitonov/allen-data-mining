from allensdk.core.mouse_connectivity_cache import MouseConnectivityCache
import numpy as np
import os
import matplotlib
import matplotlib.pyplot as plt
from pathlib import Path
import pickle

mcc = MouseConnectivityCache(resolution=10)

# annot, annot_info = mcc.get_annotation_volume()
annot, annot_info = mcc.get_annotation_volume(Path.home()/'Desktop'/'repos'/'allen_data_mining'/'connectivity'/'mouse_connectivity'/'annotation'/'ccf_2017'/'annotation_10.nrrd')

# Parameters
area = 'VISam'
projection_metric = 'projection_energy'
hemisphere_id = 1
projection_type = 'ipsilateral'
injection_volume_threshold = 0.01
projection_volume_threshold = 0.1

# Reading the file with centroids data
path = Path.home() / 'Desktop' / 'data' / 'connectivity'
foldername = f'centroids_{projection_metric}_hem_id_{hemisphere_id}_inj_vol_thresh_{injection_volume_threshold}_target_vol_thresh_{projection_volume_threshold}_{area}'
filename = f'{projection_type}_centroids_dict_hem_{hemisphere_id}_inj_vol_thresh_{injection_volume_threshold}_target_vol_thresh_{projection_volume_threshold}_{area}.pkl'
load_path = path / foldername / filename
with open(load_path, 'rb') as f: centroids_dict = pickle.load(f)

# Extracting coordinates and values of projection metric
vals = centroids_dict.values()
area_ids = list(centroids_dict.keys())
xyz = [area[:3] for area in vals]
proj_metric = [area[3] for area in vals]

# Reading acronyms corresponding to area ids
with open(path / 'areas_acronyms.pkl', 'rb') as f: areas_acronyms_dict = pickle.load(f)

# Defining data normalisation and colormap
norm = matplotlib.colors.Normalize(vmin=min(proj_metric), vmax=max(proj_metric))

cmap = matplotlib.cm.get_cmap('viridis')

fig,ax = plt.subplots(figsize=(10,10))
# plt.figure()

names = np.array(list("ABCDEFGHIJKLMNO"))
c = np.random.randint(1,5,size=15)

plt.title(f'{projection_type} {area} hem={hemisphere_id} inj_vol_thresh={injection_volume_threshold} target_vol_thresh={projection_volume_threshold} {projection_metric}')

plt.imshow(annot[:,400,:], cmap='gray', aspect='equal', vmin=0, vmax=2000)

norm = matplotlib.colors.Normalize(vmin=min(proj_metric), vmax=max(proj_metric))

x = np.array(xyz)[:,2] / 10
y = np.array(xyz)[:,0] / 10
z = norm(proj_metric)

sc = plt.scatter(x, y, c=z, s=50, cmap=cmap)

plt.colorbar()

annot = ax.annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"))
annot.set_visible(False)

def update_annot(ind):
    
    pos = sc.get_offsets()[ind["ind"][0]]
    annot.xy = pos
    text = "{}, {}".format(" ".join(list(map(str,ind["ind"]))), 
                           " ".join([names[n] for n in ind["ind"]]))
    annot.set_text(text)
    annot.get_bbox_patch().set_facecolor(cmap(norm(c[ind["ind"][0]])))
    annot.get_bbox_patch().set_alpha(0.4)
    

def hover(event):
    vis = annot.get_visible()
    if event.inaxes == ax:
        cont, ind = sc.contains(event)
        if cont:
            update_annot(ind)
            annot.set_visible(True)
            fig.canvas.draw_idle()
        else:
            if vis:
                annot.set_visible(False)
                fig.canvas.draw_idle()

# fig.canvas.mpl_connect("motion_notify_event", hover)
fig.canvas.mpl_connect('button_press_event', hover)

plt.tight_layout()
plt.show()