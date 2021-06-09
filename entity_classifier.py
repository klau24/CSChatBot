import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB


class EntityClassifier:
    def __init__(self):
        df = pd.read_csv("entity_data.csv")

        # shuffle data
        df = df.sample(frac=1).reset_index(drop=True)

        self.train = df.iloc[: int(len(df) * 0.8)]
        self.test = df.iloc[int(len(df) * 0.8) :]

        print(len(df))
        print(len(self.train))
        print(len(self.test))

        self.clf = Pipeline(
            [
                ("vect", CountVectorizer()),
                ("tfidf", TfidfTransformer()),
                ("clf", MultinomialNB()),
            ]
        )
        # train on data
        self.clf = self.clf.fit(self.train["Word"], self.train["Entity"])

    def test_accuracy(self):
        predicted = self.clf.predict(self.test["Word"])
        print(predicted)
        print("Accuracy:", np.mean(predicted == self.test["Entity"]))


if __name__ == "__main__":
    e = EntityClassifier()
    e.test_accuracy()

    # print(e.clf.predict(["CSC 238", "Mike James", "Aaron",
    #       "Data Structures", "Introduction to Computer Science"]))
