import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from tabulate import tabulate

PRINT_TABULATE = False
SHOW_VIS = False

# load clustered schedule (make sure you go make that first in google sheets)
with open("data/student schedule utc clustered.csv", encoding="utf-8") as file:
    data = [
        {k: v for k, v in row.items()}
        for row in csv.DictReader(file, skipinitialspace=True)
    ]

if SHOW_VIS:
    x = [datetime.strptime(x["Start Time"], "%Y-%m-%d %I:%M:%S %p") for x in data]
    y = [1 for x in data]
    date_fmt = mdates.DateFormatter("%I:%M:%S")
    fig, ax = plt.subplots()
    plt.title("Student Schedule Clustered - UTC")
    plt.ylim(0, 2)
    plt.xlim(x[0], x[-1])
    ax.xaxis.set_major_formatter(date_fmt)
    ax.scatter(x, y)
    plt.grid(color="r", linestyle="-", linewidth=1)
    plt.show()

# load original RSVPs and make map keyed by email
with open("data/MASTER RSVP with schools.csv", encoding="utf-8") as rsvpFile:
    rsvps = [
        {k: v for k, v in row.items()}
        for row in csv.DictReader(rsvpFile, skipinitialspace=True)
    ]
emailToRow = {}
emailToTz = {}
for student in rsvps:
    emailToRow[student["Email Address"]] = student
    try:
        emailToTz[student["Email Address"]] = int(student["Time Zone"])
    except ValueError:
        print("%s has no tz" % (student["Your Full Name"]))

studentsWithTZ = [item for item in data if item["Email"] in emailToTz]
pretty_order = [
    {
        "Name": item["Name"],
        "Start Time": (
            datetime.strptime(item["Start Time"], "%Y-%m-%d %I:%M:%S %p")
            + timedelta(hours=emailToTz[item["Email"]])
        ).strftime("%Y-%m-%d %I:%M:%S %p"),
    }
    for item in studentsWithTZ
]
if PRINT_TABULATE:
    print("\nStudent Schedule localized")
    print(tabulate(pretty_order, headers="keys"))

if SHOW_VIS:
    x = sorted(
        [
            datetime.strptime(x["Start Time"], "%Y-%m-%d %I:%M:%S %p")
            for x in pretty_order
        ]
    )
    y = [1 for x in pretty_order]
    date_fmt = mdates.DateFormatter("%I:%M:%S %p")
    fig, ax = plt.subplots()
    plt.title("Student Schedule Clustered - Localized")
    plt.ylim(0, 2)
    plt.xlim(x[0], x[-1])
    ax.xaxis.set_major_formatter(date_fmt)
    ax.scatter(x, y)
    plt.grid(color="r", linestyle="-", linewidth=1)
    plt.show()

# get school start times
schoolToTime = {}
schoolOrder = []
cur_school = "not a real school"
for entry in data:
    student = emailToRow[entry["Email"]]
    school = student["School"] if student["School"] != "" else "Unknown"
    if school != cur_school:
        schoolToTime[school] = entry["Start Time"]
        cur_school = school
        schoolOrder.append(
            {
                "School": school,
                "Start Time": datetime.strptime(
                    entry["Start Time"], "%Y-%m-%d %I:%M:%S %p"
                ),
            }
        )

schoolOrder = sorted(schoolOrder, key=lambda i: i["Start Time"])
schoolOrder = [
    {
        "School": s["School"] if s["School"] != "" else "Unknown",
        "Start Time": s["Start Time"].strftime("%Y-%m-%d %I:%M:%S %p"),
    }
    for s in schoolOrder
]

# save utc school schedule
with open(
    "data/FINAL school schedule utc.csv", "w", encoding="utf-8", newline=""
) as schoolScheduleCSVFile:
    csvFields = ["School", "Start Time"]
    writer = csv.DictWriter(schoolScheduleCSVFile, fieldnames=csvFields)
    writer.writeheader()
    writer.writerows(schoolOrder)
    print("\n--> Saved FINAL school schedule utc CSV!")

# use tabulate to save html school schedule
with open("data/school-schedule.html", "w", encoding="utf-8") as schoolScheduleHTMLFile:
    schoolScheduleHTMLFile.write(tabulate(schoolOrder, headers="keys", tablefmt="html"))
    print("\n--> Saved FINAL school schedule utc HTML!")

# save final dataset
finalData = []
for item in data:
    student = emailToRow[item["Email"]]
    student["Start Time UTC"] = item["Start Time"]
    school = student["School"] if student["School"] != "" else "Unknown"
    student["School Start Time UTC"] = schoolToTime[school]
    student["School"] = school
    student["Approx Time Zone"] = item["Time Zone"]
    finalData.append(student)

with open(
    "data/FINAL student schedule utc.csv", "w", encoding="utf-8", newline=""
) as studentScheduleFile:
    csvFields = list(finalData[0].keys())
    writer = csv.DictWriter(studentScheduleFile, fieldnames=csvFields)
    writer.writeheader()
    writer.writerows(finalData)
    print("\n--> Saved FINAL student schedule utc.csv!")
