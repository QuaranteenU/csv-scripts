import csv
from operator import itemgetter
from functools import cmp_to_key
from datetime import datetime, timedelta
from tabulate import tabulate
import bisect
from functools import total_ordering
from collections import defaultdict
import itertools

def cmp(x, y):
  """
  Replacement for built-in function cmp that was removed in Python 3

  Compare the two objects x and y and return an integer according to
  the outcome. The return value is negative if x < y, zero if x == y
  and strictly positive if x > y.

  https://portingguide.readthedocs.io/en/latest/comparisons.html#the-cmp-function
  """

  return (x > y) - (x < y)

def multikeysort(items, columns):
  comparers = [
    ((itemgetter(col[1:].strip()), -1) if col.startswith('-') else (itemgetter(col.strip()), 1))
    for col in columns
  ]
  def comparer(left, right):
    comparer_iter = (
      cmp(fn(left), fn(right)) * mult
      for fn, mult in comparers
    )
    return next((result for result in comparer_iter if result), 0)
  return sorted(items, key=cmp_to_key(comparer))

with open('data/school timezones.csv', encoding="utf-8") as schoolTimezonesFile:
  data = [{k: v if k == "School" else float(v) for k, v in row.items()} for row in csv.DictReader(schoolTimezonesFile, skipinitialspace=True)]

# sort data by descending timezone and ascending school within timezone
data = multikeysort(data, ['-Average Timezone', 'School'])
#print(tabulate(data, headers="keys"))

@total_ordering
class Event(object):
  def __init__(self, school, startTime, length, timezone):
    self.school = school
    self.startTime = startTime
    self.length = length
    self.timezone = timezone

  def __hash__(self):
    return hash(self.startTime.strftime('%Y-%m-%d %I:%M:%S %p'))

  def __lt__(self, other):
    return self.startTime < other.startTime

  def __eq__(self, other):
    return self.startTime == other.startTime

order = []
cur_tz = 24
cur_time = datetime.strptime('2020-05-20 02:00PM', '%Y-%m-%d %I:%M%p')
for item in data:
  if item['Average Timezone'] != cur_tz:
    cur_tz = item['Average Timezone']
    reset_time = datetime.strptime('2020-05-22 02:00PM', '%Y-%m-%d %I:%M%p')
    cur_time = cur_time if reset_time < cur_time else reset_time

  order_time = cur_time - timedelta(hours=cur_tz)
  event = Event(item['School'], order_time, item['Seconds'], item['Average Timezone'])
  bisect.insort(order, event)
  cur_time = cur_time + timedelta(seconds=item['Seconds'])

pretty_order = [{'School': item.school, 'Start Time': item.startTime.strftime('%Y-%m-%d %I:%M:%S %p')} for item in order]
print("Schedule UTC")
print(tabulate(pretty_order, headers="keys"))

# print event times in local timezone
pretty_order = [{'School': item.school, 'Start Time': (item.startTime + timedelta(hours=item.timezone)).strftime('%Y-%m-%d %I:%M:%S %p')} for item in order]
print("\nSchedule localized")
print(tabulate(pretty_order, headers="keys"))

# check for conflicts
haveConflicts = len(order) != len(set(order))
print('\n--> Conflicts?', haveConflicts)
if haveConflicts:
  seen = {}
  dupes = []
  for x in order:
    if x not in seen:
      seen[x] = 1
    else:
      if seen[x] == 1:
        dupes.append(x)
      seen[x] += 1

  print(dupes)

schoolToTimeMap = {}
for item in order:
  schoolToTimeMap[item.school] = item.startTime

with open('data/MASTER RSVP with schools.csv', encoding="utf-8") as rsvpFile:
  rsvps = [{k: v for k, v in row.items()} for row in csv.DictReader(rsvpFile, skipinitialspace=True)]
emails = [x['Email Address'] for x in rsvps]

schoolToStudentMap = defaultdict(list)
for student in rsvps:
  school = 'Unknown' if student['School'] == '' else student['School']
  schoolToStudentMap[school].append(student['Email Address'])

@total_ordering
class StudentTime(object):
  def __init__(self, name, startTime, timezone):
    self.name = name
    self.startTime = startTime
    self.timezone = timezone

  def __hash__(self):
    return hash(self.startTime.strftime('%Y-%m-%d %I:%M:%S %p'))

  def __lt__(self, other):
    return self.startTime < other.startTime

  def __eq__(self, other):
    return self.startTime == other.startTime

student_order = []
for school in order:
  students = sorted(schoolToStudentMap[school.school])
  cur_time = schoolToTimeMap[school.school]
  for student in students:
    bisect.insort(student_order, StudentTime(student, cur_time, school.timezone))
    cur_time = cur_time + timedelta(seconds=30)

pretty_order = [{'Name': item.name, 'Start Time': item.startTime.strftime('%Y-%m-%d %I:%M:%S %p')} for item in student_order]
print("\nStudent Schedule UTC")
print(tabulate(pretty_order, headers="keys"))

pretty_order = [{'Name': item.name, 'Start Time': (item.startTime + timedelta(hours=item.timezone)).strftime('%Y-%m-%d %I:%M:%S %p')} for item in student_order]
print("\nStudent Schedule localized")
print(tabulate(pretty_order, headers="keys"))

print('\nOrdered Students: %s, Original Students: %s' % (len(student_order), len(emails)))
ordered_emails = [x.name for x in student_order]
missing = [x for x in emails if x not in ordered_emails]
print(missing)