import os, sys, requests
import pandas as pd
import numpy as np
import pymysql.cursors
from bs4 import BeautifulSoup

url = "https://schedules.calpoly.edu/depts_52-CENG_curr.htm"
request = requests.get(url)
soup = BeautifulSoup(request.text, "html.parser")

sched_table = soup.find('table')

csSection = False
end = 0
courses = []
output = []
course = []
courses = {} #key is the index from prof list, value is the prof's courses
profCount = 0
for row in sched_table.find_all('tr'):
   test = row.find('span')
   if test is not None:
      for wrapper in test:
         if wrapper == "CENG-Computer Science & Software Engineering":
            csSection = True
         elif wrapper == "CENG-Computer Engineering":
            end = 1 
   if end == 1:
      break
         
   if csSection is True:
      td = row.findAll('td')
      if len(td) > 0:
         prof = []
         count = 0
         dontAdd = 0
         addingCourses = 0
         for data in td:
            text = data.text.strip('\n')
            text = text.replace(u'\xa0', u'')
            if text == '':
               continue
            if addingCourses == 1 and ("CSC" not in text and "CPE" not in text):
               course.append(text)
            #some redundant class data that we do not want to add
            if count == 0 and ("CSC" in text or "CPE" in text or "LAES" in text or "DATA" in text or "EE" in text):
               dontAdd = 1
               break
            #if class data is not at the start of string, we know it belongs
            #to a prof so add it to courses dictionary
            elif count > 0 and ("CSC" in text or "CPE" in text) and addingCourses == 0:
               courses[profCount] = []
               course.append(text)
               addingCourses = 1
            elif  ("CSC" in text or "CPE" in text) and addingCourses == 1:
               courses[profCount].append(course)
               course = []
               course.append(text)
            if addingCourses == 0:
               prof.append(text)
               count += 1
         #add the last class
         if len(course) > 0:
            courses[profCount].append(course)
            course = []
         if dontAdd == 0:
            output.append(prof)         
            profCount += 1

df = pd.DataFrame(output, columns=['lastName', 'firstName', 'title', 'phone', 'office'])

connection = pymysql.connect(host='localhost', user='EKK', password='EKK98', database='EKK466S21', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

with connection:
   with connection.cursor() as cursor:
      count = 0
      for prof in output:
         print(prof)
         sql = "INSERT INTO `Professors` (`id`, `name`, `alias`, `title`, `phone`, `office`) VALUES (%s, %s, %s, %s, %s, %s)"
         if len(prof) == 5:
            cursor.execute(sql, (count, prof[0], prof[1], prof[2], prof[3], prof[4])) 
         elif len(prof) == 3:
            cursor.execute(sql, (count, prof[0], prof[1], prof[2], "NULL", "NULL")) 
         elif len(prof) == 4:
            cursor.execute(sql, (count, prof[0], prof[1], prof[2], prof[3], "NULL")) 
         count += 1
   connection.commit()
