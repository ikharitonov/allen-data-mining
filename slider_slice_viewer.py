import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from matplotlib import colors
from mpl_toolkits.axes_grid1 import make_axes_locatable

filename = 'VISpm_VISam_MD.npy'
# filename = 'VISpm_RSPagl_MD.npy'
# filename = 'VISam_RSPagl_MD.npy'
A = np.load(filename)

annotation_filename = 'annotation.npy'
annot = np.load(annotation_filename)

fig,ax = plt.subplots(2,1,figsize=(10,10))

# cmap = 'hot'
cmap = 'seismic'
divnorm = colors.TwoSlopeNorm(vmin=A.min(), vcenter=0.0, vmax=A.max())
annot_cmap = 'gray'

idx0 = 0
# plot1 = ax[0].imshow(A[idx0,:,:], cmap=cmap, vmin=A.min(), vmax=A.max())
plot1 = ax[0].imshow(A[idx0,:,:], cmap=cmap, norm=divnorm)
ax[0].set_title(filename)
plot2 = ax[1].imshow(annot[idx0,:,:], cmap=annot_cmap, aspect='equal', vmin=0, vmax=2000)
ax[1].set_title(annotation_filename)

axidx = plt.axes([0.1, 0.0, 0.65, 0.03])
slidx = Slider(axidx, 'index', 0, A.shape[0], valinit=idx0, valfmt='%d')

def update(val):
    idx = slidx.val
    plot1.set_data(A[int(idx),:,:])
    plot2.set_data(annot[int(idx),:,:])
    fig.canvas.draw_idle()
slidx.on_changed(update)

divider = make_axes_locatable(ax[0])
cax = divider.append_axes("right", size="5%", pad=0.05)

plt.colorbar(plot1, cax=cax)

plt.show()