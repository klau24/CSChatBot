from __future__ import print_function
import nltk
import pymysql.cursors

class Query:
   def __init__(self, q, varDict, response):
      text = nltk.word_tokenize(q)
      wordsTagged = nltk.pos_tag(text)
      q = q.split(" ")
      self.nouns = [i[0] for i in wordsTagged if i[1] == 'NN' and i[0] not in varDict['PROF']]
      self.q = q
      self.varDict = varDict
      self.response = response.split()

   def queryDB(self):
      output = None
      #print("query: ", self.q)
      #print("nouns in q: ", self.nouns)
      #print("varDict: ", self.varDict)
      if len(self.varDict['PROF']) > 0 and len(self.varDict['COURSE']) > 0:
         self.profAndCourseQuery()
      elif len(self.varDict['PROF']) > 0 and len(self.varDict['COURSE']) == 0:
         self.profQuery()
      elif len(self.varDict['PROF']) == 0 and len(self.varDict['COURSE']) > 0:
         self.courseQuery()

      #print(self.varDict)
      output = self.formatOutput()
      return output

   def formatOutput(self):
      print(self.varDict)
      for i in self.response:
         if '[' in i:
            try:
               if i == "[PROF]":
                  print(self.varDict["FIRST"].capitalize() + " " + self.varDict["LAST"].capitalize(), end=" ")
               elif i == "[PROF]’s":
                  print(self.varDict["FIRST"].capitalize() + " " + self.varDict["LAST"].capitalize() + "'s", end=" ")
               elif i == "[ALIAS]":
                  print(self.varDict["ALIAS"], end=" ")
               elif i == "[ALIAS]’s":
                  print(self.varDict["ALIAS"] + "'s", end=" ")
               elif i == "[TITLE]":
                  print(self.varDict["TITLE"], end=" ")
               elif i == "[PHONE]":
                  print(self.varDict["PHONE"], end=" ")
               elif i == "[LOCATION]":
                  print(self.varDict["OFFICE"], end=" ")
            except:
               print("error when printing response")
         else:
            print(i, end=" ")
      print('\n')

   def profAndCourseQuery(self):
      #print("this is a prof and course query")
      return

   def profQuery(self):
      output = None
      lastName = 0
      fullName = 0
      if len(self.varDict['PROF']) == 1: #last name
         prof = self.varDict['PROF'][0].lower().strip()
         lastName = 1
      else: #first and last
         prof = self.varDict['PROF'][0] + " " + self.varDict['PROF'][1]
         prof = prof.lower().strip().split()
         fullName = 1
      #create permutations of the nouns?

      #sql query
      #print("prof:", prof)
      #if len(self.nouns) > 0:
         #print("noun:", self.nouns[0])
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
            self.varDict[key] = output[i]

   def courseQuery(self):
      print("this is a course query")
      return
