import csv
import pymysql.cursors
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Connect to the database
connection = pymysql.connect(
    host=os.getenv("SQL_HOST"),
    user=os.getenv("SQL_USER"),
    password=os.getenv("SQL_PASSWORD"),
    db=os.getenv("SQL_DB"),
    charset="utf8mb4",
    autocommit=True,
    # init_command="SET SESSION time_zone='+00:00'",
    cursorclass=pymysql.cursors.DictCursor,
)

with open("data/final schedule with uuids.csv", encoding="utf-8") as scheduleFile:
    graduates = [
        {k: v for k, v in row.items()}
        for row in csv.DictReader(scheduleFile, skipinitialspace=True)
    ]

ceremonies = sorted(
    list(set([(row["Ceremony Name"], row["Ceremony Start Time"]) for row in graduates]))
)
schools = sorted(list(set([row["School"] for row in graduates])))


def convertDate(date):
    return datetime.strptime(date, "%Y-%m-%d %I:%M:%S %p").strftime("%Y-%m-%d %H:%M:%S")


IS_HIGH_SCHOOL = True
try:
    with connection.cursor() as cursor:
        # let us do the thing SQL
        sql = "SET FOREIGN_KEY_CHECKS = 0"
        cursor.execute(sql)

        # remove all ceremonies
        sql = "TRUNCATE TABLE `ceremonies`"
        cursor.execute(sql)
        print("> DELETED * FROM ceremonies")

        # remove all universities
        sql = "TRUNCATE TABLE `universities`"
        cursor.execute(sql)
        print("> DELETED * FROM universities")

        # remove all graduates
        sql = "TRUNCATE TABLE `graduates`"
        cursor.execute(sql)
        print("> DELETED * FROM graduates")

        # back to safety
        sql = "SET FOREIGN_KEY_CHECKS = 1"
        cursor.execute(sql)

        # insert new ceremonies
        for ceremony in ceremonies:
            sql = "INSERT INTO `ceremonies` (`startTime`, `name`) VALUES (%s, %s)"
            cursor.execute(sql, (convertDate(ceremony[1]), ceremony[0]))

        # print new number of ceremonies
        sql = "SELECT `id`, `startTime`, `name` FROM `ceremonies`"
        cursor.execute(sql)
        ceremonies = cursor.fetchall()
        print("> ceremonies length:", len(ceremonies))
        ceremonyToId = {}
        for c in ceremonies:
            ceremonyToId[c["name"]] = c["id"]

        # insert new schools
        for school in schools:
            sql = "INSERT INTO `universities` (`name`) VALUES (%s)"
            cursor.execute(sql, (school))

        # print new number of schools
        sql = "SELECT `id`, `name` FROM `universities`"
        cursor.execute(sql)
        universities = cursor.fetchall()
        print("> universities length:", len(universities))
        universityToId = {}
        for u in universities:
            universityToId[u["name"]] = u["id"]

        # insert new graduates
        for grad in graduates:
            sql = "INSERT INTO `graduates` (`name`, `email`, `pronunciation`, `degreeLevel`, `honors`, `major`, `seniorQuote`, `university`, `ceremony`, `uuid`, `timeslot`, `isHighSchool`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(
                sql,
                (
                    grad["Your Full Name"],
                    grad["Email Address"],
                    grad["Phonetic spelling of your name"]
                    if grad["Phonetic spelling of your name"] != ""
                    else None,
                    grad["Your Degree"] if "Your Degree" in grad else "",
                    grad["Anything else you'd like to include?"],
                    grad["Your Major(s)"] if "Your Major(s)" in grad else "",
                    grad["Senior quote?"],
                    universityToId[grad["School"]],
                    ceremonyToId[grad["Ceremony Name"]],
                    grad["UUID"] if grad["UUID"] != "" else None,
                    convertDate(grad["Start Time UTC"]),
                    IS_HIGH_SCHOOL,
                ),
            )

        # print new number of graduates
        sql = "SELECT COUNT(*) FROM `graduates`"
        cursor.execute(sql)
        result = cursor.fetchone()
        print("> graduates length:", result["COUNT(*)"])
finally:
    connection.close()
