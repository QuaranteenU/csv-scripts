import csv
from operator import itemgetter
from functools import cmp_to_key
from datetime import datetime, timedelta
from tabulate import tabulate
import bisect
from functools import total_ordering
from collections import defaultdict

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

with open('data/school timezones.csv') as f:
  data = [{k: v if k == "School" else float(v) for k, v in row.items()} for row in csv.DictReader(f, skipinitialspace=True)]

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
# first pass
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
print(tabulate(pretty_order, headers="keys"))
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