import sys
import re
import spacy
from entity_classifier import EntityClassifier

# load spacy
nlp = spacy.load("en_core_web_sm")


class QueryParser:
    def __init__(self, question):
        self.features, self.entities = self.extract_features(question)

    def extract_bracketed_variables(self, string, entities):
        # takes a string
        # removes the bracketed variables while adding them to the entities dict
        # returns the remaining string

        # example match [PROF]'s
        matches = re.findall(f"(\[\w+])\S*", string)
        for match in matches:
            entities[match] = None

        # replace brackets with spaces
        no_var_string = re.sub(f"(\[\w+])\S*", "", string)
        # remove extra spaces between words
        no_var_string = " ".join(no_var_string.split())
        return no_var_string

    def identify_persons(self, doc, entities):
        # identifies names in the doc adding them to entities dictionary
        # returns the remaining tokens
        for token in doc:
            if token.ent_type_ == "PERSON":
                entities["PROF"].append(token.text)
        return [token for token in doc if token.ent_type_ != "PERSON"]

    def identify_courses(self, doc, entitites):
        remaining_tokens = []
        # identifies courses in the tokens adding them to entities dictionary
        for i in range(len(doc)):
            token = doc[i]
            # example course: CSC 466 or STAT 312
            if i > 0 and token.like_num and doc[i - 1].is_alpha:
                entitites["COURSE"].append(f"{doc[i-1].text} {token.text}")
                # pop last added token since that was the department name (CSC/STAT)
                remaining_tokens.pop()
            else:
                remaining_tokens.append(token)
        return remaining_tokens

    def extract_features(self, question, asked_by_user=True):
        # extracts features from each question
        # returns a list of features and a dictionary of entities

        features = []
        entities = {"PROF": [], "COURSE": []}

        # remove question mark
        question = re.sub(f"[?]", "", question)

        # extract bracketed variables
        no_var_string = self.extract_bracketed_variables(question, entities)

        # tokenize the remaining words
        doc = nlp(no_var_string)

        # for chunk in doc.noun_chunks:
        #     print(chunk.text)

        # extract entities from tokens if question is coming from the user
        if asked_by_user:
            doc = self.identify_persons(doc, entities)
            doc = self.identify_courses(doc, entities)

            # take the first word (often a question word (who, what, where, when, why, how, is, does))
        features.append(doc[0].text.lower())

        # remove stop words
        doc = [token for token in doc if not token.is_stop]

        # added variables to features
        features += [
            key
            for (key, value) in entities.items()
            if value is not None and len(value) > 0
        ]
        # add remaining "important" words to features
        features += [token.text for token in doc]
        # print(tokens)
        # print("Features", features)
        # print("Entities", entities)
        return (features, entities)


def retrieve_queries_from_file(filepath):
    # return an array of queries, ["EKK", <question>, <answer>]
    with open(filepath, "r") as f:
        lines = f.readlines()

    # pre-process each line
    queries = [line.strip().split("|") for line in lines]
    return queries


if __name__ == "__main__":
    args = sys.argv[1:]

    if len(args) != 1:
        sys.exit("usage: query_parser.py [filename]")

    queries = retrieve_queries_from_file(args[0])
    queries = [query for query in queries if len(query) == 3]

    for query in queries:
        _, question, answer = query
        QueryParser(question)
        # extract_features(question, False)

    with open("sample_questions.txt", "r") as f:
        lines = f.readlines()
    test_questions = [line.strip() for line in lines]

    print()
    for question in test_questions:
        QueryParser(question)
        # extract_features(question)
