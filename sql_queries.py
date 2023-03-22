from __future__ import print_function
import nltk
import string
import pymysql.cursors


class Query:
    def __init__(self, query, entities, answer):
        self.connection = pymysql.connect(host='dev2020.chzg5zpujwmo.us-west-2.rds.amazonaws.com', user='iotdev', password='iot985', database='iot_test', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
        self.query = query.lower().split()
        self.entities = entities
        self.answer = answer
        self.answerEntityMap = {'LOCATION': 'OFFICE', 'CP-EMAIL': 'ALIAS', 'FIRSTNAME': 'FIRST', 'LASTNAME': 'LAST'}
        self.response = []

    def queryDB(self):
        keys = list(self.entities.keys())
        #print(self.query)
        #print(self.query, self.entities, self.answer)
        if ("PROF" in keys and "COURSE" in keys) or ("who" in self.query and "COURSE" in keys):
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
                return string.capwords(self.entities[key]['first'] + " " + self.entities[key]['last'])
            elif key == "COURSE":
                return self.entities[key]['code']
        return self.entities[key]
        
    def formatOutput(self):
        self.answer = self.answer.split()
        print(self.entities)
        for word in self.answer:
            # its a variable
            if '[' in word and ']' in word:
                answerVar = word[word.find("[")+1: word.find("]")]
                try:
                    self.response.append(self.unpackDict(answerVar))
                except:
                    try:
                        self.response.append(self.entities[self.answerEntityMap[answerVar]])
                    except:
                        print("Issue with query or I do not have this information.")
                        #print("[Signal: Error][Issue with query][Query: '{0}'][Response: '{1}']".format(self.query, self.answer))
                        return -1
            else:
                self.response.append(word)

        #print("[Signal: Successful Query][Query: '{0}'][Response: '{1}']".format(self.query, self.response))
        if "NULL" in self.response:
            print("I do not have that information in the database.")
            return -1
        return " ".join(self.response)
                
    def profAndCourseQuery(self):
        output = None
        query = "SELECT * from Professors INNER JOIN Courses on Professors.courseID = Courses.courseID WHERE "
        conditions = []

        with self.connection:
            if "PROF" in self.entities:
                if "first" in self.entities['PROF']:
                    conditions.append(f"first='{self.entities['PROF']['first']}'")
                if "last" in self.entities['PROF']:
                    conditions.append(f"last='{self.entities['PROF']['last']}'")
            if "COURSE" in self.entities:
                if "code" in self.entities["COURSE"]:
                    code = self.entities["COURSE"]["code"]
                    conditions.append(f"code LIKE '%{code}%'")
                if "section" in self.entities["COURSE"]:
                    section = self.entities["COURSE"]["section"]
                    conditions.append(f"section={section}")
            query += " AND ".join(conditions)
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                output = cursor.fetchone()
        #print(query)
        if output is not None:
            for i in output:
                key = i.upper()
                self.entities[key] = output[i]
            self.entities['PROF'] = {}
            self.entities['PROF']['last'] = self.entities['LAST']
            self.entities['PROF']['first'] = self.entities['FIRST']
            self.entities['COURSE'] = {}
            self.entities["COURSE"]['code'] = self.entities['CODE']

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
            self.entities['PROF']['last'] = self.entities['LAST']
            self.entities['PROF']['first'] = self.entities['FIRST']
            profKeys = list(self.entities['PROF'].keys())
            profKeys.sort()
            self.entities['PROF'] = {i: self.entities['PROF'][i] for i in profKeys}


    def courseQuery(self):
        query = "SELECT * FROM Courses WHERE "
        conditions = []
        with self.connection:
            if "code" in self.entities["COURSE"]:
                code = self.entities["COURSE"]["code"]
                conditions.append(f"code LIKE '%{code}%'")
            if "section" in self.entities["COURSE"]:
                section = self.entities["COURSE"]["section"]
                conditions.append(f"section={section}")
            if "type" in self.entities["COURSE"]:
                type = self.entities["COURSE"]["type"]
                conditions.append(f"type={type}")
            if "days" in self.entities["COURSE"]:
                days = self.entities["COURSE"]["days"]
                conditions.append(f"days={days}")
            if "start" in self.entities["COURSE"]:
                start = self.entities["COURSE"]["start"]
                conditions.append(f"start={start}")
            if "end" in self.entities["COURSE"]:
                end = self.entities["COURSE"]["end"]
                conditions.append(f"end={end}")
            if "location" in self.entities["COURSE"]:
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
            self.entities["COURSE"]['code'] = self.entities['CODE']
