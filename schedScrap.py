import os, sys, requests
import pandas as pd
import numpy as np
import pymysql.cursors
import copy
from bs4 import BeautifulSoup

def courseInText(text):
   out = "CSC" in text or "CPE" in text or "DATA" in text or "LAES" in text or "EE" in text or "GSB" in text or "STAT" in text or "IME" in text
   return out


def getInfo(url, i):
   request = requests.get(url)
   soup = BeautifulSoup(request.text, "html.parser")

   sched_table = soup.find('table')

   inSection = False
   end = 0
   courses = []
   output = []
   course = []
   courses = {} #key is the index from prof list, value is the prof's courses
   profCount = 0
   departments = ["CENG-Computer Science & Software Engineering", "CSM-Statistics"]
   endDepartments = ["CENG-Computer Engineering", "CSM-Mathematics"]
   for row in sched_table.find_all('tr'):
      test = row.find('span')
      if test is not None:
         for wrapper in test:
            if wrapper == departments[i]:
               inSection = True
            elif wrapper == endDepartments[i]:
               end = 1 
      if end == 1:
         break
            
      if inSection is True:
         td = row.findAll('td')
         if len(td) > 0:
            prof = []
            count = 0
            dontAdd = 0
            addingCourses = 0
            for data in td:
               text = data.text.strip('\n')
               text = text.replace(u'\xa0', u'')
               inText = courseInText(text)
               if text == '':
                  continue
               if addingCourses == 1 and not inText:
                  course.append(text)
               #some redundant class data that we do not want to add
               if count == 0 and inText:
                  dontAdd = 1
                  break
               #if class data is not at the start of string, we know it belongs
               #to a prof so add it to courses dictionary
               elif count > 0 and inText and addingCourses == 0:
                  courses[profCount] = []
                  course.append(text)
                  addingCourses = 1
               elif inText and addingCourses == 1:
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
   #need to also return courses
   return output, courses

def addCourseToProf(count, output, courses):
   profAndCourses = []
   allCourses = []
   for i in range(len(output)):
      try:
         for course in courses[i]:
            temp = copy.deepcopy(output[i])
            temp.append(count)
            course[0] = course[0].replace(" (1)", "").replace(" /2", "").replace("SSD", "")
            course.insert(0, count)
            profAndCourses.append(temp)
            allCourses.append(course)
            count += 1
      except:
         pass
   return profAndCourses, allCourses, count


def addProfToDB(profCount, output):
   connection = pymysql.connect(host='localhost', user='EKK', password='EKK98', database='EKK466S21', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

   with connection:
      with connection.cursor() as cursor:
         for prof in output:
            name = prof[0].lower().split(' ')
            first = name[1]
            last = name[0].replace(',', '')
            sql = "INSERT INTO `Professors` (`id`, `first`, `last`, `alias`, `title`, `phone`, `office`, `courseID`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            if len(prof) == 6:
               cursor.execute(sql, (profCount, first, last, prof[1], prof[2], prof[3], prof[4], prof[5])) 
            elif len(prof) == 5: #[name, alias, title, phone, courseID]
               cursor.execute(sql, (profCount, first, last, prof[1], prof[2], prof[3], "NULL", prof[4])) 
            elif len(prof) == 4: #[name, alias, title, courseID]
               cursor.execute(sql, (profCount, first, last, prof[1], prof[2], "NULL", "NULL", prof[3])) 
            elif len(prof) == 3: #[name, alias, courseID]
               cursor.execute(sql, (profCount, first, last, prof[1], "NULL", "NULL", "NULL", prof[2])) 
            profCount += 1
      connection.commit()
   return profCount

def addCourseToDB(allCourses):
   connection = pymysql.connect(host='localhost', user='EKK', password='EKK98', database='EKK466S21', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

   with connection:
      with connection.cursor() as cursor:
         for course in allCourses:
            sql = "INSERT INTO `Courses` (`courseID`, `code`, `section`, `type`, `days`, `start`, `end`, `location`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            if len(course) == 8:
               cursor.execute(sql, (course[0], course[1], course[2], course[3], course[4], course[5], course[6], course[7])) 
            elif len(course) == 7:
               cursor.execute(sql, (course[0], course[1], course[2], course[3], course[4], course[5], course[6], "NULL")) 
            elif len(course) == 6:
               cursor.execute(sql, (course[0], course[1], course[2], course[3], course[4], course[5], "NULL", "NULL")) 
            elif len(course) == 5:
               cursor.execute(sql, (course[0], course[1], course[2], course[3], course[4], "NULL", "NULL", "NULL")) 
            elif len(course) == 4:
               cursor.execute(sql, (course[0], course[1], course[2], course[3], "NULL", "NULL", "NULL", "NULL")) 
            elif len(course) == 3:
               cursor.execute(sql, (course[0], course[1], course[2], "NULL", "NULL", "NULL", "NULL", "NULL")) 
      connection.commit()


if __name__ == "__main__":
   urls = ["https://schedules.calpoly.edu/depts_52-CENG_curr.htm", "https://schedules.calpoly.edu/depts_76-CSM_curr.htm"]
   count = 0
   profCount = 0
   for i in range(len(urls)):
      profs, courses = getInfo(urls[i], i)
      output, allCourses, count = addCourseToProf(count, profs, courses)
      addCourseToDB(allCourses)
      profCount = addProfToDB(profCount, output)
