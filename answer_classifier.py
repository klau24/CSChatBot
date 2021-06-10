from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk import word_tokenize
import numpy as np
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk import pos_tag
from query_parser import QueryParser
import sql_queries


nltk.download("punkt")
nltk.download("wordnet")
nltk.download("averaged_perceptron_tagger")


def customTokenizer(doc):
    parser = QueryParser(doc)
    # tokens = []
    # ignore_tokens = [",", ".", ";", ":", '"', "``", "''", "`"]
    # words = [t for t in word_tokenize(doc) if t not in ignore_tokens]
    # for pair in pos_tag(words):  # to flatten the (word, tag) pairs
    #     tokens.append(pair[0])
    #     tokens.append(pair[1])
    return parser.features


def get_answer(q):
    tfidf = None
    vectorizer = None

    # TF-IDF vectorizer with a customTokenizer
    vectorizer = TfidfVectorizer(tokenizer=customTokenizer)
    # vectorizer = TfidfVectorizer()

    tfidf = vectorizer.fit_transform(df["questions"])

    parser = QueryParser(q)
    #print(parser.features)
    #print(parser.entities)
    test = vectorizer.transform([q])
    cosine = cosine_similarity(test, tfidf)
    cosine = pd.Series(cosine[0])
    return cosine, parser.features, parser.entities


def preprocess_queries(filename):
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


if __name__ == "__main__":
    print("Enter exit to exit.\n")

    df = preprocess_queries("./466S21-Queries/normalized.txt")

    q = input("Q> ")

    while q != "exit" or q != "Exit":
        answers, features, entities = get_answer(q)
        answers = answers.sort_values(ascending=False)
        print("Index\t\tScore\t\tResponses")
        print("----------------------------")
        for i in range(5):
            print(
                "{}\t\t{}\t\t{}".format(
                    answers.index[i],
                    answers.values[i],
                    df["responses"].iloc[answers.index[i]],
                )
            )
        response = df["responses"].iloc[answers.index[0]]
        query = sql_queries.Query(q, entities, response)
        queryOutput = query.queryDB()

        q = input("Q> ")
