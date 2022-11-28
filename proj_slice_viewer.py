import numpy as np
import matplotlib.pyplot as plt
from allensdk.core.mouse_connectivity_cache import MouseConnectivityCache

class IndexTracker(object):
    def __init__(self, ax, X):
        self.ax = ax
        ax.set_title('use scroll wheel to navigate images')

        self.X = X
        rows, cols, self.slices = X.shape
        self.ind = self.slices//2

        self.im = ax.imshow(self.X[:, :, self.ind], cmap='hot')
        self.update()

    def onscroll(self, event):
        print("%s %s" % (event.button, event.step))
        if event.button == 'up':
            self.ind = (self.ind + 1) % self.slices
        else:
            self.ind = (self.ind - 1) % self.slices
        self.update()

    def update(self):
        self.im.set_data(self.X[:, :, self.ind])
        ax.set_ylabel('slice %s' % self.ind)
        self.im.axes.figure.canvas.draw()

# mcc = MouseConnectivityCache()
# experiment_id = 294481346
# pd, pd_info = mcc.get_projection_density(experiment_id)

# array_to_visualise = pd
# array_to_visualise = np.load('diff_VISpm_VISam.npy')
# array_to_visualise = np.load('annotation.npy')
array_to_visualise = np.load('VISpm_VISam_MD.npy')

fig, ax = plt.subplots(1, 1)

tracker = IndexTracker(ax, np.transpose(array_to_visualise, (1, 2, 0)))

fig.canvas.mpl_connect('scroll_event', tracker.onscroll)
plt.show()