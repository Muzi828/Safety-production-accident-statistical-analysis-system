import warnings
warnings.filterwarnings('ignore')
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date


def get_year_month_day(df, time_col):
    '''Extract the year, month, and day of the time field data'''

    df['year'] = df[time_col].dt.year
    df['month'] = df[time_col].dt.month
    df['day'] = df[time_col].dt.day
    return df

def restday(year,month,day,holidays_date,add_work_date):
    is_holiday    = [None]*len(year)
    is_weekend = [None]*len(year)
    i=0
    for yy,mm,dd in zip(year,month,day):
        is_weekend[i] = (date(yy,mm,dd) not in add_work_date) and (date(yy,mm,dd).isoweekday() in (6,7)) and (date(yy,mm,dd) not in holidays_date)
        is_holiday[i] = date(yy,mm,dd) in holidays_date
        i+=1
    return is_holiday,is_weekend

def get_data():
    df = pd.read_excel(r'数据\accident_type.xlsx')
    data = df.copy().drop('Unnamed: 6',axis =1)
    data.columns = ['time','province','city','accident','death','injury']

    data = get_year_month_day(data,'time')
    holidays = pd.read_excel(r'数据\holidays.xlsx',usecols=['日期','节假日'])
    holidays_date = [holidays.loc[i,'日期'].date() for i in range(len(holidays))]
    add_work = pd.read_excel(r'数据\add_work.xlsx',usecols=['日期','节假日'])
    add_work_date = [add_work.loc[i,'日期'].date() for i in range(len(add_work))]

    year,month,day = data.time.dt.year, data.time.dt.month, data.time.dt.day
    holiday,weekend = restday(year,month,day,holidays_date,add_work_date)
    data['holiday'] = holiday
    data['weekend'] = weekend
    data = pd.merge(data,holidays,left_on = 'time', right_on = '日期', how = 'left')
    data.drop('日期',axis=1,inplace = True)
    data['weekend_work'] = data.apply(lambda x: date(x.year,x.month,x.day) in add_work_date, axis = 1)
    return data

#因调休周末上班发生的事故
def get_data_add_work():
    data = get_data()
    data_add_work = data[data['weekend_work'] == True]
    data_add_work.reset_index(drop = True,inplace = True)
    return data_add_work

#周末发生的事故
def get_data_weekend():
    data = get_data()
    data_weekend = data[data['weekend'] == True]
    data_weekend.reset_index(drop=True, inplace=True)
    return data_weekend

#节假日发生的事故
def get_data_holidays():
    data = get_data()
    data_holidays = data[data['holiday'] == True]
    data_holidays.reset_index(drop=True, inplace=True)
    return data_holidays

def plot_holidays_data():
    data= get_data()
    plt.rcParams['figure.dpi'] = 140
    data['节假日'].value_counts()[::-1].plot(kind='pie', autopct='%.2f%%', cmap='viridis_r', label=True,
                                          wedgeprops={'linewidth': 1, 'edgecolor': "black"},
                                          figsize=(10, 5),
                                          explode=[0, 0, 0, 0, 0, 0, 0.03])
    plt.axis('off')
    plt.legend(loc=(0.94, 0.1))
    plt.savefig(r'figure\holidays.png', dpi=200)
