from __future__ import print_function
import nltk
import string
import pymysql.cursors


class Query:
    def __init__(self, query, entities, answer):
        self.connection = pymysql.connect(host='dev2020.chzg5zpujwmo.us-west-2.rds.amazonaws.com', user='iotdev', password='iot985', database='iot_test', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
        self.query = query
        self.entities = entities
        self.answer = answer
        self.answerEntityMap = {'LOCATION': 'OFFICE', 'CP-EMAIL': 'ALIAS', 'FIRSTNAME': 'FIRST', 'LASTNAME': 'LAST'}
        self.response = []
        print(self.query, self.entities, self.answer)

    def queryDB(self):
        keys = list(self.entities.keys())
        # print("Keys:", keys)
        if "PROF" in keys and "COURSE" in keys:
            self.profAndCourseQuery()
        elif "PROF" in keys and "COURSE" not in keys:
            self.profQuery()
        elif "PROF" not in keys and "COURSE" in keys:
            self.courseQuery()

        return self.formatOutput()

    def unpackDict(self, key):
        res = []
        if isinstance(self.entities[key], dict):
            for _, v in self.entities[key].items():
                res.append(v)
            if key == "PROF":
            #     res[-1] += "'s"
                return string.capwords(" ".join(res))
            return " ".join(res)
        return self.entities[key]
        
    def formatOutput(self):
        self.answer = self.answer.split()
        for word in self.answer:
            # its a variable
            if '[' in word and ']' in word:
                answerVar = word[word.find("[")+1: word.find("]")]
                try:
                    self.response.append(self.unpackDict(answerVar))
                    if "EMAIL" in answerVar or "ALIAS" in answerVar:
                        self.response[-1] += "@calpoly.edu"
                except:
                    try:
                        self.response.append(self.entities[self.answerEntityMap[answerVar]])
                        if "EMAIL" in answerVar or "ALIAS" in answerVar:
                            self.response[-1] += "@calpoly.edu"
                    except:
                        print("[Signal: Error][Issue with query][Query: '{0}'][Response: '{1}']".format(self.query, self.answer))
                        return
            else:
                self.response.append(word)

        #print("[Signal: Successful Query][Query: '{0}'][Response: '{1}']".format(self.query, self.response))
        return " ".join(self.response)
                
    def profAndCourseQuery(self):
        return

    def profQuery(self):
        output = None
        query = "SELECT * FROM Professors WHERE "
        conditions = []

        with self.connection:
            if "first" in self.entities['PROF']:
                conditions.append(f"first='{self.entities['PROF']['first']}'")
            if "last" in self.entities['PROF']:
                conditions.append(f"last='{self.entities['PROF']['last']}'")
            query += " AND ".join(conditions)
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                output = cursor.fetchone()

        if output is not None:
            for i in output:
                key = i.upper()
                self.entities[key] = output[i]

    def courseQuery(self):
        query = "SELECT * FROM Courses WHERE "
        conditions = []

        with self.connection:
            if self.entities["COURSE"]["code"]:
                code = self.entities["COURSE"]["code"]
                conditions.append(f"code={code}")
            if self.entities["COURSE"]["section"]:
                section = self.entities["COURSE"]["section"]
                conditions.append(f"section={section}")
            if self.entities["COURSE"]["type"]:
                type = self.entities["COURSE"]["type"]
                conditions.append(f"type={type}")
            if self.entities["COURSE"]["days"]:
                days = self.entities["COURSE"]["days"]
                conditions.append(f"days={days}")
            if self.entities["COURSE"]["start"]:
                start = self.entities["COURSE"]["start"]
                conditions.append(f"start={start}")
            if self.entities["COURSE"]["end"]:
                end = self.entities["COURSE"]["end"]
                conditions.append(f"end={end}")
            if self.entities["COURSE"]["location"]:
                location = self.entities["COURSE"]["location"]
                conditions.append(f"location={location}")
            query += " AND ".join(conditions)

            with self.connection.cursor() as cursor:
                cursor.execute(query)
                output = cursor.fetchone()

        if output is not None:
            for i in output:
                key = i.upper()
                self.entities[key] = output[i]
