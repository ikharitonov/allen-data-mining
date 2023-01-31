import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import scipy.stats as stats

def breakup_df(df,b,metric):
    # break up dataframe into two, based on value b of column named 'metric'
    df1 = df[df[metric] < b]
    df2 = df[df[metric] >= b]
    return df1, df2

def data_from_df(df,metric_1,metric_2):
    return np.array(df[metric_1]).reshape((-1, 1)), np.array(df[metric_2])
def data_to_df(arr_1,arr_2,metric_1,metric_2):
    return pd.DataFrame({metric_1:arr_1, metric_2:arr_2})

def lin_reg(x,y):
    # perform linear regression and find line of best fit

    model = LinearRegression(fit_intercept=True)
    model.fit(x, y)

    r_sq = model.score(x, y)
    print('coefficient of determination:', r_sq)

    print('intercept:', model.intercept_)

    print('slope:', model.coef_) 

    # xfit = np.linspace(x.min(), x.max(), 1000)
    yfit = model.predict(x)

    return x,yfit

def rss_fit(mod_y, data_y):
    return np.sum(np.square(mod_y - data_y))

def chow_test(data_y1, data_y2, data_c, bestfit1, bestfit2, bestfit_c):
    # perform Chow test on segments data_y1 & bestfit1 and data_y2 & bestfit2 trying to fit the data
    # https://medium.com/@remycanario17/the-chow-test-dealing-with-heterogeneity-in-python-1b9057f0f07a

    N1 = len(data_y1)
    N2 = len(data_y2)
    k = 2
    rss_1 = rss_fit(bestfit1, data_y1)
    rss_2 = rss_fit(bestfit2, data_y2)
    rss_c = rss_fit(bestfit_c, data_c)
    chow_stat = ((rss_c - (rss_1 + rss_2))/k)/((rss_1 + rss_2)/(N1+N2-2*k))
    pvalue = stats.f.sf(chow_stat, k, N1+N2-2*k)
    return chow_stat, pvalue

def fit_model_for_breakpoint(df, break_p):
    # break up data into two segments at a given breakpoint and perform linear regression for the two segments and complete data

    df_below, df_above = breakup_df(df,break_p,'density')
    x,y = data_from_df(df_below,'density','intensity')
    below_x,below_best_fit = lin_reg(x,y)
    x,y = data_from_df(df_above,'density','intensity')
    above_x,above_best_fit = lin_reg(x,y)
    x,y = data_from_df(df,'density','intensity')
    all_x,all_best_fit = lin_reg(x,y)

    return df_below['intensity'].to_numpy(), df_above['intensity'].to_numpy(), df['intensity'].to_numpy(), [below_x,below_best_fit], [above_x,above_best_fit], [all_x,all_best_fit]

def chow_test_for_breakpoint(df, break_p):
    # compute Chow test statistics given a dataset and a breakpoint

    below_array, above_array, all_array, below_best_fit,above_best_fit,all_best_fit = fit_model_for_breakpoint(df, break_p)
    chow_stat, chow_pval = chow_test(below_array, above_array, all_array, below_best_fit[1], above_best_fit[1], all_best_fit[1])

    return chow_stat, chow_pval

path = "/home/ikharitonov/Desktop/data/ish/postsynaptic_receptor_list/antisense/"

density = np.array(pd.read_excel(path+"expression_density_data.xlsx")['expression_density'])
intensity = np.array(pd.read_excel(path+"expression_intensity_data.xlsx")['expression_intensity'])

density = density[~np.isnan(density)]
intensity = intensity[~np.isnan(intensity)]
df = data_to_df(density,intensity,'density','intensity')


breakpoints = [0.003,0.004,0.005,0.006,0.007,0.008,0.009,0.010,0.011,0.012]
pvals = []

for b in breakpoints:
    _,pval = chow_test_for_breakpoint(df,b)
    pvals.append(pval)

plt.plot(breakpoints,pvals)
plt.xlabel('breakpoint')
plt.ylabel('p-value')
plt.show()

print('======================================================================')

_,_,_,below_fit,above_fit,_ = fit_model_for_breakpoint(df,0.006)
x,y = data_from_df(df,'density','intensity')

plt.scatter(x, y)
plt.plot(below_fit[0], below_fit[1], color='red')
plt.plot(above_fit[0], above_fit[1], color='orange')

plt.tight_layout()
plt.show()