from sklearn import svm
from sklearn.model_selection import train_test_split
import numpy
import json
from joblib import dump


# Citing scipy-lectures example: https://scipy-lectures.org/packages/scikit-learn/index.html

absent_data = []
present_data = []
with open('person_absent.json', 'r') as f:
    absent_data = json.load(f)

with open('person_absent_2.json', 'r') as f:
    absent_data += json.load(f)

with open('person_absent_3.json', 'r') as f:
    absent_data += json.load(f)    

with open('person_absent_4.json', 'r') as f:
    absent_data += json.load(f)    

with open('person_present.json', 'r') as f:
    present_data = json.load(f)

with open('person_present_2.json', 'r') as f:
    present_data += json.load(f)

target_data = ([0] * len(absent_data)) + ([1] * len(present_data))
data = absent_data + present_data

X_train, X_test, y_train, y_test = train_test_split(numpy.asarray(data), numpy.asarray(target_data))

clf = svm.SVC(gamma=0.001, C=100.)
clf.fit(X_train, y_train)


dump(clf, 'personClassifier.joblib')
# use the model to predict the labels of the test data
predicted = clf.predict(X_test)
expected = y_test

print(predicted)
print(expected)