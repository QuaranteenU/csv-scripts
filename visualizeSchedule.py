import csv
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from tabulate import tabulate

with open('data/student schedule utc clustered.csv', encoding="utf-8") as file:
  data = [{k: v for k, v in row.items()} for row in csv.DictReader(file, skipinitialspace=True)]

x = [datetime.strptime(x['Start Time'], '%Y-%m-%d %I:%M:%S %p') for x in data]
y = [1 for x in data]
date_fmt = mdates.DateFormatter('%I:%M:%S')
fig, ax = plt.subplots()
plt.ylim(0, 2)
plt.xlim(x[0],x[-1])
ax.xaxis.set_major_formatter(date_fmt)
ax.scatter(x, y)
plt.grid(color='r', linestyle='-', linewidth=1)
#plt.show()

with open('data/MASTER RSVP with schools.csv', encoding="utf-8") as rsvpFile:
  rsvps = [{k: v for k, v in row.items()} for row in csv.DictReader(rsvpFile, skipinitialspace=True)]

emailToTZ = {}
for student in rsvps:
  try:
    emailToTZ[student['Email Address']] = int(student['Time Zone'])
  except ValueError:
    emailToTZ[student['Email Address']] = 0
  

pretty_order = [{'Name': item['Name'], 'Start Time': (datetime.strptime(item['Start Time'], '%Y-%m-%d %I:%M:%S %p') + timedelta(hours=emailToTZ[item['Name']])).strftime('%Y-%m-%d %I:%M:%S %p')} for item in data]
print("\nStudent Schedule localized")
print(tabulate(pretty_order, headers="keys"))

x = sorted([datetime.strptime(x['Start Time'], '%Y-%m-%d %I:%M:%S %p') for x in pretty_order])
y = [1 for x in data]
date_fmt = mdates.DateFormatter('%I:%M:%S %p')
fig, ax = plt.subplots()
plt.ylim(0, 2)
plt.xlim(x[0],x[-1])
ax.xaxis.set_major_formatter(date_fmt)
ax.scatter(x, y)
plt.grid(color='r', linestyle='-', linewidth=1)
plt.show()
