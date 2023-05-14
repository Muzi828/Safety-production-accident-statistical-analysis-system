import pandas as pd
import numpy as np
from dateutil.parser import parse
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

def excel_concat(dir_path):
    import glob
    file_paths = glob.glob(dir_path + '/*.xls')
    #print(file_paths)
    df = pd.DataFrame()
    i = 1
    for file_path in file_paths:
        df_ = pd.read_excel(file_path)
        df_['日期'] = file_path.split("\\")[-1].split("-")[0].replace("_","/") + "/01"
        df = pd.concat([df,df_])
        print(f'Concating {i} file')
        i += 1
    print('Concated!')
    return df

def data_year():
    df = excel_concat(r'数据\zone_data')
    data = df.copy().fillna(0).reset_index(drop = True)
    data_accident_china = data[data['省市'] == '全国'][['日期','事故/起','死亡/人','受伤/人']]

    data_accident_china['日期'] = [parse(i) for i in data_accident_china['日期']]
    data_accident_china['年'] = data_accident_china['日期'].dt.year
    data_accident_china['月'] = data_accident_china['日期'].dt.month
    data_accident_china['上/下半年'] = pd.cut(data_accident_china['月'],bins=[0,6,12],labels=['上半年','下半年'])
    data_accident_china = data_accident_china.sort_values(by = '日期').drop('日期',axis = 1).reset_index(drop = True)

    data_by_year = data_accident_china[['年','事故/起','死亡/人','受伤/人']]
    data_by_year = data_by_year.groupby(by = '年').sum()

    data_by_half_year = data_accident_china[['年','上/下半年','事故/起']]
    data_by_half_year = data_by_half_year.groupby(by=['年','上/下半年']).sum()

    ls_befor_year = []
    ls_after_year = []
    for i in range(2005,2020):
        ls_befor_year.extend(data_by_half_year.ix[i].values[0])
        ls_after_year.extend(data_by_half_year.ix[i].values[1])

    data_by_half_year = pd.DataFrame({"上半年":ls_befor_year,
                                "下半年":ls_after_year},index=np.arange(2005,2020))

    population_year_data = pd.read_excel('D:\paper\safety\data\population_year.xlsx')
    data_by_year = pd.merge(data_by_year,population_year_data,left_index=True,right_on='年份')
    data_by_year['十万人事故率/%'] = data_by_year.apply(lambda x: round(x['事故/起']/x['人口/万']*1000,2), axis =1)
    data_by_year['十万人死亡率/%'] = data_by_year.apply(lambda x: round(x['死亡/人']/x['人口/万']*1000,2), axis =1)
    data_by_year['十万人受伤率/%'] = data_by_year.apply(lambda x: round(x['受伤/人']/x['人口/万']*1000,2), axis =1)
    gdp_year_data = pd.read_excel(r'D:\paper\safety\data\gdp_year.xlsx')
    data_by_year = pd.merge(data_by_year,gdp_year_data,left_on='年份',right_on='年份')
    data_by_year['亿元gdp事故率/%'] = data_by_year.apply(lambda x: round(x['事故/起']/x['gdp/亿元']*100,3), axis =1)
    data_by_year['亿元gdp死亡率/%'] = data_by_year.apply(lambda x: round(x['死亡/人']/x['gdp/亿元']*100,3), axis =1)
    data_by_year['亿元gdp受伤率/%'] = data_by_year.apply(lambda x: round(x['受伤/人']/x['gdp/亿元']*100,3), axis =1)
    return data_by_year,data_by_half_year,

def plot_data_year():
    data_by_year, data_by_half_year = data_year()
    fig,ax1 = plt.subplots(figsize = (12, 8), facecolor='white')
    plt.xticks(np.arange(2005,2020))
    x = data_by_half_year.index
    y1 = data_by_half_year['上半年'].values
    y2 = data_by_half_year['下半年'].values
    y3 = data_by_year['事故/起'].values
    y4 = data_by_year['死亡/人'].values
    y5 = data_by_year['受伤/人'].values

    ax1.set_ylim([0,5000])
    bar_width = 0.1
    ax1.bar(x-bar_width,y1,color='dimgray',width=bar_width,label="上半年年事故总量",alpha=0.5)
    ax1.bar(x+bar_width,y2,color='black',width=bar_width,label="下半年年事故总量",alpha=0.5)
    ax1.plot(x,y3,'-b*',label='每年事故总总量',color = 'black')
    mean = data_by_year["事故/起"].sum() / len(data_by_year["事故/起"])
    ax1.axhline(mean, label = '年平均事故次数:{:.0f}起'.format(mean), color = 'r', linestyle = '--',alpha = 0.5)
    ax1.axvline(2011, color = 'g',label ='2011年事故分割线',linestyle = '--',alpha = 0.5)
    ax1.legend(loc=(0.755,0.82))
    ax1.text(2010.8,1365,1365)
    ax1.set_ylabel('事故发生数量（起）')
    ax1.set_xlabel('事故发生年份')

    ax2 = ax1.twinx()
    ax2.set_ylim([0,10000])
    ax2.plot(x,y4,'-rx',label='年死亡人数')
    ax2.plot(x,y5,'-o',label='年受伤人数')
    ax2.legend(loc=(0.1,0.92))
    ax2.set_ylabel('事故受伤/死亡人数（人）')
    plt.margins(0.015)
    # plt.show()
    plt.savefig(r'figure\time_series1.png',dpi=300)

def data_month():
    data_by_month = excel_concat(r'数据\accident_type_by_month')
    data_by_month['事故类型'] = data_by_month['事故类型'].apply(lambda x: x.replace('露','漏').replace('毒物泄漏与中毒','泄漏中毒'))
    data_by_month['日期'] = data_by_month['日期'].apply(lambda x: x.replace('.xls',''))
    data_by_month['日期'] = [parse(i) for i in data_by_month['日期']]
    data_by_month.sort_values(by = '日期', ascending=True, inplace = True)
    data_by_month['年'] = data_by_month['日期'].dt.year
    data_by_month['月'] = data_by_month['日期'].dt.month
    data_by_month['季度'] = pd.cut(data_by_month['月'],bins=[0,3,6,9,12],labels=['第一季度','第二季度','第三季度','第四季度'])
    return data_by_month

def data_month_acc():
    data_by_month = data_month()
    fig_data_by_month_1 = data_by_month[data_by_month['事故类型'].isin(['总计'])][['月', '事故/起', '死亡/人']].groupby(by='月').sum()
    fig_data_by_month_1['事故占比'] = fig_data_by_month_1['事故/起'] / fig_data_by_month_1['事故/起'].sum()
    fig_data_by_month_1['事故占比'] = fig_data_by_month_1['事故占比'].apply(lambda x: str(round(x * 100, 2)) + '%')
    return fig_data_by_month_1

def data_month_detail():
    data_by_month = data_month()
    fig_data_by_month_2 = data_by_month[data_by_month['事故类型'].isin(['总计'])][['年', '月', '事故/起']].groupby(
        by=['年', '月']).sum()
    fig_data_by_month_2 = fig_data_by_month_2.unstack(['月'])
    fig_data_by_month_2.columns = [f'{i}月' for i in range(1, 13)]
    return fig_data_by_month_2

def data_season_acc():
    data_by_month = data_month()
    fig_data_by_season_1 = data_by_month[data_by_month['事故类型'].isin(['总计'])][['季度', '事故/起', '死亡/人']].groupby(
        by='季度').sum()
    fig_data_by_season_1['事故占比'] = fig_data_by_season_1['事故/起'] / fig_data_by_season_1['事故/起'].sum()
    fig_data_by_season_1['事故占比'] = fig_data_by_season_1['事故占比'].apply(lambda x: str(round(x * 100, 2)) + '%')
    return  fig_data_by_season_1

def data_season_detail():
    data_by_month = data_month()
    fig_data_by_season_2 = data_by_month[data_by_month['事故类型'].isin(['总计'])][['年', '季度', '事故/起']].groupby(
        by=['年', '季度']).sum()
    fig_data_by_season_2 = fig_data_by_season_2.unstack(['季度'])
    fig_data_by_season_2.columns = ['第一季度', '第二季度', '第三季度', '第四季度']
    for i in list('一二三四'):
        fig_data_by_season_2[f'第{i}季度占比'] = fig_data_by_season_2[f'第{i}季度'] / fig_data_by_season_2.sum(axis=1)
        fig_data_by_season_2[f'第{i}季度占比'] = fig_data_by_season_2[f'第{i}季度占比'].apply(
            lambda x: str(round(x * 100, 2)) + '%')
    return fig_data_by_season_2