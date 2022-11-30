import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from matplotlib import colors
from mpl_toolkits.axes_grid1 import make_axes_locatable
from allensdk.core.mouse_connectivity_cache import MouseConnectivityCache

mcc = MouseConnectivityCache()
structure_tree = mcc.get_structure_tree()

# filename = 'VISpm_VISam_MAD.npy'
filename = 'VISpm_RSPagl_MD.npy'
# filename = 'VISam_RSPagl_MD.npy'
A = np.load(filename)
absolute = True
if np.any(A<0): absolute = False

annotation_filename = 'annotation.npy'
annot = np.load(annotation_filename)

fig,ax = plt.subplots(2,1,figsize=(10,10))

if absolute: cmap = 'hot'
else:
    cmap = 'seismic'
    divnorm = colors.TwoSlopeNorm(vmin=A.min(), vcenter=0.0, vmax=A.max())
annot_cmap = 'gray'

idx0 = 0
if absolute: plot1 = ax[0].imshow(A[idx0,:,:], cmap=cmap, vmin=A.min(), vmax=A.max())
else: plot1 = ax[0].imshow(A[idx0,:,:], cmap=cmap, norm=divnorm)
ax[0].set_title(filename)
plot2 = ax[1].imshow(annot[idx0,:,:], cmap=annot_cmap, aspect='equal', vmin=0, vmax=2000)
ax[1].set_title(annotation_filename)

axidx = plt.axes([0.1, 0.0, 0.65, 0.03])
slidx = Slider(axidx, 'index', 0, A.shape[0], valinit=idx0, valfmt='%d')

def onclick(event):
    if event.inaxes == ax[0] or event.inaxes == ax[1]:
        x = event.xdata
        y = event.ydata
        structure_id = annot[int(slidx.val),int(y),int(x)]
        if structure_id:
            s = structure_tree.get_structures_by_id([structure_id])[0]
            name = s['name']
            acronym = s['acronym']
            ax[1].set_title(name+' ('+acronym+') / ID: '+str(structure_id))
        fig.canvas.draw_idle()

def update(val):
    idx = slidx.val
    plot1.set_data(A[int(idx),:,:])
    plot2.set_data(annot[int(idx),:,:])
    fig.canvas.draw_idle()
slidx.on_changed(update)

divider = make_axes_locatable(ax[0])
cax = divider.append_axes("right", size="5%", pad=0.05)

plt.colorbar(plot1, cax=cax)

fig.canvas.mpl_connect('button_press_event', onclick)

plt.show()