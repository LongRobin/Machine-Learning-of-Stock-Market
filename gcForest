from GCForest import gcForest
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pandas as pd

#loading the iris data
iris = load_iris()
X = iris.data
Y = iris.target

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.33)

gcf = gcForest(shape_1X=4, window = 2, tolerance=0.0)
gcf.fit(X_train, Y_train)

#predict 方法预测的是每一条样本的分类类别，结果 pred_X 是一个 [0,1,2...]的 array
pred_X = gcf.predict(X_test)
accuracy = accuracy_score(y_true=Y_test, y_pred=pred_X) #用 test 数据的真实类别和预测类别算准确率
print ('gcForest accuracy:{}'.format(accuracy))

#  predict_proba 方法预测的是每一条样本为 0，1,...类别的概率，结果是这样的：
# [[ 概率 1，概率 2，...],[ 概率 1，概率 2，...],...]的 DataFrame
# [:,1]表示取出序号为 1 的列，也就是预测类别为 1 的概率值,结果是一个数组
Y_predict_prod_test = gcf.predict_proba(X_test)[:, 1]
Y_predict_prod_train = gcf.predict_proba(X_train)[:, 1]
