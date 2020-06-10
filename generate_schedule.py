import csv
import bisect
import itertools
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from operator import itemgetter
from functools import cmp_to_key
from datetime import datetime, timedelta
from tabulate import tabulate
from functools import total_ordering
from collections import defaultdict

PRINT_TABULATE = False
SHOW_VIS = True

# from https://stackoverflow.com/a/1144405/3325942
def cmp(x, y):
    return (x > y) - (x < y)


def multikeysort(items, columns):
    comparers = [
        (
            (itemgetter(col[1:].strip()), -1)
            if col.startswith("-")
            else (itemgetter(col.strip()), 1)
        )
        for col in columns
    ]

    def comparer(left, right):
        comparer_iter = (cmp(fn(left), fn(right)) * mult for fn, mult in comparers)
        return next((result for result in comparer_iter if result), 0)

    return sorted(items, key=cmp_to_key(comparer))


# load data then sort by descending timezone and ascending school within timezone
filename = input("Enter timezones filename (default: school timezones.csv): ") or "school timezones.csv"
with open("data/{}".format(filename), encoding="utf-8") as schoolTimezonesFile:
    data = [
        {k: v if k == "School" else float(v) for k, v in row.items()}
        for row in csv.DictReader(schoolTimezonesFile, skipinitialspace=True)
    ]
data = multikeysort(data, ["-Average Timezone", "School"])
# print(tabulate(data, headers="keys"))

# custom object so we can sort/hash events
@total_ordering
class Event(object):
    def __init__(self, school, startTime, length, timezone):
        self.school = school
        self.startTime = startTime
        self.length = length
        self.timezone = timezone

    def __hash__(self):
        return hash(self.startTime.strftime("%Y-%m-%d %I:%M:%S %p"))

    def __lt__(self, other):
        return self.startTime < other.startTime

    def __eq__(self, other):
        return self.startTime == other.startTime


order = []
cur_tz = 24
cur_time = datetime.strptime(
    "2020-05-20 02:00PM", "%Y-%m-%d %I:%M%p"
)  # MAKE THE DATA HERE CONFIGURABLE
for item in data:
    if item["Average Timezone"] != cur_tz:
        cur_tz = item["Average Timezone"]
        reset_time = datetime.strptime(
            "2020-05-22 02:00PM", "%Y-%m-%d %I:%M%p"
        )  # MAKE THE DATA HERE CONFIGURABLE
        cur_time = cur_time if reset_time < cur_time else reset_time

    order_time = cur_time - timedelta(hours=cur_tz)
    event = Event(item["School"], order_time, item["Seconds"], item["Average Timezone"])
    bisect.insort(order, event)
    cur_time = cur_time + timedelta(seconds=item["Seconds"])

# print school start times in UTC
pretty_order = [
    {
        "School": item.school,
        "Start Time": item.startTime.strftime("%Y-%m-%d %I:%M:%S %p"),
    }
    for item in order
]
if PRINT_TABULATE:
    print("Schedule UTC")
    print(tabulate(pretty_order, headers="keys"))

# print school start times in local timezone
pretty_order = [
    {
        "School": item.school,
        "Start Time": (item.startTime + timedelta(hours=item.timezone)).strftime(
            "%Y-%m-%d %I:%M:%S %p"
        ),
    }
    for item in order
]
if PRINT_TABULATE:
    print("\nSchedule localized")
    print(tabulate(pretty_order, headers="keys"))

# check for conflicts
haveConflicts = len(order) != len(set(order))
print("\n--> School Start Time Conflicts?", haveConflicts)
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

# now to order students
filename = input("Enter contacts filename (default: contacts.csv): ") or "contacts.csv"
with open("data/{}".format(filename), encoding="utf-8") as rsvpFile:
    rsvps = [
        {k: v for k, v in row.items()}
        for row in csv.DictReader(rsvpFile, skipinitialspace=True)
    ]
emails = [x["Email Address"] for x in rsvps]

schoolToTimeMap = {}
for item in order:
    schoolToTimeMap[item.school] = item.startTime

schoolToStudentMap = defaultdict(list)
for student in rsvps:
    school = "Unknown" if student["Your school"] == "" else student["Your school"]
    schoolToStudentMap[school].append(
        {
            "name": student["Your Full Name"],
            "email": student["Email Address"],
            "timezone": student["Time Zone"],
        }
    )

# custom object so we can sort/hash students
@total_ordering
class StudentTime(object):
    def __init__(self, name, email, startTime, timezone, school):
        self.name = name
        self.email = email
        self.startTime = startTime
        self.timezone = timezone
        self.school = school

    def __hash__(self):
        return hash(self.startTime.strftime("%Y-%m-%d %I:%M:%S %p"))

    def __lt__(self, other):
        return self.startTime < other.startTime

    def __eq__(self, other):
        return self.startTime == other.startTime


student_order = []
for school in order:
    students = sorted(schoolToStudentMap[school.school], key=lambda i: i["name"])
    cur_time = schoolToTimeMap[school.school]
    for student in students:
        try:
            studentTz = int(student["timezone"])
        except ValueError:
            studentTz = (
                school.timezone
            )  # if student doesn't have a timezone, use school timezone to approx
        bisect.insort(
            student_order,
            StudentTime(
                student["name"], student["email"], cur_time, studentTz, school.school
            ),
        )
        cur_time = cur_time + timedelta(seconds=30)

# check for conflicts
haveConflicts = len(student_order) != len(set(student_order))
print("\n--> Student Start Time Conflicts?", haveConflicts)
if haveConflicts:
    seen = {}
    dupes = []
    for x in student_order:
        if x not in seen:
            seen[x] = 1
        else:
            if seen[x] == 1:
                dupes.append(x)
            seen[x] += 1

    print(dupes)

pretty_order = [
    {
        "Name": item.name,
        "Email": item.email,
        "School": item.school,
        "Time Zone": item.timezone,
        "Start Time": item.startTime.strftime("%Y-%m-%d %I:%M:%S %p"),
    }
    for item in student_order
]
if PRINT_TABULATE:
    print_order = [
        {"Name": item["Name"], "Start Time": item["Start Time"]}
        for item in pretty_order
    ]
    print("\nStudent Schedule UTC")
    print(tabulate(print_order, headers="keys"))

# save utc student schedule
filename = input("Enter student schedule filename (default: student schedule utc.csv): ") or "student schedule utc.csv"
with open(
    "data/{}".format(filename), "w", encoding="utf-8", newline=""
) as studentScheduleFile:
    csvFields = list(pretty_order[0].keys())
    writer = csv.DictWriter(studentScheduleFile, fieldnames=csvFields)
    writer.writeheader()
    writer.writerows(pretty_order)
    print("\n--> Saved student schedule utc.csv!")

pretty_order = [
    {
        "Name": item.name,
        "Start Time": (item.startTime + timedelta(hours=item.timezone)).strftime(
            "%Y-%m-%d %I:%M:%S %p"
        ),
    }
    for item in student_order
]
if PRINT_TABULATE:
    print("\nStudent Schedule localized")
    print(tabulate(pretty_order, headers="keys"))

print("\n--> Missing students?", len(student_order) != len(emails))
if len(student_order) != len(emails):
    ordered_emails = [x.email for x in student_order]
    missing = [x for x in emails if x not in ordered_emails]
    print(missing)

if SHOW_VIS:
    # visualize
    x = [x.startTime for x in student_order]
    y = [1 for x in student_order]
    date_fmt = mdates.DateFormatter("%I:%M:%S")
    fig, ax = plt.subplots()
    plt.title("Student Schedule UTC")
    plt.ylim(0, 2)
    plt.xlim(x[0], x[-1])
    ax.xaxis.set_major_formatter(date_fmt)
    ax.scatter(x, y)
    plt.grid(color="r", linestyle="-", linewidth=1)
    plt.show()
