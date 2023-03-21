import pandas as pd

import sql_queries
from query_classifier import QueryClassifier
from entity_classifier import EntityClassifier
import spacy
from nltk.metrics.distance  import edit_distance
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
        first_name = self.professors[self.professors["first"] == text]
        if len(first_name) > 0:
            return True
        return False

    def prof_check_first_s(self, text):
        if text[-1] == "s":
            first_name_no_s = self.professors[self.professors["first"] == text[:-1]]
            if len(first_name_no_s) > 0:
                return True
        return False

    def prof_check_last(self, text):
        last_name = self.professors[self.professors["last"] == text]
        if len(last_name) > 0:
            return True

        return False

    def prof_check_last_s(self, text):
        if text[-1] == "s":
            last_name_no_s = self.professors[self.professors["first"] == text[:-1]]
            if len(last_name_no_s) > 0:
                return True
        return False

    def class_check(self, text):
        class_num = self.courses[self.courses["CourseNumber"] == float(text)]
        if len(class_num) > 0:
            return True
        return False

    def spell_check(self, text):
        names = list(self.professors["first"]) + list(self.professors["last"])
        distances = [(x, edit_distance(text, x)) for x in names]
        min_val = distances[0][1]
        min_name = distances[0]
        for i in range(len(distances)):
            new_name = distances[i][0]
            new_val = distances[i][1]
            if new_val < min_val:
                min_val = new_val
                min_name = new_name
        return min_name, min_val


    # Given tokenized query, substitutes recognized entities with entity tags
    # Returns extracted entities and new query with tags
    def subst_entities(self, tokens):
        new_q = ""
        entities = {}
        for token in tokens:
            # print(token,token.tag_, token.pos_)
            # Proper noun was found
            # Checking for Class number and section
            if token.pos_ == "NUM":
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
                name, distance = self.spell_check(token.text.lower())
                # print(name, distance)
                # Check for first name
                if self.prof_check_first(token.text.lower()):
                    new_q += " [PROF]"
                    entities["PROF"] = {"first": token.text}
                # Check for last name
                elif self.prof_check_last(token.text.lower()):
                    if new_q.split()[-1] == "[PROF]":
                        entities["PROF"]["last"] = token.text
                    else:
                        new_q += " [PROF]"
                        entities["PROF"] = {"last": token.text}
                # It was similar to an existing name
                elif distance <= 1:
                    # Check if it was a first name
                    if self.prof_check_first(name):
                        new_q += " [PROF]"
                        entities["PROF"] = {"first": name}
                    # Check if it was a last name
                    elif self.prof_check_last(name):
                        # First name was also given
                        if new_q.split()[-1] == "[PROF]":
                            entities["PROF"]["last"] = name
                        else:
                            # Only last name was given
                            new_q += " [PROF]"
                            entities["PROF"] = {"last": name}
                # Not an entity
                else:
                    new_q += " " + token.text
        return entities, new_q

    # Given a query, prints responses from similar questions
    def get_sample_answers(self, q):
        entities, new_q = self.subst_entities(nlp(q))
        answer = self.queryClf.get_answer(new_q)
        return entities, answer

    def split_queries(self, q):
        entities = {}
        answers = []
        queries = q.split("and")
        for q in queries:
            new_entities, new_answer = self.get_sample_answers(q)
            entities.update(new_entities)
            answers += [new_answer]
        return entities, answers

def main():
    bot = ChatBot()
    print("Hello I am EKK, your Cal Poly Virtual Assistant. How can I help you today?")
    q = input("Q> ")
    while q != "exit" and q != "Exit":
        entities, answer = bot.split_queries(q)
        #entities, answer = bot.get_sample_answers(q)
        responses = []
        for a in answer:
            if a != -1:
                query = sql_queries.Query(q, entities, a)
                responses.append(query.queryDB())
        print(". ".join(responses)+".")
        q = input("Q> ")
    print("I'm glad I could help you :)")
    print("[Signal: End]")

if __name__ == "__main__":
    main()
