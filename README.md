# CSV Scripts

This is where we do the scheduling magic.

## How to use

1. `mergeRsvps.js` is only used for the commencement ceremony as there were two RSVP forms. Use it to create a Master RSVP file.
2. `getSchools.js` is only used for the commencement ceremony as QUA RSVP asked for school name. Use it to create a Master RSVP with schools file (uses `university_map.json` to populate school names, will need some manual work after to catch what it missed). At this point, do cleaning of the RSVP file (normalize timezones to ints, normalize degrees/etc, remove joke entries/bad language, etc).
3. `getSchoolTimezones.js` averages timezones across a school based on the timezones of the students who RSVP'd from that school.
4. `orderSchools.py` does the big work, creating a schedule of schools based on the average timezone (preferring to start at 2 PM localized when possible), then using the school schedule to generate a schedule of students (`student schedule utc.csv`). This schedule maximizes the number of students who get a good localized timeslot, but this leads to a very broken up ceremony as students are spread out. To fix this, manually cluster the students using Google Sheets (upload the csv, pick start times for clusters and use the drag autofill feature).
5. `mergeScheduleWithRSVP.py` creates the final dataset, which includes students' RSVP info, their school start time (UTC), and their start time (UTC). Send an email to people with their start times UTC, and localized if we have their timezone.

## Contributing

Just make sure you use the autoformatter when you're done (`npm run format`). You'll have to install the Python dependencies (including the formatter, [black](https://github.com/psf/black)) separately from your `npm install`.
