import pymysql
import pandas as pd
conn = pymysql.connect(host = '127.0.0.1', user = 'root', passwd = 'lx520828',db = 'test')
df = pd.read_sql('select * from accident_data',conn)

print(d.head())



