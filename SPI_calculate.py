#%%
import pandas as pd 
import scipy.stats as sc
import numpy as np

def spi_calculate (var, window, distr = "gamma"):

    x = var.rolling(window = window).sum()


    x = np.array(x)
    x = x[~np.isnan(x)]

    if distr == "gamma":
        q = len(np.where(x == 0)[0])/(len(x))
        x_nozero = x[x  > 0]
        params_fit = sc.gamma.fit(x_nozero, floc = 0)
        prob_acc = q + (1-q)*sc.gamma.cdf(x, *params_fit)

    if distr == "pearson3":
        params_fit = sc.pearson3.fit(x)
        prob_acc = sc.pearson3.cdf(x, *params_fit)

    if distr == "logistic":
        params_fit = sc.logistic.fit(x)
        prob_acc = sc.logistic.cdf(x, *params_fit)

    spi = sc.norm.ppf(prob_acc, loc = 0, scale = 1)

    return spi
   
#%%
data = pd.read_csv("Dados/Brasil_WGS84_Country_precip_1951_2020.csv", sep  = ";")

scale_spi = 12
list_spi = []
for i in range(len(data)):
    spi = spi_calculate(data.iloc[i,2:].T, window = 12, distr = "gamma")
    list_spi.append([data.iloc[i,0], data.iloc[i,1]])
    list_spi[i].extend(list(spi))

cols = ["lon", "lat"]
cols.extend(list(data.columns[2 + (scale_spi-1):]))

df = pd.DataFrame(list_spi, columns = cols)

df.to_csv("Dados/df_spi.csv", sep = ";", index = None, header = True)
# %%
