import sklearn
from sklearn import datasets
from sklearn import svm
import matplotlib.pyplot as plt
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
    """"
    digits 数据集中的区别   

  digits.data (训练数据) vs digits.images        
  (原始图片)
                                                 
  ┌─────┬──────────────────────┬──────────────┐
  │     │         data         │    images    │
  ├─────┼──────────────────────┼──────────────┤
  │ 形  │ (1797, 64)           │ (1797, 8, 8) │
  │ 状  │                      │              │
  ├─────┼──────────────────────┼──────────────┤
  │ 结  │ 二维数组，每张图片展 │ 三维数组，保 │
  │ 构  │ 平成64个像素值       │ 留8×8矩阵结  │
  │     │                      │ 构           │
  ├─────┼──────────────────────┼──────────────┤
  │ 用  │ 直接输入机器学习模型 │ 可视化展示、 │
  │ 途  │ （模型需要一维特征向 │ 查看图片原始 │
  │     │ 量）                 │ 形状         │
  └─────┴──────────────────────┴──────────────┘

  本质上是同样的数据，只是形状不同：
  images[i]       →  8×8 的二维矩阵
  data[i]         →
  把上面那个矩阵"拉平"成长度64的一维数组
  data[i] == images[i].flatten()  # True

  ---
  digits.target (标签) vs digits.target_names 
  (标签名字)
  ┌─────┬────────────────────┬────────────────┐
  │     │       target       │  target_names  │
  ├─────┼────────────────────┼────────────────┤
  │ 内  │ [0, 1, 2, ..., 9,  │ [0, 1, 2, 3,   │
  │ 容  │ 0, 1, ...]         │ 4, 5, 6, 7, 8, │
  │     │                    │  9]            │
  ├─────┼────────────────────┼────────────────┤
  │ 长  │ 1797（每张图片对应 │ 10（所有类别， │
  │ 度  │ 一个）             │ 不重复）       │
  ├─────┼────────────────────┼────────────────┤
  │ 作  │ 每张图片对应的答案 │ 所有可能的类别 │
  │ 用  │ 是哪个数字         │ 列表           │
  └─────┴────────────────────┴────────────────┘

  类比理解：
  - target → 试卷上每道题的答案（1797个）
  - target_names → 答案的取值范围是
  0~9（只有10个）

  在这个数据集中两者看起来很像（都是数字0-9），但
  在其他分类任务里区别更明显，比如鸢尾花数据集：
  target        # [0, 0, 1, 2, 1, ...]
  (数字编码)
  target_names  # ['setosa', 'versicolor',
  'virginica']  (真实名称)

    
    """


def test3():
    digits = datasets.load_digits()
    #加载训练数据
    clf = svm.SVC(gamma=0.001, C=100.)
    """
    svm.SVC 参数详解         

  当前使用的参数                                                            
   
  C=100. — 正则化参数（惩罚系数）                                           
  - 控制对误分类的惩罚力度
  - C 越大：边界越严格，对训练集拟合越紧（可能过拟合）
  - C 越小：允许更多误分类，模型更简单（可能欠拟合）
  - 默认值：1.0

  gamma=0.001 — 核函数系数（用于 rbf/poly/sigmoid 核）
  - 定义单个训练样本的影响范围
  - gamma 越大：每个点影响范围越小，决策边界越复杂（过拟合风险）
  - gamma 越小：每个点影响范围越大，决策边界越平滑
  - 也可设为 'scale'（默认）或 'auto'

  ---
  其他常用训练参数

  ┌──────────────────────┬───────┬──────────────────────────────────────┐
  │         参数         │ 默认  │                 说明                 │
  │                      │  值   │                                      │
  ├──────────────────────┼───────┼──────────────────────────────────────┤
  │ kernel               │ 'rbf' │ 核函数：'linear'、'poly'、'rbf'、'si │
  │                      │       │ gmoid'                               │
  ├──────────────────────┼───────┼──────────────────────────────────────┤
  │ degree               │ 3     │ 多项式核（poly）的次数               │
  ├──────────────────────┼───────┼──────────────────────────────────────┤
  │ coef0                │ 0.0   │ 核函数的独立项，影响 poly/sigmoid    │
  ├──────────────────────┼───────┼──────────────────────────────────────┤
  │ probability          │ False │ 是否启用概率估计（启用后可用         │
  │                      │       │ predict_proba()）                    │
  ├──────────────────────┼───────┼──────────────────────────────────────┤
  │ class_weight         │ None  │ 类别权重，处理样本不均衡，可设       │
  │                      │       │ 'balanced'                           │
  ├──────────────────────┼───────┼──────────────────────────────────────┤
  │ max_iter             │ -1    │ 最大迭代次数，-1 表示不限制          │
  ├──────────────────────┼───────┼──────────────────────────────────────┤
  │ tol                  │ 1e-3  │ 迭代停止的容忍误差                   │
  ├──────────────────────┼───────┼──────────────────────────────────────┤
  │ random_state         │ None  │ 随机种子，用于结果复现               │
  ├──────────────────────┼───────┼──────────────────────────────────────┤
  │ decision_function_sh │ 'ovr' │ 多分类策略：'ovr'（一对多）或        │
  │ ape                  │       │ 'ovo'（一对一）                      │
  └──────────────────────┴───────┴──────────────────────────────────────┘

  ---
  选参建议

  # 线性可分数据
  svm.SVC(kernel='linear', C=1.0)

  # 非线性数据（常用）
  svm.SVC(kernel='rbf', C=10, gamma='scale')

  # 需要概率输出
  svm.SVC(probability=True)

  # 类别不均衡
  svm.SVC(class_weight='balanced')

  通常用 GridSearchCV 对 C 和 gamma 做网格搜索找最优组合。


    """
    #创建svm分类器
    clf.fit(digits.data, digits.target)
    #训练数据
    predict = clf.predict(digits.data[-1:])
    #预测结果
    print("预测结果:"+str(predict))
    print("实际结果:"+str(digits.target[-1]))
    plt.gray()
    plt.matshow(digits.images[-1])
    plt.show()


def test4():
    from sklearn.model_selection import train_test_split
    from sklearn import metrics

    digits = datasets.load_digits()

    # 1. 拆分训练集和测试集（80% 训练，20% 测试）
    X_train, X_test, y_train, y_test = train_test_split(
        digits.data, digits.target, test_size=0.2, random_state=42
    )

    # 2. 训练
    clf = svm.SVC(gamma=0.001, C=100.)
    clf.fit(X_train, y_train)

    # 3. 预测
    y_pred = clf.predict(X_test)

    # 4. 评估
    print('准确率:', metrics.accuracy_score(y_test, y_pred))
    print('详细报告:\n', metrics.classification_report(y_test, y_pred))

    # 5. 可视化：取前5张测试图看预测对不对
    fig, axes = plt.subplots(1, 5, figsize=(10, 3))
    for i, ax in enumerate(axes):
        ax.imshow(X_test[i].reshape(8, 8), cmap='gray')
        ax.set_title(f'真实:{y_test[i]}\n预测:{y_pred[i]}',
                     color='green' if y_test[i] == y_pred[i] else 'red')
        ax.axis('off')
    plt.show()


def test2():

    digits = datasets.load_digits()

    # 取出第0张图片
    index = 0
    for i in range(10):
        plt.imshow(digits.images[i], cmap='gray')
        plt.title(f'Label: {digits.target[i]}')
        plt.axis('off')
        plt.show()


if __name__ == '__main__':
    #test2()
    #test4()
    test3()
