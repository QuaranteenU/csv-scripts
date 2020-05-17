import csv
from operator import itemgetter as i
from functools import cmp_to_key
from datetime import datetime, timedelta
from tabulate import tabulate

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
    ((i(col[1:].strip()), -1) if col.startswith('-') else (i(col.strip()), 1))
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

order = []
cur_tz = 24
cur_time = None
for item in data:
  if item['Average Timezone'] != cur_tz:
    cur_tz = item['Average Timezone']
    cur_time = datetime.strptime('2020-05-22 02:00PM', '%Y-%m-%d %I:%M%p')

  order_time = cur_time - timedelta(hours=cur_tz)
  order.append({
    'School': item['School'],
    'Start Time': order_time
  })
  cur_time = cur_time + timedelta(seconds=item['Seconds'])

order = multikeysort(order, ['Start Time'])
pretty_order = [{'School': item['School'], 'Start Time': item['Start Time'].strftime('%Y-%m-%d %I:%M:%S %p')} for item in order]
print(tabulate(pretty_order, headers="keys"))