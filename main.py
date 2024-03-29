# -*- coding: utf-8 -*-
"""n-gram-analysis-on-stock-data.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1DwtrlLQWN_LDHCaVjQsMZ_wZQEyO87ts
"""

from google.colab import drive
drive.mount('/content/drive')

import numpy as np
import pandas as pd 
from subprocess import check_output
print(check_output(["ls", "/content/drive/My Drive/ml"]).decode("utf8"))

# Commented out IPython magic to ensure Python compatibility.
import nltk
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns
from nltk.corpus import stopwords
from nltk import word_tokenize, ngrams
from sklearn import ensemble
from sklearn.model_selection import KFold
from sklearn.metrics import log_loss
import xgboost as xgb
nltk.download('stopwords')
eng_stopwords = set(stopwords.words('english') + ['>', '<', '#', ',', 'herf','\n\n\n', '\n\n',"\n"])
color = sns.color_palette()

# %matplotlib inline

pd.options.mode.chained_assignment = None

train_df = pd.read_csv('/content/drive/My Drive/ml/train.csv')
test_df = pd.read_csv('/content/drive/My Drive/ml/singleData.csv')
print(train_df.shape)
print(test_df.shape)

train_df.rename(columns ={'description_x':'question1','description_y':'question2','same_security':'is_similar'},inplace=True)

test_df.rename(columns={'description_x':'question1','description_y':'question2','same_security':'is_similar'},inplace=True)

def feature_extraction(row):
    que1 = str(row['question1'])
    que2 = str(row['question2'])
    out_list = []
    # get unigram features #
    unigrams_que1 = [word for word in que1.lower().split() if word not in eng_stopwords]
    unigrams_que2 = [word for word in que2.lower().split() if word not in eng_stopwords]
    common_unigrams_len = len(set(unigrams_que1).intersection(set(unigrams_que2)))
    common_unigrams_ratio = float(common_unigrams_len) / max(len(set(unigrams_que1).union(set(unigrams_que2))),1)
    out_list.extend([common_unigrams_len, common_unigrams_ratio])
    
    # get bigram features #
    bigrams_que1 = [i for i in ngrams(unigrams_que1, 2)]
    bigrams_que2 = [i for i in ngrams(unigrams_que2, 2)]
    common_bigrams_len = len(set(bigrams_que1).intersection(set(bigrams_que2)))
    common_bigrams_ratio = float(common_bigrams_len) / max(len(set(bigrams_que1).union(set(bigrams_que2))),1)
    out_list.extend([common_bigrams_len, common_bigrams_ratio])
    
    # get trigram features #
    unigrams_que_std1 = [i for i in unigrams_que1 if i]
    unigrams_que_std2 = [i for i in unigrams_que2 if i]
    trigrams_que1 = [i for i in ngrams(unigrams_que_std1, 3)]
    trigrams_que2 = []
    try:
      trigrams_que2 = [i for i in ngrams(unigrams_que_std2, 3)]
    except:
      print(1)
    common_trigrams_len = len(set(trigrams_que1).intersection(set(trigrams_que2)))
    common_trigrams_ratio = float(common_trigrams_len) / max(len(set(trigrams_que1).union(set(trigrams_que2))),1)
    out_list.extend([common_trigrams_len, common_trigrams_ratio])
    return out_list

def runXGB(train_X, train_y, test_X, test_y=None, feature_names=None, seed_val=0):
        params = {}
        params["objective"] = "binary:logistic"
        params['eval_metric'] = 'logloss'
        params["eta"] = 0.02
        params["subsample"] = 0.7
        params["min_child_weight"] = 1
        params["colsample_bytree"] = 0.7
        params["max_depth"] = 6
        params["silent"] = 1
        params["seed"] = seed_val
        num_rounds = 500 
        plst = list(params.items())
        xgtrain = xgb.DMatrix(train_X, label=train_y)

        if test_y is not None:
                xgtest = xgb.DMatrix(test_X, label=test_y)
                watchlist = [ (xgtrain,'train'), (xgtest, 'test') ]
                model = xgb.train(plst, xgtrain, num_rounds, watchlist, early_stopping_rounds=100, verbose_eval=10)
        else:
                xgtest = xgb.DMatrix(test_X)
                model = xgb.train(plst, xgtrain, num_rounds)
                
        pred_test_y = model.predict(xgtest)

        loss = 1
        if test_y is not None:
                loss = log_loss(test_y, pred_test_y)
                return pred_test_y, loss, model
        else:
            return pred_test_y, loss, modelv

test_X = np.vstack( np.array(test_df.apply(lambda row: feature_extraction(row), axis=1)) )

train_X = np.vstack( np.array(train_df.apply(lambda row: feature_extraction(row), axis=1)) ) 


train_y = np.array(train_df["is_similar"])

test_id = np.array(test_df["test_id"])

train_X_similar = train_X[train_y==1]
train_X_non_similar = train_X[train_y==0]

train_X = np.vstack([train_X_non_similar, train_X_similar, train_X_non_similar, train_X_non_similar])
train_y = np.array([0]*train_X_non_similar.shape[0] + [1]*train_X_similar.shape[0] + [0]*train_X_non_similar.shape[0] + [0]*train_X_non_similar.shape[0])
del train_X_similar
del train_X_non_similar
print("Mean target rate : ",train_y.mean())

kf = KFold(n_splits=10, shuffle=True, random_state=2021)
for dev_index, val_index in kf.split(range(train_X.shape[0])):
    dev_X, val_X = train_X[dev_index,:], train_X[val_index,:]
    dev_y, val_y = train_y[dev_index], train_y[val_index]
    print(dev_index)
    print(val_index)
    preds, lloss, model = runXGB(dev_X, dev_y, val_X, val_y)
    break

xgtest = xgb.DMatrix(test_X)
preds = model.predict(xgtest)

out_df = pd.DataFrame({"test_id":test_id, "is_similar":preds})
out_df.to_csv("/content/drive/My Drive/ml/singleData_ans.csv", index=False)

test_X