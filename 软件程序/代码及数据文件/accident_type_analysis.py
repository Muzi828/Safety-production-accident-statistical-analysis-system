import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import matplotlib.pyplot as plt
import time_series_analysis

def get_type_data_by_month(data):
    df = pd.DataFrame()
    for i in range(1,13):
        df_ = data[data['月'].isin([i])].groupby(by = '事故类型').sum()
        df_[f'{i}月占比'] = df_['事故/起'] /df_['事故/起'].sum()
        df_[f'{i}月占比'] = df_[f'{i}月占比'].apply(lambda x: round(x*100,2))
        df[f'{i}月占比'] = df_[f'{i}月占比']
    return df

def get_type_data_by_season(data):
    df = pd.DataFrame()
    for i in list('一二三四'):
        df_ = data[data['季度'].isin([f'第{i}季度'])].groupby(by = '事故类型').sum()
        df_[f'第{i}季度占比'] = df_['事故/起'] /df_['事故/起'].sum()
        df_[f'第{i}季度占比'] = df_[f'第{i}季度占比'].apply(lambda x: round(x*100,2))
        df[f'第{i}季度占比'] = df_[f'第{i}季度占比']
    return df

def data_type_month():
    data_by_month = time_series_analysis.data_month()
    type_data_by_month = data_by_month[~data_by_month['事故类型'].isin(['总计'])][['月','事故类型','事故/起']]
    type_data_by_month[type_data_by_month['月'].isin([1])].groupby(by='事故类型').sum()
    data_type_month = get_type_data_by_month(type_data_by_month)
    return data_type_month

def data_type_season():
    data_by_month = time_series_analysis.data_month()
    type_data_by_season = data_by_month[~data_by_month['事故类型'].isin(['总计'])][['季度', '事故类型', '事故/起']]
    data_by_season = get_type_data_by_season(type_data_by_season)
    return data_by_season

def data_type_acc():
    data_by_month = time_series_analysis.data_month()
    type_data_by_month = data_by_month[~data_by_month['事故类型'].isin(['总计'])][['月', '事故类型', '事故/起']]
    type_data_by_month[type_data_by_month['月'].isin([1])].groupby(by='事故类型').sum()
    data_type_acc = type_data_by_month.groupby(by='事故类型').sum()
    data_type_acc.drop('月', axis=1, inplace=True)
    return data_type_acc

def plot_data_type_acc():
    type_data = data_type_acc()
    from bokeh.palettes import brewer
    plt.rcParams['figure.dpi'] = 100
    plt.style.use('ggplot')
    colori = brewer['YlGn'][7]
    plt.figure(figsize=(12, 6))
    # 设置颜色
    result = type_data.index
    plt.pie(type_data['事故/起'], labels=result, wedgeprops={'linewidth': 0.6, 'edgecolor': "black"}, autopct='%.2f%%',
            pctdistance=0.6, labeldistance=1.1, explode=[0.04, 0, 0, 0, 0, 0],
            startangle=0, shadow=False, radius=1.2, counterclock=False, colors=colori)
    plt.legend(loc=(1, 0.))
    plt.margins(0.5)
    plt.savefig(r'figure\\type.png', dpi=200)


