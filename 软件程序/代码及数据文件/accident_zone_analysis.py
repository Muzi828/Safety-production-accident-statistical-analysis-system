import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import time_series_analysis
import geopandas as gpd
from fuzzywuzzy import process
import warnings
warnings.filterwarnings('ignore')


def concat_data(data):
    df = pd.DataFrame()
    for name in data['省市'].unique():
        df_ = data[data["省市"] == name].resample('Y').sum()
        df_.columns = [name]
        df = pd.concat([df,df_.T])
    df = df.T.to_period(freq="Y")
    return df

def get_zone_data():
    data_load = time_series_analysis.excel_concat(r'数据\zone_data')
    data_load['省市'] = data_load['省市'].apply(lambda x: x.replace('内蒙','内蒙古').replace('内蒙古古','内蒙古'))
    date = pd.to_datetime(data_load["日期"])
    data_load.index = date
    data = data_load[data_load['省市'] != '全国'][['省市','事故/起']]
    data = concat_data(data).T
    data['sum'] = data.sum(axis=1)
    data['account'] = data['sum'] / data['sum'].sum()
    data['account'] = data['account'].map(lambda x: f'{round(x*100,2)}%')
    data = data.sort_values(by = 'account',ascending=False)
    return data

def plot_zone_data():
    data = get_zone_data()
    plt.figure(figsize=(20,14))
    sns.heatmap(data[data.columns[:-2]],
               annot = True,
                fmt = 'd',
                center = 63,
                cmap = 'hot_r'
               )
    plt.savefig(r'figure\zone_analysis.png',dpi =200)


#重大事故各省份死亡人数与经济增速之间的关联
def fuzzy_merge(df_1, df_2, key1, key2, threshold=90, limit=3):
    s = df_2[key2].tolist()
    m = df_1[key1].apply(lambda x: process.extract(x, s, limit=limit))
    df_1['matches'] = m
    m2 = df_1['matches'].apply(
        lambda x: [i[0] for i in x if i[1] >= threshold][0] if len([i[0] for i in x if i[1] >= threshold]) > 0 else '')
    df_1['matches'] = m2
    return df_1

def get_special_accident_data():
    df = pd.read_excel(r'数据\accident_type.xlsx')
    data_area = df.copy().drop('Unnamed: 6',axis =1)
    data_area.columns = ['time','province','city','accident','death','injury']
    china_spatial = gpd.GeoDataFrame.from_file('chinadata.json')
    df = fuzzy_merge(data_area, china_spatial, 'province', 'name', threshold=86)
    df_ = df.groupby(['matches']).agg({'death': 'sum'})
    return df_


def get_gdp_rate_data(df):
    rate_data_ls = []
    for column in df.columns:
        rate_data = (df[column] - df[column].shift(1)) / df[column]
        rate_data = (rate_data.dropna().sum() / len(rate_data)).round(4)
        rate_data_ls.append(rate_data)
    return rate_data_ls

def get_finial_data():
    province_data = pd.read_excel('数据\分省年度数据.xls')
    province_data = province_data.set_index('地区').T[15::-1]
    province_data_ = province_data.T
    province_data_['rate'] = get_gdp_rate_data(province_data)
    province_data_final = province_data_['rate'].reset_index()
    df_ = get_special_accident_data()
    china_spatial = gpd.GeoDataFrame.from_file('chinadata.json')
    data_ = pd.merge(df_, province_data_final, left_index=True, right_on='地区', how='left')
    data = pd.merge(china_spatial, data_, right_on='地区', left_on='name', how='left')
    del data['地区']
    # data.drop([24,31,33],inplace = True)
    data['death'] = data['death'].fillna(0).astype(int)
    return data

def plot_finial_data():
    data = get_finial_data()
    plt.figure(figsize=(20, 20))
    plt.title('"十一五"至"十三五"特大事故各省市分布', fontsize=20)

    # 绘制底图
    data.plot(ax=plt.subplot(1, 1, 1), scheme='FisherJenks',
              edgecolor='k', linewidth=0.5, color='gray', alpha=0.6)

    # 添加气泡图
    plt.scatter(data['centerlng'] + 0.2, data['centerlat'] + 0.2, c=data['rate'], cmap='Reds',
                s=data['death'], edgecolors='k', alpha=0.8)

    # 设置网格线
    plt.grid(True, alpha=0.5)

    # 添加省市信息
    lst = data[['name', 'centerlng', 'centerlat', 'death']].to_dict(orient='record')
    for i in lst:
        plt.text(i['centerlng'] - 2, i['centerlat'], i['name'] + ':' + str(i['death']))
    plt.axis('off')
    plt.savefig(r'figure\special_accident_analysis.png', dpi=100)



