#%%
from sklearn.cluster import KMeans
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import geopandas as gpd
import os

#%%
def spatial_plot(df, shp, dict_scatter, title, fig_name):

    os.makedirs("Figuras", exist_ok = True)

    #Para Coletar apenas as legendas das clusteres utilizadas
    dict_plot = [] 
    for j in dict_scatter:
        if j["cluster"] in np.arange(df["cluster"].min(), df["cluster"].max()+1):
            dict_plot.append(j)
    
    fig, ax = plt.subplots(figsize = (6,6), dpi = 600)
    for i in dict_plot:
        ax.scatter(
            x = df["lon"].loc[df["cluster"] == i["cluster"]], 
            y = df["lat"].loc[df["cluster"] == i["cluster"]],
            c = i["color"], label = i["label"], s = 10, zorder = 3)

    shp.plot(
        ax = ax,  color = "None", linestyle = "solid",
        alpha = 1, linewidth=0.5, zorder = 2)

    ax.grid(linestyle = "--", alpha = 0.5, zorder = 1)

    ax.legend(
        loc = "lower right", markerfirst = True, handletextpad = 0.1,
        borderaxespad = 0.3, fontsize = 10,  markerscale = 1.5)

    ax.set_ylabel("Latitude")
    ax.set_xlabel("Longitude")
    ax.set_title(title, loc = "left")

    fig.savefig(
        "Figuras/{}.png".format(fig_name),
        dpi = 600, bbox_inches = "tight", facecolor = "w")
    
    plt.close()

def n_cluster(df, max_cluster, title, fig_name):
    inertia_list = []
    for i in range(1, max_cluster+1):
        km = KMeans(n_clusters = i, random_state = 0).fit(df)
        inertia_list.append([i, km.inertia_])

    inertia_list = np.array(inertia_list)
    print(inertia_list[0,1])
    diff = np.abs(np.diff(inertia_list[:,1], axis = 0)/inertia_list[0:-1,1])
    fig, ax = plt.subplots(dpi = 600)
    ax.bar(x = inertia_list[1::,0], height = diff, zorder = 1, tick_label = range(2, max_cluster+1))
    # ax.bar(x = inertia_list[:,0], height = inertia_list[:,1], zorder = 1, tick_label = range(1, max_cluster+1))
    # ax.plot(inertia_list[:,0], inertia_list[:,1])
    # ax.set_xticks(range(1,max_cluster+1))
    # ax.plot(inertia_list[1::,0], diff)
    # ax.set_xticks(range(2,max_cluster+1))
    ax.set_xlabel("n° clusters")
    ax.set_ylabel("SSE Variation")
    ax.set_title(title, loc = "left")
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1))
    print(diff)
    fig.savefig(
        "Figuras/{}.png".format(fig_name),
        dpi = 600, bbox_inches = "tight", facecolor = "w")
    return inertia_list
#%%
data_spi = pd.read_csv("Dados/df_spi.csv", sep = ";")
band1 = pd.read_csv("Dados/Banda1.csv", sep = ";", header = None, index_col = 0).T
band2 = pd.read_csv("Dados/Banda2.csv", sep = ";", header = None, index_col = 0).T
band3 = pd.read_csv("Dados/Banda3.csv", sep = ";", header = None, index_col = 0).T
shp = gpd.read_file("shapes/BR_Macro_Regioes.shp")
# if (data_spi.iloc[0:2,:].equals(band1.iloc[0:2,:])) & (band1.iloc[0:2,:].equals(band2.iloc[0:2,:])) & (band2.iloc[0:2,:].equals(band3.iloc[0:2,:])) :
#     coords = data_spi.iloc[0:2,:]
# else:
#     print("Coordenadas divergem entre os dataframes")
coords = data_spi.iloc[:,0:2]
#%%
spi_df = data_spi.iloc[:,2:]
b1_df = band1.iloc[:,2:]
b2_df = band2.iloc[:,2:]
b3_df = band3.iloc[:,2:]

spi_df.columns, b1_df.columns, b2_df.columns, b3_df.columns = (pd.to_datetime(spi_df.columns),
                                                            pd.to_datetime(b1_df.columns),
                                                            pd.to_datetime(b2_df.columns),
                                                            pd.to_datetime(b3_df.columns))
spi_df = spi_df.loc[:, spi_df.columns.month == 12]
#%%

#Definindo número de Cluster
n_cluster(spi_df, 10, "a) SPI-12", "SPI-12")
n_cluster(b1_df, 10, "b) High Frequency Band (2 to 8 years)", "Banda_1_SSE")
n_cluster(b2_df, 10, "c) Medium Frequency Band (9 to 40 years)", "Banda_2_SSE")
n_cluster(b3_df, 10, "d) Low Frequency Band (40+ years)", "Banda_3_SSE")

#%%
kmeans_spi = KMeans(n_clusters = 7, random_state = 0)
kmeans_spi.fit(spi_df)
center_spi = pd.DataFrame(kmeans_spi.cluster_centers_).T
center_spi.index = spi_df.columns
cluster_spi = pd.DataFrame({
    "lon": coords.lon, "lat": coords.lat, "cluster": kmeans_spi.labels_
})
center_spi.to_csv("Dados/spi_Center.csv",
            sep = ";", header = True, index = True)

#%%
kmeans_b1 = KMeans(n_clusters = 6, random_state = 0)
kmeans_b1.fit(b1_df)
center_b1 = pd.DataFrame(kmeans_b1.cluster_centers_).T
center_b1.index = b1_df.columns
cluster_b1 = pd.DataFrame({
    "lon": coords.lon, "lat": coords.lat, "cluster": kmeans_b1.labels_
})
center_b1.to_csv("Dados/band1_Center.csv",
            sep = ";", header = True, index = True)

#%%
kmeans_b2 = KMeans(n_clusters = 3, random_state = 0)
kmeans_b2.fit(b2_df)
center_b2 = pd.DataFrame(kmeans_b2.cluster_centers_).T
center_b2.index = b2_df.columns
cluster_b2 = pd.DataFrame({
    "lon": coords.lon, "lat": coords.lat, "cluster": kmeans_b2.labels_
})
center_b2.to_csv("Dados/band2_Center.csv",
            sep = ";", header = True, index = True)
#%%
kmeans_b3 = KMeans(n_clusters = 3, random_state = 0)
kmeans_b3.fit(b3_df)
center_b3 = pd.DataFrame(kmeans_b3.cluster_centers_).T
center_b3.index = b3_df.columns
cluster_b3 = pd.DataFrame({
    "lon": coords.lon, "lat": coords.lat, "cluster": kmeans_b3.labels_
})
center_b3.to_csv("Dados/band3_Center.csv",
            sep = ";", header = True, index = True)

#%%
dict_scatter = [
    {"cluster": 0, "color": "green", "label": "Cluster 1"},
    {"cluster": 1, "color": "red", "label": "Cluster 2"},
    {"cluster": 2, "color": "blue", "label": "Cluster 3"},
    {"cluster": 3, "color": "darkorange", "label": "Cluster 4"},
    {"cluster": 4, "color": "black", "label": "Cluster 5"},
    {"cluster": 5, "color": "darkmagenta", "label": "Cluster 6"},
    {"cluster": 6, "color": "darkcyan", "label": "Cluster 7"},
    {"cluster": 7, "color": "brown", "label": "Cluster 8"}
]

#%%
spatial_plot(cluster_spi, shp, dict_scatter, "a) SPI12", "SPI12")
spatial_plot(cluster_b1, shp, dict_scatter, "b) High Frequency Band (2 to 8 years)", "Banda_1")
spatial_plot(cluster_b2, shp, dict_scatter, "c) Medium Frequency Band (9 to 40 years)", "Banda_2")
spatial_plot(cluster_b3, shp, dict_scatter, "d) Low Frequency Band (40+ years)", "Banda_3")

#%%
fig, ax = plt.subplots(dpi = 600)
for i in dict_scatter:
    ax.scatter(x = cluster_spi.lon.loc[cluster_spi.cluster == i["cluster"]],
               y = cluster_spi.lat.loc[cluster_spi.cluster == i["cluster"]],
               c = i["color"], marker = "o", s = 10, label = i["label"])
ax.legend(loc = "lower right", markerfirst = True, handletextpad = 0.1,
        borderaxespad = 0.3, fontsize = 10,  markerscale = 1.5)

#
# %%
