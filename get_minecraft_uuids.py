import csv
import requests

# load contacts
filename = input("Enter contacts filename (default: contacts.csv): ") or "contacts.csv"
with open("data/{}".format(filename), encoding="utf-8") as scheduleFile:
    contacts = [
        {k: v for k, v in row.items()}
        for row in csv.DictReader(scheduleFile, skipinitialspace=True)
    ]

# if user says they have minecraft account, fetch their UUID
def fetch_uuid(contact):
    if (
        contact[
            "I confirm I have a Minecraft Java Edition account or will get one before the ceremony"
        ]
        == "Yup, I got it!"
    ):
        username = contact["Your Minecraft Username"]
        data = requests.get("https://api.ashcon.app/mojang/v2/user/{}".format(username))
        data.json()
        contact["UUID"] = data["uuid"]
        return contact
    else:
        contact["UUID"] = ""
        return contact


contacts_with_uuids = [fetch_uuid(contact) for contact in contacts]

# save CSV
filename = input("Enter contacts filename (default: contacts.csv): ") or "contacts.csv"
with open(
    "data/{}".format(filename), "w", encoding="utf-8", newline=""
) as timezones_file:
    csvFields = list(contacts_with_uuids[0].keys())
    writer = csv.DictWriter(timezones_file, fieldnames=csvFields)
    writer.writeheader()
    writer.writerows(contacts_with_uuids)
    print("\n--> Saved {}".format(filename))
