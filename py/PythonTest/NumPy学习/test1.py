import numpy as np


def test5():
    #线性代数与一些技巧
    print("---------------------------------")

def test4():
    #索引
    print("---------------------------------")
    """
    花式索引 = 用数组当下标
    一维数组用索引数组 → 批量取值
    索引是几维，结果就是几维
    二维数组用 i,j 两个索引矩阵 → 一一对应取值
    可以直接赋值 → 批量修改
    """
    # 1. 创建数组 a: [0, 1, 4, 9, 16, 25, 36, 49, 64, 81, 100, 121]
    a = np.arange(12)**2

    # 2. 定义一个索引数组：我要去取第 1,1,3,8,5 个元素
    i = np.array([1, 1, 3, 8, 5])

    # 3. 花式索引！
    print(a[i])

    j = np.array([[3,4], [9,7]])
    print(a[j])


    print("---------------------------------")

    a = np.arange(12).reshape(3,4)
    # a 长这样：
    # [[ 0  1  2  3]
    #  [ 4  5  6  7]
    #  [ 8  9 10 11]]

    i = np.array([[0,1],
                  [1,2]]) # 行索引
    j = np.array([[2,1],
                  [3,3]]) # 列索引


    print(a[i, j])

    """
    0,2   1,1
    1,2   2,3
    
    """

    print("---------------------------------")
    a = np.array([0,1,2,3,4])
    a[[1,3,4]] = 0  # 把第1、3、4位全部改成0
    print("----------------------------------")
    #布尔索引
    a = np.arange(12).reshape(3,4)
    print( a)
    b=a>4
    print(b)
    print(a[b])
    a[b]=-1
    print(a)

def test3():
    #广播
    print("---------------------------------")
    """
    两个形状不一样的数组，NumPy 自动把它们 “扩展” 成相同形状，然后再计算。
    
    维度少的数组，前面补 1比如 (3,) → 变成 (1,3)
    最终形状 = 每个轴取最大值比如 (3,4) 和 (1,4) → 最终形状 (3,4)
    必须满足：对应轴相等 或 其中一个是 1否则报错！
    
    
    
    """

    a = np.array([[1, 2, 3, 4],
                  [5, 6, 7, 8],
                  [9,10,11,12]])

    # 1 维数组：4个元素
    b = np.array([10, 20, 30, 40])

    # 直接相加！形状不一样，但广播自动生效
    result = a + b
    print(result)





def test2():
    print("---------------------------------")
    arr = np.array([(1, 2, 3), (4, 5, 6)])
    brr = np.array([(7,8,9), (10,11,12)])

    vstack = np.vstack((arr, brr))
    # 竖向堆叠
    hstack = np.hstack((arr, brr))
    # 横向堆叠


    print(vstack)
    print(hstack)

    print("-------------------------")
    arr = np.array([[1, 2, 3, 4, 5, 6],
                    [7, 8, 9, 10, 11, 12]])
    print(np.hsplit(arr,2))
    print(np.vsplit(arr,2))
    print("-------------------------")
    print(np.hsplit(arr,[2,3]))
    #[]里的数字是切割位置的索引，从2，3后面分割

    print("-------------------------")
    #浅拷贝
    view = arr.view()
    print(view is arr)
    # 判断是否是同一对象
    print(view.base is arr)
    # 判断源头指针
    print( view.flags.owndata)
    # 判断是否是原数据
    #深拷贝
    copy = arr.copy()

    print(copy is arr)
    print(copy.base is arr)
    print(copy.flags.owndata)

def test1():
    # 创建数组
    array = np.array([1, 2, 3, 4])
    print( array)
    np_array = np.array([(1.5, 2, 3), (4, 5, 6)])
    print(np_array)
    n = np.array([[1, 2], [3, 4]], dtype=str)
    print( n)
    """
    创建集合
    一维二维
    设置指定类型
    
    
    int
整数
dtype=int → [1, 2, 3]
float
浮点数
dtype=float → [1.0, 2.0, 3.0]
complex
复数
dtype=complex → [1.+0.j, 2.+0.j]
bool
布尔值
dtype=bool → [True, False]
str
字符串
dtype=str → ['a', 'b']
    
    """
    #使用函数创建
    """
    使用函数创建
zeros(shape) 函数创建一个全是 0 的数组
ones(shape) 函数创建全是 1 的数组
empty(shape) 创建一个随机的数组。默认创建数组的类型是 float64
arange(start, end, step) 为了创建数字序列，返回一个数组而不是列表
linspace(start, end, num) 类似arange()，但它接收元素数量而不是步长作为参数
    """
    zeros = np.zeros(5, dtype=int)
    print( zeros)
    empty = np.empty(5, dtype=int)
    print( empty)
    arange = np.arange(1, 10, 1)
    print( arange)


    #访问数组
    print(array[0])
    print(array[1:3])
    ndarray = np.array([(1, 2, 3, 4, 5, 6, 7, 8, 9, 10), (21, 22, 23, 24, 25, 26, 27, 28, 29, 30)])

    print(ndarray[1,1:6])
    print("-------------------------")
    print(array)
    array_ = array + 2
    print(array_)
    array_1 = array + 1

    print(array_1)
    print("----------------------------------集合的加减和向量积")
    array__array__ = array_ + array_1
    print(array__array__)
    array__ = array_ @ array_1
    print(array__)
    print("----------------------------------")
    print(array)
    print(array.min())
    print(array.mean())
    print(array.max())
    print(array.sum())

    array1 = np.array([(1, 2, 3), (4, 5, 6), (7, 8, 9)])
    print(array1)
    print(array1.min(axis=0))
    print(array1.min(axis=1))

    print("\n【示例3】keepdims 参数")
    #print(f"arr.min(axis=0, keepdims=True):\n{arr.min(axis=0, keepdims=True)}")
    #print(f"形状: {arr.min(axis=0, keepdims=True).shape}")  # 输出: (1, 3)
    #print(f"arr.min(axis=0, keepdims=False):\n{arr.min(axis=0, keepdims=False)}")
    #print(f"形状: {arr.min(axis=0, keepdims=False).shape}")  # 输出: (3,)
    #默认false 压缩为一维
    print(array1.min(axis=0, keepdims=True))
    print(array1.min(axis=0, keepdims=False))
    print(array1.min(axis=1, keepdims=True))
    print(array1.min(axis=1, keepdims=False))



    # 4. out 参数 - 指定输出数组
    print("\n【示例4】out 参数")
    result = np.zeros(3, dtype=int)
    array1.min(axis=0, out=result)
    print(f"结果数组: {result}")

    """
axis
指定计算最小值的轴
axis=0(列), axis=1(行)

keepdims
是否保持原维度
True保持, False不保持

out
输出结果的数组
预先创建的数组

initial
初始比较值
如果initial更小则返回它

where
条件掩码
只在满足条件的元素中找最小值
    
    """



    print('---------------------------------')
    print("【示例5】numpy.sin()和numpy.cos()函数")


    print(array)
    print(np.sin(array))
    print(np.cos(array))
    print("===============================")
    array = np.array([1, 4, 3, 5, 2,9])
    print(array)
    print(array.shape)
   # print(np.reshape(array,(2,4)))
    array_reshape = array.reshape(2, 3)
    #修改格式 从1维度修改其他维度，但是总数必须匹配
    print(array_reshape)
    #转置
    print(array_reshape.T)



if __name__ == '__main__':
    #test1()
    #test2()
    #test3()
    test4()
    test5()






