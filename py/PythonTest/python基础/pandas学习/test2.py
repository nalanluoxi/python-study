import os
from os.path import dirname

import  pandas as pd

#读取csv文件保存到制定位置
def readCsvByPath(path,targetpath):
    df = pd.read_csv(path)
    print("显示前10行")
    print(df.head(10))
    os.makedirs(os.path.dirname(targetpath),exist_ok=True)
    df.to_csv(targetpath)