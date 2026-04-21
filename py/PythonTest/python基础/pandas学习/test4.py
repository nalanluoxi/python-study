import pandas as pd
import matplotlib.pyplot as plt

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 50)



def test8():
    # 表1：英国降雨数据
    df_uk = pd.DataFrame({
        'year':         [2020, 2021, 2022, 2023],
        'uk_rainfall':  [1200, 1350, 980,  1100]
    })

    # 表2：日本降雨数据
    df_jpn = pd.DataFrame({
        'year':         [2020, 2021, 2022, 2024],  # 注意：2023没有，多了2024
        'jpn_rainfall': [1600, 1450, 1700, 1550]
    })
    print("========表1")
    print(df_uk)
    print("========表2")
    print(df_jpn)

    print("------------inner")
    merge1 = df_uk.merge(df_jpn, on='year', how='inner')
    print(merge1)
    print("------------left")
    merge2 = df_uk.merge(df_jpn, on='year', how='left')
    print(merge2)
    print("------------right")
    merge3 = df_uk.merge(df_jpn, on='year', how='right')
    print(merge3)
    print("------------outer")
    merge4 = df_uk.merge(df_jpn, on='year', how='outer')
    print(merge4)

    print("------------画图")
    merge1.plot(x='year', y=['uk_rainfall', 'jpn_rainfall'])
    plt.show()

def test7():
    #df = pd.read_csv("table/new_记录.csv")
    #print(df)
    df = pd.DataFrame({
        'city':    ['北京', '上海', '北京', '上海', '北京'],
        'product': ['A',   'A',   'B',   'B',   'A'],
        'sales':   [100,   200,   170,   300,   120]
    })

    # 按城市分组，计算销售额总和
    sales__sum = df.groupby('city')['sales'].sum()
    print(sales__sum)
    print("--------")
    product_sales__sum = df.groupby(['city', 'product'])['sales'].sum()
    print(product_sales__sum)

    print("--------------")
    city__sum = df.groupby('city').sum()
    print(city__sum)
    print("-----------------")
    sales__max = df.groupby('city')['sales'].max()
    print(sales__max)
    print("-----------------")
    result = df.groupby(['city', 'product'])['sales'].sum()
    unstack = result.unstack()
    print(unstack)
    """
    把多层索引的最内层行索引变成列（转置内层）。

  # groupby 多列后得到多层索引
  result = df.groupby(['city', 'product'])['sales'].sum()
  print(result)
  # city  product
  # 上海   A          200
  #        B          300
  # 北京   A          220
  #        B          150

  # unstack 把 product 从行变成列
  result.unstack()
  # product    A    B
  # city
  # 上海      200  300
  # 北京      220  150

    """

    print("=============")
    df2= pd.DataFrame({
        'city':    ['北京', '北京', '上海', '上海'],
        'product': ['A',   'B',   'A',   'B'],
        'sales':   [220,   150,   200,   300]
    })

    pivot = df2.pivot(index='city', columns='product', values='sales')
    print(pivot)
    """
    直接指定行、列、值来重塑 DataFrame，类似 Excel 透视表。

  df = pd.DataFrame({
      'city':    ['北京', '北京', '上海', '上海'],
      'product': ['A',   'B',   'A',   'B'],
      'sales':   [220,   150,   200,   300]
  })

  df.pivot(index='city', columns='product', values='sales')
  # product    A    B
  # city
  # 上海      200  300
  # 北京      220  150
    需要列数对应符合,df2旋转后对应a,b分别有一个,原来df会报错
    """

"""
    groupby()分组
    max() 、 min() 、mean()最大,最小,平均
    unstack()
    pivot()：旋转
    
    """


def test6():
    """
    显示被折叠问题
    常用的显示设置汇总：

  ┌──────────────────────┬─────────────────────────────┐
  │        设置项        │            作用             │
  ├──────────────────────┼─────────────────────────────┤
  │ display.max_columns  │ 最大显示列数，None = 全部   │
  ├──────────────────────┼─────────────────────────────┤
  │ display.max_rows     │ 最大显示行数，None = 全部   │
  ├──────────────────────┼─────────────────────────────┤
  │ display.width        │ 终端显示宽度，None = 自适应 │
  ├──────────────────────┼─────────────────────────────┤
  │ display.max_colwidth │ 单列最大字符宽度            │
  └──────────────────────┴─────────────────────────────┘

  一般在文件开头加上前两行就够用了：
  pd.set_option('display.max_columns', None)
  pd.set_option('display.width', None)


    :return:
    """
    # print("-------map---------")
    df = pd.read_csv("table/new_记录.csv")

    print(df.head(10))
    dfs = df["dt"]
    """
    从表获取列

  ┌───────────────┬─────────────────────────────────┐
  │     写法      │              含义               │
  ├───────────────┼─────────────────────────────────┤
  │ df["列名"]    │ 按列名取列，返回 Series         │
  ├───────────────┼─────────────────────────────────┤
  │ df.iloc[:, 0] │ 按整数位置取第0列               │
  ├───────────────┼─────────────────────────────────┤
  │ df.iloc[0]    │ 按整数位置取第0行               │
  ├───────────────┼─────────────────────────────────┤
  │ df.loc[0]     │ 按行索引标签取行（索引是0才行） │
  └───────────────┴─────────────────────────────────┘

    """
    print(dfs)

    print("---------map")
    df_map = df.map(lambda x: x + 1)
    """
    map用法:
     # 用法1：传入函数
  s.map(lambda x: x.upper())
  # 0     APPLE
  # 1    BANANA
  # 2    CHERRY

  # 用法2：传入字典（映射替换）
  s.map({'apple': '苹果', 'banana': '香蕉', 'cherry': '樱桃'})
  # 0    苹果
  # 1    香蕉
  # 2    樱桃

  # 用法3：传入 Series
  mapping = pd.Series({'apple': 1, 'banana': 2, 'cherry': 3})
  s.map(mapping)
  # 0    1
  # 1    2
  # 2    3

  特点：只能用于 Series，不能用于 DataFrame。

    """
    print(df_map)

    print("---------apply")
    df_apply = df.apply(lambda x: x + 1)
    print(df_apply)

    apply = df["cnt_eq_0"].apply(lambda x: 10)
    print(apply)
    print(df.head(10))

    df["cnt_eq_0"] = df["cnt_eq_0"].apply(lambda x: 10)
    print(df.head(10))


def test5():
    df = pd.read_csv("table/new_记录.csv")

    df['dt'] = df.dt.apply(get_year)
    df.head(5)
    print(df.head(10))
    """
    apply ()是将一个函数逐行或逐列应用到 DataFrame/Series 的每个元素上。
    """


def base_year(year):
    base_year = year[:4]
    base_year = pd.to_datetime(base_year).year
    return base_year


def get_year(dt):
    year = str(dt)  # str(dt)[0:4]        # 先转成字符串再切片
    datetime = pd.to_datetime(year)
    """
     pd.to_datetime('2026') 只传入了年份字符串，pandas 会自动补全缺失的月份和日期，默认填充为 1月1日。                                                                                                   
   
  pd.to_datetime('2026')        # → 2026-01-01 00:00:00  只有年，补01-01                                                                                                                                   
  pd.to_datetime('2026-03')     # → 2026-03-01 00:00:00  只有年月，补01
  pd.to_datetime('2026-03-31')  # → 2026-03-31 00:00:00  完整日期                                                                                                                                          
                  
  所以输出 2026-01-01 00:00:00 是正常的，并不是错误。
    
    """
    print(datetime)
    datetime_year = datetime.year
    return datetime_year

    # base_year = year[:4]
    # base_year= pd.to_datetime(base_year).year
    # return base_year


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
        取消索引df.reset_index()
        index = df.sort_index(ascending=False)  # 倒序（从大到小）                                                                                                                                               
        index = df.sort_index(ascending=True)   # 正序（从小到大，默认）
    """
    sort_values = df.sort_values("cnt_eq_0", ascending=False)
    print(sort_values.head(10))
    df = df.reset_index()
    print(df.head(10))


def test03():
    path = "table/根据站点分类1.csv"
    df = pd.read_csv(path)
    print(df.head(100))
    df1 = df[df.domain.str.startswith("www.", na=False)]
    print("筛选出www开头的域名")
    print(df1.head(100))
    df2 = df[
        (df.url_count > 10) & (df.domain.str.startswith("www.", na=False) | df.domain.str.endswith(".com", na=False))]
    print("筛选出url_count>10的域名")
    print(df2.head(100))
    # 字符处理要加.str

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
    # print(index.head(100))

    """
    df.sort_index()按照索引排序
    """


def test02():
    path = "table/new_记录.csv"
    df = pd.read_csv(path)
    dt1 = df[df["dt"] > 20260331]
    print("删选dt>20260331的")
    print(dt1.head())
    # 过滤筛选


def test01():
    path = "table/new_记录.csv"
    df = pd.read_csv(path)
    # print(df)
    unique = df["dt"].unique()
    print(unique)
    # 删选当前列唯一数据


if __name__ == '__main__':
    # test01()
    # test02()
    # test03()
    # test4()
    # test5()
    # test6()
    test7()
    #test8()

