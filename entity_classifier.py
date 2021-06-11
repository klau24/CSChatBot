import pandas as pd
import numpy as np
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB


class EntityClassifier:
    def __init__(self):
        df = pd.read_csv("entity_data.csv").drop_duplicates(ignore_index=True)

        # shuffle data
        df = df.sample(frac=1).reset_index(drop=True)

        self.train = df.iloc[: int(len(df) * 0.8)]
        self.test = df.iloc[int(len(df) * 0.8) :]

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

    def predict(self, doc):
        # handles specific course codes
        COURSE_CODE_REGEX = f"((CSC|STAT) \d\d\d)"
        match = re.search(COURSE_CODE_REGEX, doc, re.IGNORECASE)
        if match and match[1]:
            return match[1], "COURSE"

        return doc, self.clf.predict([doc])[0]


if __name__ == "__main__":
    e = EntityClassifier()
    e.test_accuracy()

    # print(e.clf.predict(["CSC 238", "Mike James", "Aaron",
    #       "Data Structures", "Introduction to Computer Science"]))
