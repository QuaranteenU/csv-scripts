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
    init_command="SET SESSION time_zone='+00:00'",
    cursorclass=pymysql.cursors.DictCursor,
)

try:
    with connection.cursor() as cursor:
        # init temp variable
        sql = "SET @row_number = 0"
        cursor.execute(sql)

        # use variable to update timeslots
        sql = "UPDATE `graduates` SET `timeslot` = FROM_UNIXTIME(30 * (@row_number:=@row_number + 1) + UNIX_TIMESTAMP()) WHERE `graduated` = 0"
        cursor.execute(sql)
        print("> Reset timeslots")
finally:
    connection.close()
