import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

path = "/home/ikharitonov/Desktop/data/ish/postsynaptic_receptor_list/antisense/expression_density_data.xlsx"

df = pd.read_excel(path)

T = 0.006

# plot receptor vs expression density
# plot horizontal T value
# for each receptor
# for every experiment in it plot the its density
# two ways of plotting:
# 1) select specific area for all data and only plot density values for it
# 2) for each receptor and each experiment plot densities in all areas, color each area distinctively
# mark the "weakly expression" receptors, according to chow test / k-means plot


plt.figure(figsize=(30,5))

plt.title('data consistency - all areas')

plt.hlines(T,-100,100,linestyles='dashed',colors='red')
select_df = df[df['structure']=='VISam5']
plt.scatter(select_df['receptor'],select_df['expression_density'],s=10,c='green')
select_df = df[df['structure']=='VISpm5']
plt.scatter(select_df['receptor'],select_df['expression_density'],s=10,c='blue')
select_df = df[df['structure']=='RSPagl5']
plt.scatter(select_df['receptor'],select_df['expression_density'],s=10,c='orange')
select_df = df[df['structure']=='VISp5']
plt.scatter(select_df['receptor'],select_df['expression_density'],s=10,c='purple')

plt.legend(['Chow test threshold','VISam5','VISpm5','RSPagl5','VISp5'])

plt.xticks(fontsize=5)

plt.tight_layout()
plt.show()