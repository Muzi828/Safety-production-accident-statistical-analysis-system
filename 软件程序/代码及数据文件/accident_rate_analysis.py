import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import matplotlib.pyplot as plt
from dateutil.parser import parse

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

def get_data_accident_china():
    data_by_month = excel_concat(r'数据\accident_type_by_two_month')
    data_by_month['事故类型'] = data_by_month['事故类型'].apply(lambda x: x.replace('露', '漏'))
    data_by_month['日期'] = data_by_month['日期'].apply(lambda x: x.replace('.xls', ''))
    data_by_month['日期'] = [parse(i) for i in data_by_month['日期']]
    data_by_month.sort_values(by='日期', ascending=True, inplace=True)
    data_by_month['年'] = data_by_month['日期'].dt.year
    data_by_month['月'] = data_by_month['日期'].dt.month
    data_by_month['上/下半年'] = pd.cut(data_by_month['月'], bins=[0, 6, 12], labels=['上半年', '下半年'])
    data_accident_china = data_by_month[data_by_month['事故类型'] == '总计']
    data_accident_china = data_accident_china.sort_values(by='日期')
    return data_accident_china

def acc_rate_by_month(month):
    data_accident_china = get_data_accident_china()
    data_same_rate = data_accident_china[['年', '月', '上/下半年', '事故/起']]
    data_same_rate_ = data_same_rate[data_same_rate['月'].isin([month])]
    data_same_rate_[f'rate_{month}_{month+1}'] = (data_same_rate_['事故/起'] - data_same_rate_.shift(1)['事故/起'])*100 / data_same_rate_['事故/起']
    data_same_rate_[f'rate_{month}_{month+1}'] = data_same_rate_[f'rate_{month}_{month+1}'].apply(lambda x: round(x,2))
    data_same_rate_[f'rate_{month}_{month+1}'].fillna(0,inplace=True)
    return data_same_rate_[f'rate_{month}_{month+1}']

def accident_ring_rate():
    data_accident_china = get_data_accident_china()
    data_accident_china['环比增长率%'] = (data_accident_china['事故/起'] - data_accident_china.shift(1)['事故/起']) * 100 / \
                                    data_accident_china['事故/起']
    data_accident_china['环比增长率%'] = data_accident_china['环比增长率%'].apply(lambda x: round(x, 2))
    data_rate = data_accident_china[['年', '月', '环比增长率%']]
    data_rate['时间'] = data_rate.apply(lambda x: str(int(x['年'])) + '/' + str(int(x['月'])), axis=1)
    data_rate = data_rate.drop(['年', '月'], axis=1).set_index('时间')
    data_rate.fillna(0, inplace=True)
    return data_rate

def plot_ring_rate():
    data_rate = accident_ring_rate()
    data_rate.plot(figsize=(16, 4), style='--b.', ylim=[-65, 40], alpha=0.8)
    plt.axhline(0, color='r', linestyle="--", alpha=0.8)
    plt.ylabel('事故环比增长率/%')
    plt.margins(0.015)
    plt.savefig(r'figure\accident_ring_rate.png', dpi=200)

def accident_same_rate():
    data_accident_china = get_data_accident_china()
    data_same_rate = data_accident_china[['年', '月', '上/下半年', '事故/起']]
    data_same_rate_ = data_same_rate[data_same_rate['月'].isin([1])]
    data_same_rate_['rate_1_2'] = (data_same_rate_['事故/起'] - data_same_rate_.shift(1)['事故/起']) * 100 / data_same_rate_[
        '事故/起']
    data_same_rate_['rate_1_2'] = data_same_rate_['rate_1_2'].apply(lambda x: round(x, 2))
    data_same_rate_['rate_1_2'].fillna(0, inplace=True)
    data_same_rate_.drop(['月', '事故/起'], 1, inplace=True)
    for month in range(3, 12, 2):
        data_same_rate_[f'rate_{month}_{month + 1}'] = acc_rate_by_month(month).values

    acc_up_year = data_same_rate[data_same_rate['上/下半年'].isin(['上半年'])].groupby(by='年').sum()
    rate_up_year = (acc_up_year['事故/起'] - acc_up_year.shift(1)['事故/起']) * 100 / acc_up_year['事故/起']
    rate_up_year = rate_up_year.apply(lambda x: round(x, 2))
    rate_up_year.fillna(0, inplace=True)

    acc_down_year = data_same_rate[data_same_rate['上/下半年'].isin(['下半年'])].groupby(by='年').sum()
    rate_down_year = (acc_down_year['事故/起'] - acc_down_year.shift(1)['事故/起']) * 100 / acc_down_year['事故/起']
    rate_down_year = rate_down_year.apply(lambda x: round(x, 2))
    rate_down_year.fillna(0, inplace=True)

    data_same_rate_['rate_up_year'] = rate_up_year.values
    data_same_rate_['rate_down_year'] = rate_down_year.values

    data_same_rate_.drop(['上/下半年'], 1, inplace=True)
    acc_year = data_same_rate.groupby(by='年').sum()
    rate_year = (acc_year['事故/起'] - acc_year.shift(1)['事故/起']) * 100 / acc_year['事故/起']
    rate_year = rate_year.apply(lambda x: round(x, 2))
    rate_year.fillna(0, inplace=True)

    data_same_rate_['rate_year'] = rate_year.values
    data_same_rate_.set_index('年', inplace=True)
    return data_same_rate_

