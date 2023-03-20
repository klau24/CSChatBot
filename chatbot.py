import pandas as pd

import sql_queries
from query_classifier import QueryClassifier
from entity_classifier import EntityClassifier
import spacy
import pandas

nlp = spacy.load("en_core_web_sm")


class ChatBot:
    def __init__(self):
        self.entityClf = EntityClassifier()
        self.queryClf = QueryClassifier()
        self.professors = pd.read_csv("prof_name.csv")
        self.courses = pd.read_csv("courses.csv")

    # # Given a query, returns tokenized query with adjacent nouns grouped together
    # def group_tokens(self, q):
    #     doc = nlp(q)
    #     tokenized = []
    #     for token in doc:
    #         print(token,token.tag_, token.pos_)
    #         if token.pos_ == "PROPN" and len(tokenized) > 0  and tokenized[-1][1] == "PROPN":
    #             tokenized[-1][0] += " " + token.text
    #         else:
    #             tokenized.append([token.text, token.pos_])
    #         # try:
    #         #     if token.tag_[:2] in ["NN", "CD", "HY"] and tokenized[-1][1] == "NN":
    #         #         tokenized[-1][0] += " " + token.text
    #         #     elif token.tag_[:2] == "NN":
    #         #         tokenized.append([token.text, "NN"])
    #         #     else :
    #         #         tokenized.append([token.text, token.tag_])
    #         # except:
    #         #     print("[Signal: Error][Issue with query][Query: '{0}']".format(q))
    #         #     return -1
    #     return tokenized

    def prof_check_first(self, text):
        first_name = self.professors[self.professors["FirstName"] == text]
        if len(first_name) > 0:
            return True
        return False

    def prof_check_first_s(self, text):
        if text[-1] == "s":
            first_name_no_s = self.professors[self.professors["FirstName"] == text[:-1]]
            if len(first_name_no_s) > 0:
                return True
        return False

    def prof_check_last(self, text):
        last_name = self.professors[self.professors["LastName"] == text]
        if len(last_name) > 0:
            return True

        return False

    def prof_check_last_s(self, text):
        if text[-1] == "s":
            last_name_no_s = self.professors[self.professors["FirstName"] == text[:-1]]
            if len(last_name_no_s) > 0:
                return True
        return False

    def class_check(self, text):
        class_num = self.courses[self.courses["CourseNumber"] == float(text)]
        if len(class_num) > 0:
            return True
        return False

    # Given tokenized query, substitutes recognized entities with entity tags
    # Returns extracted entities and new query with tags
    def subst_entities(self, tokens):
        new_q = ""
        entities = {}
        for token in tokens:
            # print(token,token.tag_, token.pos_)
            # Proper noun was found
            if token.pos_ == "PROPN" or token.pos_ == "NOUN":
                # Check for first name
                if self.prof_check_first(token.text.lower()):
                    new_q += " [PROF]"
                    entities["PROF"] = {"FirstName": token.text}
                # Check for last name
                elif self.prof_check_last(token.text.lower()):
                    if new_q.split()[-1] == "[PROF]":
                        entities["PROF"]["LastName"] = token.text
                    else:
                        new_q += " [PROF]"
                        entities["PROF"] = {"LastName": token.text}
                # Check for extra s in first name
                elif self.prof_check_first_s(token.text.lower()):
                    new_q += " [PROF]"
                    entities["PROF"] = {"FirstName": token.text[:-1]}
                # Check for extra s in last name
                elif self.prof_check_last_s(token.text.lower()):
                    if new_q.split()[-1] == "[PROF]":
                        entities["PROF"]["LastName"] = token.text[:-1]
                    else:
                        new_q += " [PROF]"
                        entities["PROF"] = {"LastName": token.text[:-1]}
                # Not an entity
                else:
                    new_q += " " + token.text
            # Checking for Class number and section
            elif token.pos_ == "NUM":
                # Check if is a course
                if self.class_check(token.text):
                    new_q += " [COURSE]"
                    entities["COURSE"] = {"code": token.text}
                # Check if a section
                else:
                    new_q += " [SECTION]"
                    if "COURSE" in entities:
                        entities["COURSE"]["section"] = token.text
                    else:
                        entities["COURSE"] = {"section":token.text}
            else:
                new_q += " " + token.text
        return entities, new_q

    # Given a query, prints responses from similar questions
    def get_sample_answers(self, q):
        entities, new_q = self.subst_entities(nlp(q))
        answer = self.queryClf.get_answer(new_q)
        return entities, answer

def main():
    bot = ChatBot()
    print("Hello I am EKK, your Cal Poly Virtual Assistant. How can I help you today?")
    q = input("Q> ")
    while q != "exit" and q != "Exit":
        entities, answer = bot.get_sample_answers(q)
        # print("Entities:", entities)
        # print("Answer:", answer)
        if answer != -1:
            query = sql_queries.Query(q, entities, answer)
            query.queryDB()
        q = input("Q> ")
    print("I'm glad I could help you :)")
    print("[Signal: End]")

if __name__ == "__main__":
    main()
