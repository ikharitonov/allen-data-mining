import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

receptors = {"Drd":["Drd1","Drd2","Drd3","Drd4","Drd5"],"Htr":["Htr1a","Htr1b","Htr1d","Htr1e","Htr1f","Htr2a","Htr2b","Htr2c","Htr4","Htr5a","Htr5bp","Htr6","Htr7","Htr3a","Htr3b","Htr3c","Htr3d","Htr3e"],"Chrn":["Chrna1","Chrna2","Chrna3","Chrna4","Chrna5","Chrna6","Chrna7","Chrna8","Chrna9","Chrna10","Chrnb1","Chrnb2","Chrnb3","Chrnb4","Chrnd","Chrne","Chrng","Chrm1","Chrm2","Chrm3","Chrm4","Ch4m5"],"Cnr":["Cnr1","Cnr2"],"Opr":["Oprd1","Oprk1","Oprl1","Oprm1"],"Hrh":["Hrh1","Hrh2","Hrh3","Hrh4"],"P2r":["P2ry1","P2ry2","P2ry4","P2ry6","P2ry11","P2ry12","P2ry13","P2ry14","P2rx1","P2rx2","P2rx3","P2rx4","P2rx5","P2rx6","P2rx7"],"Grm":["Grm1","Grm2","Grm3","Grm4","Grm5","Grm6","Grm7","Grm8"],"Gabbr":["Gabbr1","Gabbr2"],"Endocannabinoid":["Faah","Mgll","Nat2","Napepld","Amt"],"Adr":["Adra1a","Adra2a","Adrb1","Adrb3","Adra1b","Adrad","Adra2b","Adra2c","Adrab2"]}
df = pd.read_csv('/home/ikharitonov/Desktop/Allen_10X_Data/trimmed_means.csv')

# get the names of clusters
sheet_names = ['L2.3_IT','L4_IT','L5_IT','L6_IT','L5_PT']
clusters = {}
for name in sheet_names:
    sheet_df = pd.read_excel('/home/ikharitonov/Desktop/Allen_10X_Data/Allen10x_5HT.xlsx',sheet_name=name)
    # Removing columns which had identical names in excel (here they are added .1 in the end)
    sheet_df = sheet_df.loc[:,sheet_df.columns.str.find('.') < 0]
    column_list = list(sheet_df.columns)
    column_list.remove('AVG')
    column_list.remove('SD')
    column_list.remove('Prevalence')
    clusters[name] = column_list

# pull each of the clusters for each family of receptors
# {receptor_family_1: {L5_PT: dataframe_1, L5_IT: dataframe_2, ...}, receptor_family_2: {...}}
data = {}
for family, receptor_list in receptors.items():
    cluster_data = {}
    # selecting data for clusters defined above and a family of receptors from dataframe
    for cluster_name, cluster in clusters.items():
        temp_df = df[df['feature'].isin(receptor_list)][df.columns.intersection(cluster)]
        # Sorting the dataframe by feature - receptor list values
        temp_df.sort_values(by="feature", key=lambda column: column.map(lambda e: receptor_list.index(e)), inplace=True)
        # compute mean, sd and prevalence for single receptors
        temp_df['MEAN'] = temp_df[cluster[1:]].mean(axis=1)
        temp_df['STD'] = temp_df[cluster[1:]].std(axis=1)
        temp_df['Prevalence(%)'] = temp_df[cluster[1:]].gt(0,axis = 0).sum(axis = 1) / len(cluster[1:]) * 100
        cluster_data[cluster_name] = temp_df
    data[family] = cluster_data

print(data['Htr']['L5_IT'])

# save results in separate excels for each family of receptors
for family, clusters in data.items():
    with pd.ExcelWriter(family+'_data.xlsx') as writer:
        for sheet, df_data in clusters.items(): df_data.to_excel(writer, sheet_name=sheet)

# plot
for family, clusters in data.items():
    fig, axes = plt.subplots(2, 5,figsize=(24,4),sharex=True)
    for sheet, df_data in clusters.items():
        i = list(clusters.keys()).index(sheet)
        axes[1][i].bar(df_data['feature'],df_data['Prevalence(%)'], color='black')
        axes[1][i].yaxis.tick_right()
        axes[1][i].spines['top'].set_visible(False)
        axes[1][i].spines['left'].set_visible(False)
        axes[1][i].set_ylim([-1,100])
        axes[1][i].set_ylabel('prevalence (%)')
        axes[1][i].yaxis.set_label_position("right")
        axes[1][i].set_xticklabels(df_data['feature'], rotation=-80, ha='center')

        axes[0][i].set_title(sheet)
        axes[0][i].errorbar(df_data['feature'],df_data['MEAN'],yerr=df_data['STD'], fmt="o", c='black')
        axes[0][i].get_xaxis().set_visible(False)
        axes[0][i].spines['top'].set_visible(False)
        axes[0][i].spines['right'].set_visible(False)
        axes[0][i].spines['bottom'].set_visible(False)
        axes[0][i].set_ylim([-1,12])
        axes[0][i].set_ylabel('avg. expr.(a.u.)')
    plt.tight_layout()
    plt.savefig(family+'.png')
    plt.show()