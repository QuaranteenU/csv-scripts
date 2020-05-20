import csv
import pymysql.cursors
from datetime import datetime

# Connect to the database
connection = pymysql.connect(
    host="localhost",
    user="root",
    password="asdfasdf",
    db="graduation",
    charset="utf8mb4",
    autocommit=True,
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


try:
    with connection.cursor() as cursor:
        # remove all graduates
        sql = "DELETE FROM `graduates`"
        cursor.execute(sql)
        print("> DELETED * FROM graduates")

        # remove all universities
        sql = "DELETE FROM `universities`"
        cursor.execute(sql)
        print("> DELETED * FROM universities")

        # remove all ceremonies
        sql = "DELETE FROM `ceremonies`"
        cursor.execute(sql)
        print("> DELETED * FROM ceremonies")

        # insert new ceremonies
        for ceremony in ceremonies:
            sql = "INSERT INTO `ceremonies` (`startTime`, `name`) VALUES (%s, %s)"
            cursor.execute(sql, (convertDate(ceremony[1]), ceremony[0]))

        # print new number of ceremonies
        sql = "SELECT `*` FROM `ceremonies`"
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
        sql = "SELECT `*` FROM `universities`"
        cursor.execute(sql)
        universities = cursor.fetchall()
        print("> universities length:", len(universities))
        universityToId = {}
        for u in universities:
            universityToId[u["name"]] = u["id"]

        # insert new graduates
        for grad in graduates:
            sql = "INSERT INTO `graduates` (`name`, `email`, `pronunciation`, `degreeLevel`, `honors`, `major`, `seniorQuote`, `university`, `ceremony`, `uuid`, `timeslot`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(
                sql,
                (
                    grad["Your Full Name"],
                    grad["Email Address"],
                    grad["Phonetic spelling of your name"],
                    grad["Your Degree"],
                    grad["Anything else you'd like to include?"],
                    grad["Your Major(s)"],
                    grad["Senior quote?"],
                    universityToId[grad["School"]],
                    ceremonyToId[grad["Ceremony Name"]],
                    grad["UUID"],
                    convertDate(grad["Start Time UTC"]),
                ),
            )

        # print new number of graduates
        sql = "SELECT COUNT(*) FROM `graduates`"
        cursor.execute(sql)
        result = cursor.fetchone()
        print("> graduates length:", result["COUNT(*)"])
finally:
    connection.close()
