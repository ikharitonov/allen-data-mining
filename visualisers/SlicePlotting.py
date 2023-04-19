from allensdk.core.mouse_connectivity_cache import MouseConnectivityCache
import numpy as np
import os
import matplotlib
import matplotlib.pyplot as plt
from pathlib import Path
import pickle
import time

class Plotter:
    def __init__(self, annotation_path, data_path):
        self.data_path = data_path

        mcc = MouseConnectivityCache(resolution=10)
        print('Allen Mouse Connectivity library loaded.')

        self.annot_vol, _ = mcc.get_annotation_volume(annotation_path)
        print(f'Annotation volume with shape {self.annot_vol.shape} loaded.')

        # Reading acronyms corresponding to area ids
        with open(data_path / 'areas_acronyms.pkl', 'rb') as f: self.areas_acronyms_dict = pickle.load(f)

    def load_parameters(self,parameters):
        print('Parameters loaded:')
        print(parameters)
        self.parameters = parameters

        # Reading the file with centroids data
        foldername = f'centroids_{parameters["projection_metric"]}_hem_id_{parameters["hemisphere_id"]}_inj_vol_thresh_{parameters["injection_volume_threshold"]}_target_vol_thresh_{parameters["projection_volume_threshold"]}_{parameters["area"]}'
        filename = f'{parameters["projection_type"]}_centroids_dict_hem_{parameters["hemisphere_id"]}_inj_vol_thresh_{parameters["injection_volume_threshold"]}_target_vol_thresh_{parameters["projection_volume_threshold"]}_{parameters["area"]}.pkl'
        load_path = self.data_path / foldername / filename
        with open(load_path, 'rb') as f: self.centroids_dict = pickle.load(f)
        print(f'Centroids data loaded from {filename}')

        # Extracting coordinates and values of projection metric
        vals = self.centroids_dict.values()
        self.area_ids = list(self.centroids_dict.keys())
        self.xyz = [area[:3] for area in vals]
        self.proj_metric = [area[3] for area in vals]

    def plot(self):
        # https://stackoverflow.com/questions/7908636/how-to-add-hovering-annotations-to-a-plot

        def update_annot(ind,event):
            annot.xy = (x[ind], y[ind])
            text = f'{self.area_ids[ind]}: {self.areas_acronyms_dict[self.area_ids[ind]]}'
            annot.set_text(text)
            annot.get_bbox_patch().set_alpha(0.6)

        def on_pick(event):
            ind = int(event.ind)
            print(f"Index of picked point: {ind}")
            vis = annot.get_visible()
            update_annot(ind,event)
            annot.set_visible(True)
            fig.canvas.draw_idle()
        #     time.sleep(5)
        #     annot.set_visible(False)
        #     fig.canvas.draw_idle()

        # Defining data normalisation and colormap
        norm = matplotlib.colors.Normalize(vmin=min(self.proj_metric), vmax=max(self.proj_metric))
        cmap = matplotlib.cm.get_cmap('viridis')

        fig,ax = plt.subplots(figsize=(10,10))

        plt.title(f'{self.parameters["projection_type"]} {self.parameters["area"]} hem={self.parameters["hemisphere_id"]} inj_vol_thresh={self.parameters["injection_volume_threshold"]} target_vol_thresh={self.parameters["projection_volume_threshold"]} {self.parameters["projection_metric"]}')

        plt.imshow(self.annot_vol[:,400,:], cmap='gray', aspect='equal', vmin=0, vmax=2000)

        norm = matplotlib.colors.Normalize(vmin=min(self.proj_metric), vmax=max(self.proj_metric))

        x = np.array(self.xyz)[:,2] / 10
        y = np.array(self.xyz)[:,0] / 10
        z = norm(self.proj_metric)

        sc = plt.scatter(x, y, c=z, s=50, cmap=cmap, picker=True)

        plt.colorbar()

        annot = ax.annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w"),
                            arrowprops=dict(arrowstyle="->"))
        annot.set_visible(False)

        fig.canvas.mpl_connect('pick_event', on_pick)

        plt.tight_layout()
        plt.show()