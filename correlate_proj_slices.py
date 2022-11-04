import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import correlate2d
from tqdm import tqdm
from allensdk.core.mouse_connectivity_cache import MouseConnectivityCache

mcc = MouseConnectivityCache()

experiment_id1 = 294481346 # VISpm
pd1, pd_info1 = mcc.get_projection_density(experiment_id1)
print("Experiment 1:",experiment_id1,"in VISpm.")

experiment_id2 = 159753308 # VISam
pd2, pd_info2 = mcc.get_projection_density(experiment_id2)
print("Experiment 2:",experiment_id2,"in VISam.")

corr = np.zeros_like(pd1)

for slice in tqdm(range(corr.shape[0]), "Correlating "+str(corr.shape[0])+" slices"):
    corr[slice,:,:] += correlate2d(pd1[slice,:,:],pd2[slice,:,:])

np.save("proj_density_corr_exp_"+str(experiment_id1)+"_exp_"+str(experiment_id1)+".npy",corr)