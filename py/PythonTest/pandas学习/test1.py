
import os
import pandas as pd

df = pd.read_csv("/Volumes/WenshuSpace/下载/摸底表.csv",encoding="utf-8")
#读取路径的csv文件
head = df.head(100)
#serise是一纬数据
#dataframe是二维表格类型
#从这里获取的是表格的
print(head)

output_path = "table/new_记录.csv"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
#创建目录
df.to_csv(output_path)
#保存文件
"""
列操作

"""
cnt_qu_0 = df.columns[1]
#根据索引序号获取列名
print(cnt_qu_0)

print("================")
eq__ = df["cnt_eq_0"]

print(eq__)
print("======")
print(eq__.values)
print(eq__.index)
print(eq__.name)
"""
直接根据列名获取
"""
print("----------------------")
cnt____ = df[["dt", "cnt_eq_0", "cnt_1_10"]]
print(cnt____.values)
#获取多列
print("-=-=-=-=-=-=-=-=-=-=-=-=")
df.columns = ['dt1', 'dt2', '333', '444', '555', '666', '7777']
"""
修改列名
 1. 一次性替换所有列名（按顺序）：                                                                                                                                                                        
  df.columns = ['新列名1', '新列名2', '新列名3']                                                                                                                                                           
                                                                                                                                                                                                           
  2. 只改某几列，用 rename：
  df = df.rename(columns={'dt': '日期', 'dt1': '日期2'})

  3. 用 str 方法批量处理列名（如全部转大写）：
  df.columns = df.columns.str.upper()       # 全部大写
  df.columns = df.columns.str.replace('_', '-')  # 替换字符

  4. 你当前第42行如果想重命名 dt 和 dt1：
  df.columns = df.columns.map(lambda x: '日期' if x == 'dt' else x)

"""

print(df.head())

print("=========")

comlen = len(df.columns)
print(df.columns)
for i in range(comlen):
    print("第",i,"列的列名:",df.columns[i])
#print(df.ix[0,0])
#这个版本这个方法被丢弃了

print("==================")
print(df.iloc[0,0])
#根据xy坐标获取
print(df.loc[0,'dt1'])
#根据行+列名获取

