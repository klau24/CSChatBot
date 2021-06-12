from __future__ import print_function
import nltk
import pymysql.cursors


class Query:
    def __init__(self, query, entities, answer):
        self.query = query
        self.entities = entities
        if "PROF" in self.entities.keys():
            self.entities["PROF"] = self.entities["PROF"].lower().replace("dr.", "").replace("dr . ", "").replace("professor", "").strip()
        elif "COURSE" in self.entities.keys():
            self.entities["COURSE"] = self.entities["COURSE"].replace("course", "").strip()
            course = self.entities["COURSE"].split()
            course[0] = course[0].upper()
            course = " ".join(course)
            self.entities["COURSE"] = course
        self.answer = answer
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

    def formatProf(self, i):
        oldLen = len(self.response)
        if '[' in i:   
            try:
                i = i.replace(".", "").replace("'", "'")
                if i == "[PROF]":
                    self.response += self.entities["FIRST"].capitalize() + " " + self.entities["LAST"].capitalize() + " "
                elif i == "[PROF]'s":
                    self.response += self.entities["FIRST"].capitalize() + " " + self.entities["LAST"].capitalize() + "'s" + " "
                elif i == "[ALIAS]":
                    self.response += self.entities["ALIAS"] + " "
                elif i == "[ALIAS]’s":
                    self.response += self.entities["ALIAS"] + "'s" + " "
                elif i == "[TITLE]":
                    self.response += self.entities["TITLE"] + " "
                elif i == "[PHONE]":
                    self.response += self.entities["PHONE"] + " "
                elif i == "[LOCATION]" and "PROF" in self.entities:
                    self.response += self.entities["OFFICE"] + " "
            except:
                return -2

        if len(self.response) > oldLen:
            return 1
        return -1

    def formatCourse(self, i):
        oldLen = len(self.response)
        if '[' in i:   
            try:
                i = i.replace(".", "")
                if i == "[COURSE]":
                    self.response += self.entities["CODE"] + " "
                elif i == "[SECTION]":
                    self.response += self.entities["SECTION"] + " "
                elif i == "[TYPE]":
                    self.response += self.entities["TYPE"] + " "
                elif i == "[DAYS]":
                    self.response += self.entities["DAYS"] + " "
                elif i == "[START]":
                    self.response += self.entities["START"] + " "
                elif i == "[END]":
                    self.response += self.entities["END"] + " "
                elif i == "[LOCATION]" and "COURSE" in self.entities:
                    self.response += self.entities["LOCATION"] + " "
            except:
                return -2

        if len(self.response) > oldLen:
            return 1
        return -1
        

    def formatOutput(self):
        self.answer = self.answer.split()
        count = 0
        for i in self.answer: 
            res = self.formatProf(i)
            if res == 1:
               count += 1
               continue
            if res == -2:
               break
            res = self.formatCourse(i)
            if res == -1:
                if count == 0:
                    self.response += i.capitalize() + " "
                else:
                    self.response += i.lower() + " "
            elif res == -2:
                break 
            count += 1
        if res == -2 or '[' in self.response:
            print("[Signal: Error][Issue with query][Query: '{0}'][Response: '{1}']".format(self.query, self.answer))
        elif res != -2:
            print(self.response)
            print("[Signal: Successful Query][Query: '{0}'][Response: '{1}']".format(self.query, self.response))


    def profAndCourseQuery(self):
        return

    def profQuery(self):
        output = None
        lastName = 0
        fullName = 0

        prof = self.entities["PROF"].split()
        #IMPLEMENT FIRST NAME AS WELL

        if len(prof) == 1: #last name
            lastName = 1
        else: #first and last
            fullName = 1

        connection = pymysql.connect(host='localhost', user='EKK', password='EKK98', database='EKK466S21', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
        with connection:
            if lastName == 1:
                with connection.cursor() as cursor:
                    sql = "SELECT * FROM Professors WHERE `last`=%s"
                    cursor.execute(sql, (prof))
                    output = cursor.fetchone()
            elif fullName == 1:
                with connection.cursor() as cursor:
                    sql = "SELECT * FROM Professors WHERE `first`=%s AND `last`=%s"
                    cursor.execute(sql, (prof[0], prof[1]))
                    output = cursor.fetchone()
        if output is not None:
            for i in output:
                key = i.upper()
                self.entities[key] = output[i]

    def courseQuery(self):
        course = self.entities["COURSE"]
        connection = pymysql.connect(host='localhost', user='EKK', password='EKK98', database='EKK466S21', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
        with connection:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM Courses WHERE code=%s"
                cursor.execute(sql, (course))
                output = cursor.fetchone()
        if output is not None:
            for i in output:
                key = i.upper()
                self.entities[key] = output[i]
