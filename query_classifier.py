from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import pandas as pd

class QueryClassifier:
  def __init__(self):
    self.data = self.preprocess_queries("./466S21-Queries/normalized.txt")
    self.vectorizer = TfidfVectorizer()
    self.tfidf = self.vectorizer.fit_transform(self.data["questions"])

  def get_answer(self, q):
    test = self.vectorizer.transform([q])
    cosine = cosine_similarity(test, self.tfidf)
    answers = pd.Series(cosine[0]).sort_values(ascending=False)
    print("Index\t\tScore\t\tResponses")
    print("----------------------------")
    for i in range(5):
        print(
            "{}\t\t{}\t\t{}".format(
                answers.index[i],
                answers.values[i],
                self.data["responses"].iloc[answers.index[i]],
            )
        )
    if answers.values[0] < .50:
       print("[Signal: Unknown Query][Query: '{0}']".format(q.strip()))
       return -1
    return self.data["responses"].iloc[answers.index[0]]


  def preprocess_queries(self, filename):
    data = None
    with open(filename, "r") as f:
        data = f.readlines()

    questions = []
    responses = []
    for i in range(len(data)):
        line = data[i].split("|")
        if len(line) == 3:
            questions.append(line[1].strip())
            responses.append(line[2].strip())
        elif len(line) == 2:
            line = line[1].split("?")
            if len(line) == 2:
                questions.append(line[0].strip())
                responses.append(line[1].strip())
    return pd.DataFrame({"questions": questions, "responses": responses})
