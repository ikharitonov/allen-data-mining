import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

d = {"Drd":["Drd1","Drd2","Drd3","Drd4","Drd5"],"Htr":["Htr1a","Htr1b","Htr1d","Htr1e","Htr1f","Htr2a","Htr2b","Htr2c","Htr4","Htr5a","Htr5bp","Htr6","Htr7","Htr3a","Htr3b","Htr3c","Htr3d","Htr3e"],"Chrn":["Chrna1","Chrna2","Chrna3","Chrna4","Chrna5","Chrna6","Chrna7","Chrna8","Chrna9","Chrna10","Chrnb1","Chrnb2","Chrnb3","Chrnb4","Chrnd","Chrne","Chrng","Chrm1","Chrm2","Chrm3","Chrm4","Ch4m5"],"Cnr":["Cnr1","Cnr2"],"Opr":["Oprd1","Oprk1","Oprl1","Oprm1"],"Hrh":["Hrh1","Hrh2","Hrh3","Hrh4"],"P2r":["P2ry1","P2ry2","P2ry4","P2ry6","P2ry11","P2ry12","P2ry13","P2ry14","P2rx1","P2rx2","P2rx3","P2rx4","P2rx5","P2rx6","P2rx7"],"Grm":["Grm1","Grm2","Grm3","Grm4","Grm5","Grm6","Grm7","Grm8"],"Gabbr":["Gabbr1","Gabbr2"],"Endocannabinoid":["Faah","Mgll","Nat2","Napepld","Amt"],"Adr":["Adra1a","Adra2a","Adrb1","Adrb3","Adra1b","Adrad","Adra2b","Adra2c","Adrab2"]}

variable = 'intensity'
path = '/home/ikharitonov/Desktop/data/ish/postsynaptic_receptor_list/antisense/'
df = pd.read_excel(path+'expression_'+variable+'_data.xlsx')
values = {}
save_path = '/home/ikharitonov/Desktop/data/ish/postsynaptic_receptor_list_histograms/'

for family,receptors in d.items():
    values[family] = np.array(df[df['receptor'].isin(receptors)]['expression_'+variable])

i = 1

plt.figure(figsize=(20,12))
for family,array in values.items():
    np.save(save_path+variable+'/'+family+'.npy',array)
    plt.subplot(3,4,i)
    plt.hist(array,bins=50)
    plt.xlabel(variable)
    plt.ylabel('frequency')
    plt.xlim([70,200])
    # plt.ylim([0,70])
    plt.gca().set_title(family,fontsize=10)
    i += 1
plt.tight_layout()
plt.savefig(save_path+variable+'.png')