import csv
import statistics
from collections import defaultdict

# load data
filename = input("Enter contacts filename (default: contacts.csv): ") or "contacts.csv"
with open("data/{}".format(filename), encoding="utf-8") as scheduleFile:
    contacts = [
        {k: v for k, v in row.items()}
        for row in csv.DictReader(scheduleFile, skipinitialspace=True)
    ]

# prepare default dicts so we don't have to check if key exists
school_to_timezones = defaultdict(list)
school_to_student_count = defaultdict(int)

for contact in contacts:
    # use default value for schools
    school = "Unknown" if contact["Your school"] == "" else contact["Your school"]

    # append timezone if it parses, otherwise ignore
    try:
        tz = int(contact["Time Zone"])
        school_to_timezones[school].append(tz)
    except ValueError:
        print("No timezone found for {}".format(contact["Your Full Name"]))

    # increment number of students in this school
    school_to_student_count[school] += 1

schools = []
SEC_PER_PERSON = 30

# generate data
for school, timezones in school_to_timezones.items():
    total_students = school_to_student_count[school]
    schools.append(
        {
            "School": school,
            "Average Timezone": round(statistics.mean(timezones)),
            "Students": total_students,
            "Seconds": round(total_students * SEC_PER_PERSON, 2),
            "Minutes": round(total_students * SEC_PER_PERSON / 60, 2),
            "Hours": round(total_students * SEC_PER_PERSON / 60 / 60, 2),
        }
    )

# save CSV
filename = (
    input("Enter timezones filename (default: school timezones.csv): ")
    or "school timezones.csv"
)
with open(
    "data/{}".format(filename), "w", encoding="utf-8", newline=""
) as timezones_file:
    csvFields = list(schools[0].keys())
    writer = csv.DictWriter(timezones_file, fieldnames=csvFields)
    writer.writeheader()
    writer.writerows(schools)
    print("\n--> Saved {}".format(filename))
