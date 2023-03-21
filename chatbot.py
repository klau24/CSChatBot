import pandas as pd

import sql_queries
from query_classifier import QueryClassifier
from entity_classifier import EntityClassifier
import spacy
from nltk.metrics.distance  import edit_distance
import pandas
import requests

nlp = spacy.load("en_core_web_sm")


class ChatBot:
    def __init__(self):
        self.entityClf = EntityClassifier()
        self.queryClf = QueryClassifier()
        self.professors = pd.read_csv("prof_name.csv")
        self.courses = pd.read_csv("courses.csv")

    # Given a name Entity, if it is misspelled, return the correction, otherwise return the original text
    def spellCheck(self, text):
        api_key = "c4479fb57ebf4c9c9e872cf972e943f8"
        endpoint = "https://api.bing.microsoft.com/v7.0/spellcheck"
        data = {'text': text}
        params = {'mkt':'en-us', 'mode':'spell'}
        headers = {'Ocp-Apim-Subscription-Key': api_key}
        response = requests.post(endpoint, headers=headers, params=params, data=data)
        json_response = response.json()
        print(json_response)
        if json_response["flaggedTokens"]:
            correction = json_response["flaggedTokens"][0]["suggestions"][0]["suggestion"]
            return correction[0].upper() + correction[1:]
        else:
            return text
    
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
            last_name_no_s = self.professors[self.professors["last"] == text[:-1]]
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
            #print(token,token.tag_, token.pos_)
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
                if token.pos_ == "PROPN":
                    spell_check_word = self.spellCheck(token.text.capitalize()).lower()
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
                # Check if an extra s was added to the first name
                elif self.prof_check_first_s(token.text.lower()):
                    new_q += " [PROF]"
                    entities["PROF"] = {"first": token.text[:-1]}
                # Check if an extra s was added to the last name
                elif self.prof_check_last_s(token.text.lower()):
                    #print("Entered last s ")
                    if new_q.split()[-1] == "[PROF]":
                        entities["PROF"]["last"] = token.text[:-1]
                    else:
                        new_q += " [PROF]"
                        entities["PROF"] = {"last": token.text[:-1]}
                # Check if it was a misspelled first name
                elif token.pos_ == "PROPN" and self.prof_check_first(spell_check_word):
                    new_q += " [PROF]"
                    entities["PROF"] = {"first": spell_check_word}
                # Check if it was a misspelled last name
                elif token.pos_ == "PROPN" and self.prof_check_last(spell_check_word):
                    if new_q.split()[-1] == "[PROF]":
                        entities["PROF"]["last"] = spell_check_word
                    else:
                        new_q += " [PROF]"
                        entities["PROF"] = {"last": spell_check_word}
                # Token is not an entity
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
        queries = q.split(" and ")
        for q in queries:
            new_entities, new_answer = self.get_sample_answers(q)
            entities.update(new_entities)
            answers += [new_answer]
        # print("Entities:",entities)
        # print("Answers:", answers)
        return entities, answers

def getQueries(q, entities, answer):
    responses = []
    for a in answer:
        if a != -1:
            # print("Before SQL QUERY")
            query = sql_queries.Query(q, entities, a)
            # print("After SQL QUERY")
            query_res = query.queryDB()
            if query_res != -1:
                responses.append(query_res)
            else:
                return
    if len(responses) > 1:
        return ". ".join(responses)+"."
    else:
        return responses[0] + "."

def get_response(q, bot):
    entities, answer = bot.split_queries(q)
    # print("After split queries")
    response = getQueries(q, entities, answer)
    return response

def main():
    bot = ChatBot()
    print("Hello I am PolyChat, your Cal Poly Virtual Assistant. How can I help you today?")
    q = input("Q> ")
    while q != "exit" and q != "Exit":
        response = get_response(q, bot)
        print(response)
        q = input("Q> ")
    print("I'm glad I could help you :)")
    print("[Signal: End]")

if __name__ == "__main__":
    main()
