import csv
import pymysql.cursors
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from pydub import AudioSegment
from pydub.playback import play
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()

sched = BackgroundScheduler()
sched.start()
running = True


def printNextJob():
    jobs = sched.get_jobs()
    if len(jobs) > 0:
        print("Next job:", jobs[0])
    else:
        print("That's it!")
        running = False


def playAudio(filePath, name):
    print("Playing audio for {}".format(name))
    printNextJob()
    audio = AudioSegment.from_mp3(filePath)
    play(audio)

filename = input("Enter data filename (default: contacts.csv): ") or "contacts.csv"
with open("data/{}".format(filename), encoding="utf-8") as scheduleFile:
    graduates = [
        {k: v for k, v in row.items()}
        for row in csv.DictReader(scheduleFile, skipinitialspace=True)
    ]

emailToAudioFile = {}
for grad in graduates:
    emailToAudioFile[grad["Email Address"]] = grad["Audio File Name"]

# Connect to the database
connection = pymysql.connect(
    host=os.getenv("SQL_HOST"),
    user=os.getenv("SQL_USER"),
    password=os.getenv("SQL_PASSWORD"),
    db=os.getenv("SQL_DB"),
    charset="utf8mb4",
    autocommit=True,
    cursorclass=pymysql.cursors.DictCursor,
)

try:
    with connection.cursor() as cursor:
        sql = "SELECT `id`, `name`, `email`, `timeslot` FROM `graduates` WHERE NOT `graduated`"
        cursor.execute(sql)
        graduates = cursor.fetchall()
        for grad in graduates:
            num = emailToAudioFile[grad["email"]]
            sched.add_job(
                playAudio,
                "date",
                name=grad["name"],
                run_date=grad["timeslot"],
                args=["audio/{}.mp3".format(num), grad["name"]],
            )
finally:
    connection.close()


printNextJob()
while running:
    inp = input("=====\nEnter Q to quit\n=====\n")
    if inp == "Q" or inp == "q":
        running = False
        sched.shutdown(wait=False)

if sched.running:
    sched.shutdown(wait=False)
