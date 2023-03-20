from __future__ import print_function
import nltk
import pymysql.cursors


class Query:
    def __init__(self, query, entities, answer):
        self.connection = pymysql.connect(host='dev2020.chzg5zpujwmo.us-west-2.rds.amazonaws.com', user='iotdev', password='iot985', database='iot_test', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
        self.query = query
        self.entities = entities
        self.answer = answer
        self.answerEntityMap = {}
        self.response = ""

    def queryDB(self):
        keys = list(self.entities.keys())
        if "PROF" in keys and "COURSE" in keys:
            self.profAndCourseQuery()
        elif "PROF" in keys and "COURSE" not in keys:
            self.profQuery()
        elif "PROF" not in keys and "COURSE" in keys:
            self.courseQuery()

        self.formatOutput()

    # def formatProf(self, i):
    #     oldLen = len(self.response)
    #     if '[' in i:   
    #         try:
    #             i = i.replace(".", "").replace("'", "'")
    #             if i == "[PROF]":
    #                 self.response += self.entities["FIRST"].capitalize() + " " + self.entities["LAST"].capitalize() + " "
    #             elif i == "[PROF]'s":
    #                 self.response += self.entities["FIRST"].capitalize() + " " + self.entities["LAST"].capitalize() + "'s" + " "
    #             elif "[ALIAS]" in i:
    #                 self.response += self.entities["ALIAS"] + " "
    #             elif i == "[ALIAS]’s":
    #                 self.response += self.entities["ALIAS"] + "'s" + " "
    #             elif i == "[TITLE]":
    #                 self.response += self.entities["TITLE"] + " "
    #             elif i == "[PHONE]":
    #                 self.response += self.entities["PHONE"] + " "
    #             elif i == "[LOCATION]" and "PROF" in self.entities:
    #                 self.response += self.entities["OFFICE"] + " "
    #         except:
    #             return -2

    #     if len(self.response) > oldLen:
    #         return 1
    #     return -1

    # def formatCourse(self, i):
    #     oldLen = len(self.response)
    #     if '[' in i:   
    #         try:
    #             i = i.replace(".", "")
    #             if i == "[COURSE]":
    #                 self.response += self.entities["CODE"] + " "
    #             elif i == "[SECTION]":
    #                 self.response += self.entities["SECTION"] + " "
    #             elif i == "[TYPE]":
    #                 self.response += self.entities["TYPE"] + " "
    #             elif i == "[DAYS]":
    #                 self.response += self.entities["DAYS"] + " "
    #             elif i == "[START]":
    #                 self.response += self.entities["START"] + " "
    #             elif i == "[END]":
    #                 self.response += self.entities["END"] + " "
    #             elif i == "[LOCATION]" and "COURSE" in self.entities:
    #                 self.response += self.entities["LOCATION"] + " "
    #         except:
    #             return -2

    #     if len(self.response) > oldLen:
    #         return 1
    #     return -1

    # def _OLD_formatOutput(self):
    #     self.answer = self.answer.split()
    #     count = 0
    #     for i in self.answer: 
    #         res = self.formatProf(i)
    #         if res == 1:
    #            count += 1
    #            continue
    #         if res == -2:
    #            break
    #         res = self.formatCourse(i)
    #         if res == -1:
    #             if count == 0:
    #                 self.response += i.capitalize() + " "
    #             else:
    #                 self.response += i.lower() + " "
    #         elif res == -2:
    #             break 
    #         count += 1
    #     if res == -2 or '[' in self.response:
    #         print("[Signal: Error][Issue with query][Query: '{0}'][Response: '{1}']".format(self.query, self.answer))
    #     elif res != -2:
    #         print(self.response)
    #         print("[Signal: Successful Query][Query: '{0}'][Response: '{1}']".format(self.query, self.response))

    def formatOutput(self):
        self.answer = self.answer.split()
        for word in self.answer:
            # its a variable
            if '[' in word and ']' in word:
                answerVar = word[word.find("[")+1: word.find("]")]
                try:
                    self.response += self.entities[answerVar]
                except:
                    try:
                        self.response += self.answerEntityMap[answerVar]
                    except:
                        print("[Signal: Error][Issue with query][Query: '{0}'][Response: '{1}']".format(self.query, self.answer))
            else:
                self.response += word
                
        print(self.response)
        print("[Signal: Successful Query][Query: '{0}'][Response: '{1}']".format(self.query, self.response))
                
    def profAndCourseQuery(self):
        return

    def profQuery(self):
        output = None
        query = "SELECT * FROM Professors WHERE "
        conditions = []

        with self.connection:
            if self.entities['first']:
                conditions.append(f"first={self.entities['first']}")
            if self.entities['last']:
                conditions.append(f"last={self.entities['last']}")
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
