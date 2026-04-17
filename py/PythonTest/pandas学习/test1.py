
import pandas as pd

df = pd.read_csv("/Volumes/WenshuSpace/下载/摸底表.csv",encoding="utf-8")

head = df.head(100)

print(head)

