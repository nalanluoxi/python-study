
import pandas as pd


def test4():
    df = pd.read_csv("table/new_记录.csv")
    print(df.head(100))
    df = df.set_index("dt")
    index = df.sort_index()
    print(index.head(10))


    index = df.sort_index(ascending=False)
    print(index.head(10))
    """
        设置索引要给值
        之后根据值排序
        index = df.sort_index(ascending=False)  # 倒序（从大到小）                                                                                                                                               
        index = df.sort_index(ascending=True)   # 正序（从小到大，默认）
    """
    sort_values = df.sort_values("cnt_eq_0",ascending=False)
    print(sort_values.head(10))

def test03():
    path="table/根据站点分类1.csv"
    df = pd.read_csv(path)
    print(df.head(100))
    df1 = df[df.domain.str.startswith("www.", na=False)]
    print("筛选出www开头的域名")
    print(df1.head(100))
    df2 = df[(df.url_count > 10) & (df.domain.str.startswith("www.", na=False) | df.domain.str.endswith(".com", na=False))]
    print("筛选出url_count>10的域名")
    print(df2.head(100))
    #字符处理要加.str

    iloc_ = df.iloc[0]
    print(iloc_)
    print("======")
    df_iloc_ = df.iloc[0:5, 0:5]
    print(len(df_iloc_))
    print(df_iloc_.values)

    """
      iloc = integer location，按整数位置索引，与列名无关。                                                                                                                                                    
                  
  df.iloc[0]      # 第1行（索引位置0）
  df.iloc[1]      # 第2行
  df.iloc[-1]     # 最后一行

iloc 还可以取更多

  df.iloc[0:3]       # 前3行（切片）
  df.iloc[0, 1]      # 第0行第1列的单个值
  df.iloc[0:3, 0:2]  # 前3行、前2列


    """
    print('----------------------修改索引')
    df2_ = pd.read_csv("table/new_记录.csv")
    d5 = df2_.set_index("dt")
    loc_ = d5.loc[20260331]
    print(loc_)

    print("--------------排序")
    df_sorted = df2.sort_values("dt")
    print(df_sorted.head(10))
    index = df.sort_index()
    #print(index.head(100))

    """
    df.sort_index()按照索引排序
    """


def test02():
    path="table/new_记录.csv"
    df = pd.read_csv(path)
    dt1 = df[df["dt"] > 20260331]
    print("删选dt>20260331的")
    print(dt1.head())
    #过滤筛选


def test01():
    path="table/new_记录.csv"
    df = pd.read_csv(path)
    #print(df)
    unique = df["dt"].unique()
    print(unique)
    #删选当前列唯一数据

if __name__ == '__main__':
    #test01()
    #test02()
    #test03()
    test4()
