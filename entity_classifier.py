import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB

df = pd.read_csv("entity_data.csv")
df = df.sample(frac=1).reset_index(drop=True)

train = df.iloc[:int(len(df)*0.8)]
test = df.iloc[int(len(df)*0.8):]

text_clf = Pipeline([('vect', CountVectorizer()),
  ('tfidf', TfidfTransformer()),
  ('clf', MultinomialNB())])

text_clf = text_clf.fit(train["Word"], train["Entity"])
predicted = text_clf.predict(test["Word"])
print("Accuracy:", np.mean(predicted == test["Entity"]))