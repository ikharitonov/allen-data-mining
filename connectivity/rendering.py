from brainrender import Scene
from brainrender.actors import Point, Points
import matplotlib
import pickle
import numpy as np
from pathlib import Path

# Atlas dimensions
# 13200 µm x 8000 µm x 11400 µm

# Reading the file with centroids data
path = Path.home() / 'Desktop' / 'data' / 'connectivity'
filename = path / 'ipsilateral_centroids_dict_hem_1_VISam.pkl'
with open(filename, 'rb') as f: ipsilateral_centroids_dict = pickle.load(f)

# Extracting coordinates and values of projection metric
vals = ipsilateral_centroids_dict.values()
area_ids = list(ipsilateral_centroids_dict.keys())
xyz = [area[:3] for area in vals]
proj_metric = [area[3] for area in vals]

# Defining data normalisation
norm = matplotlib.colors.Normalize(vmin=min(proj_metric), vmax=max(proj_metric))

# Create a brainrender scene
scene = Scene(title=filename.name)

# Adding brain regions to the plot
scene.add_brain_region("VISam", "VISpm", "RSPagl", alpha=0.2, color="green")
scene.add_brain_region("VISp", alpha=0.2, color="red")

# Adding color hex codes into a list according to colormap
cmap_name = "hot"
cmap = matplotlib.cm.get_cmap(cmap_name)
hex_colors = []
normalised_proj_matrix_vals = []
for i in range(len(xyz)):
    # Compute color from the value of each point
    hex_colors.append(matplotlib.colors.rgb2hex(cmap(norm(proj_metric[i]))))
    # Save values into list
    v = norm(proj_metric[i])
    normalised_proj_matrix_vals.append(v)
    # Add transparent points (for plotting area id captions)
    scene.add(Point(xyz[i], name="invisible areas", alpha=0,radius=1))
    # Plotting the caption
    actors = scene.get_actors()
    actors[-1].caption(str(area_ids[i]),size=(0.05, 0.01))
# Plot all points as a 'Points' object
scene.add(Points(np.array(xyz),name='Areas',colors=hex_colors,radius=75))

# Plot the color scale
actors = scene.get_actors()
# addScalarBar(title='', pos=(0.8, 0.05), titleYOffset=15, titleFontSize=12, size=(None, None), nlabels=None, c=None, horizontal=False, useAlpha=True) method of vedo.mesh.Mesh instance
actors[-1].cmap(cmap,).addScalarBar(pos=(0.1,0.1),size=(400,200), horizontal=True)

# Render!
scene.render()