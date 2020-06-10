# CSV Scripts

This is where we do the scheduling magic.

## How to use

average school timezones
generate schedule
merge schedule
get uuids
genereate quote audio
import sql
play ceremony audio


maybe:
convert m4a
reset timeslots


1. `average school times.js` averages timezones across a school based on the timezones of the students who RSVP'd from that school.
2. `gener.py` does the big work, creating a schedule of schools based on the average timezone (preferring to start at 2 PM localized when possible), then using the school schedule to generate a schedule of students (`student schedule utc.csv`). This schedule maximizes the number of students who get a good localized timeslot, but this leads to a very broken up ceremony as students are spread out. To fix this, manually cluster the students using Google Sheets (upload the csv, pick start times for clusters and use the drag autofill feature).
3. `mergeScheduleWithRSVP.py` creates the final dataset, which includes students' RSVP info, their school start time (UTC), and their start time (UTC). Send an email to people with their start times UTC, and localized if we have their timezone.
4. get uuids
5. 

## Contributing

Just make sure you use the autoformatter when you're done (`npm run format`). You'll have to install the Python dependencies (including the formatter, [black](https://github.com/psf/black)) separately from your `npm install`.

black .

# TODO

- add the above sql calls when deleting so that auto increment is fixed
- fix licenses on all repos here (GPL) and add all the fixins (contributors etc, check the Github community todolist)
- make all scripts python and add a requirements.txt
- make all scripts take command line input (either in args/flags or when running if no flags passed)/.env stuff so nothing is hard coded
- add reset sql script
