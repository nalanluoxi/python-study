import sklearn
from sklearn import datasets

"""

Scikit-learn（简称sklearn）是开源的 Python 机器学习库，它基于Numpy和Scipy，包含大量数据挖掘和分析的工具，例如数据预处理、交叉验证、算法与可视化算法等。

从功能上来讲，Sklearn基本功能被分为分类，回归，聚类，数据降维，模型选择，数据预处理。

从机器学习任务的步骤来讲，Sklearn可以独立完成机器学习的六个步骤：

选择数据：将数据分成三组，分别是训练数据、验证数据和测试数据。
模拟数据：使用训练数据来构建使用相关特征的模型。
验证模型：使用验证数据接入模型。
测试模型：使用测试数据检查被验证的模型的表现。
使用模型：使用完全训练好的模型在新数据上做预测。
调优模型：使用更多数据、不同的特征或调整过的参数来提升算法的性能表现。

"""

def test1():
    digits = datasets.load_digits()
   # print(digits)
    print(digits.data)
    # 训练数据
    print('===========================')
    # 标签
    print(digits.target)
    print('===========================')
    # 原始图片
    print(digits.images)
    print('===========================')
    # 标签名字
    print(digits.target_names)
    print('===========================')
    print(digits.DESCR)

if __name__ == '__main__':
    test1()

