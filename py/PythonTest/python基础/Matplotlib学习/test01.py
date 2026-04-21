import matplotlib.pyplot as plt
import numpy as np

"""

matplotlib主要是一个2d画图库

"""


def test2():
    #简单例子
    print("简单例子")
    x = np.linspace(0, 2, 100)
    # 用 NumPy 生成从 0 到 2 之间均匀分布的 100 个点作为 x 轴数据
    print(x)

    plt.plot(x, x,    label='linear')    # y = x      线性函数
    plt.plot(x, x**2, label='quadratic') # y = x²     二次函数
    plt.plot(x, x**3, label='cubic')     # y = x³     三次函数
    #label 给线标注名字
    plt.xlabel('x 坐标')   # x 轴标题
    plt.ylabel('y 坐标')   # y 轴标题
    plt.title("测试表格") # 图表标题
    plt.legend()             # 显示图例（对应上面的 label）
    plt.show()               # 渲染并弹出图形窗口



def test3():
    #多个字图
    print("多个字图")
    fig, (ax1, ax2) = plt.subplots(1, 2)
    """
    基本作用                                                                                
   
  创建一个画布（figure），并在上面划分出多个子图区域（axes）。                            
                  
  ---
  函数签名

  fig, axes = plt.subplots(nrows, ncols)

  ┌───────────┬────────────────────────┐
  │   参数    │          含义          │
  ├───────────┼────────────────────────┤
  │ nrows     │ 子图的行数             │
  ├───────────┼────────────────────────┤
  │ ncols     │ 子图的列数             │
  ├───────────┼────────────────────────┤
  │ 返回 fig  │ 整个画布对象           │
  ├───────────┼────────────────────────┤
  │ 返回 axes │ 子图对象（数组或元组） │
  └───────────┴────────────────────────┘
    """
    #my_plotter(ax1, data1, data2, {'marker': 'x'})
    #my_plotter(ax2, data3, data4, {'marker': 'o'})

def my_plotter(ax, data1, data2, param_dict):
    out = ax.plot(data1, data2, **param_dict)
    return out

""" ax.plot(data1, data2, **param_dict)                                                     
                  
  ┌──────────────┬────────────────────────────────┐
  │     部分     │              含义              │
  ├──────────────┼────────────────────────────────┤
  │ ax           │ 指定的子图对象（画在哪张图上） │
  ├──────────────┼────────────────────────────────┤
  │ data1        │ x 轴数据                       │
  ├──────────────┼────────────────────────────────┤
  │ data2        │ y 轴数据                       │
  ├──────────────┼────────────────────────────────┤
  │ **param_dict │ 把字典解包成关键字参数         │
  └──────────────┴────────────────────────────────┘

  ---
  **param_dict 解包过程

  param_dict = {'marker': 'x'}

  # 解包后等价于：
  ax.plot(data1, data2, marker='x')

  marker='x' 表示每个数据点用 ✕ 标记显示：
  marker='x'  →  ✕ 形状
  marker='o'  →  ● 形状
  marker='*'  →  ★ 形状
  marker='^'  →  ▲ 形状

  ---
  返回值 out

  out = ax.plot(...)

  ax.plot() 返回一个线条对象列表 [Line2D]，保存在 out
  中，可以用来后续修改线条样式，但这里只是返回出去，不做额外操作。

  ---
  整体执行效果

  # 调用时
  my_plotter(ax1, data1, data2, {'marker': 'x'})

  # 内部执行
  ax1.plot(data1, data2, marker='x')
  # → 在左子图上，以 ✕ 标记画出 data1 vs data2 的散点折线图

  简单说：就是在指定子图上，用指定样式把两组数据画成图。
"""



def test4():
    #其他
    print("子图布局")

if __name__ == '__main__':
    test2()


