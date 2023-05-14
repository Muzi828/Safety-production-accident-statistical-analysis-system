
import pandas as pd
import glob
import webbrowser
import pathlib

def history_rank_acc():
    data_load = pd.read_excel("数据\\historical_change.xlsx", index_col="Unnamed: 0")
    name_set = set(data_load.name.to_list())
    data_load['date'] = pd.to_datetime(data_load['date'])
    df = pd.DataFrame()
    for city in name_set:
        data_ = data_load[data_load['name'] == city].sort_values(by = 'date')
        data_['value'] = data_['value'].cumsum()
        df = pd.concat([df,data_])

    df.to_csv('history_rank_analysis\history_rank_acc.csv', index=False, encoding='GBK')
    webbrowser.open(r'history_rank\src\bargraph.html')
    return df


def history_rank_month():
    path_dir = r'数据\zone_data'
    path_list = []
    path_root = pathlib.Path(path_dir)
    for item in path_root.iterdir():#对里面所有的文件进行迭代
        path_list.append(item)

    ls_name = []
    ls_date = []
    ls_value = []

    all_file_paths = [str(path) for path in path_list]
    for path in all_file_paths:
        data = pd.read_excel(path)
        ls_name.append(data["省市"].values[:-2])
        ls_value.append(data["事故/起"].values[:-2])
        ls_date.append([path.split("\\")[-1].split("-")[0].replace("_","/") + "/01"]*30)

    name_data = []
    date_data = []
    value_data = []

    for num in range(len(ls_date)):
        for i, j, k in zip(ls_name[num], ls_value[num], ls_date[num]):
            name_data.append(i)
            value_data.append(j)
            date_data.append(k)

    df = pd.DataFrame({"name": name_data,"type": None, "value": value_data, "date": date_data})
    df.to_csv('history_rank_analysis\history_rank_month.csv',index = False,encoding = 'GBK')
    webbrowser.open(r'history_rank\src\bargraph.html')
    return data

