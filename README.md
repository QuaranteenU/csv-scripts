# csv scripts
These scripts contain all the logic necessary to run a Minecraft graduation, outside of the GradCraft Plugin (you need that as well). This repository generates a schedule, retrieves Minecraft UUIDs, runs TTS on quotes, and imports them to SQL. If the workflow changes to use Firebase instead of Google Sheets/CSVs, a lot of code will have to be modified.

## Installation
Clone the repo and create a virtual env with `python3 -m venv`. Next install dependencies with `python3 -m pip install -r requirements.txt`. Then create the following folders in the root directory: `audio`, `convert`, `data`. Finally, copy `.env.sample` to `.env` and fill it out appropriately.

## Running
These scripts should be called in a specific order:
1. `average_school_timezones.py` will average timezones across a school based on the timezones of the students who RSVP'd from that school. It saves this list of schools and their average timezones.
2. `generate_schedule.py` creates a schedule of schools based on the average timezone (preferring to start at 2 PM localized when possible), then using the school schedule to generate a schedule of students. This schedule maximizes the number of students who get a good localized timeslot (between 2 PM and 6 PM localized), but this leads to a very broken up ceremony as students are spread out. To fix this, manually cluster the students using Google Sheets (upload the csv, pick start times for clusters and use the drag autofill feature).
3. `merge_schedule_with_contacts.py` combines the schedule generated in the previous step with the contact data so everything is one place. From here, you can start to email people their timeslots.
4. `get_minecraft_uuids.py` will look up Minecraft UUIDs for all contacts that gave one, and save it back into the contacts CSV.
5. `generate_quote_audio.py` will use Google TTS to generate audio of contacts' senior quotes, and append them to audio files of their names beind read. Make sure to have created those audio files of names being read first, named according to the "Audio File Name" column inside the contacts dataset.
6. `import_sql.py` imports the contact dataset into your SQL database, so that the GradCraft plugin can access the data as well.
7. `play_ceremony_audio.py` pulls the data from SQL (to ensure it's the same data GradCraft is using), and schedules the playing of audio files based on the contact's timeslot.

Following the above order will set up your data and run the audio for the ceremony. Make sure to run `play_ceremony_audio.py` **BEFORE** you run `/cerstart` in Minecraft.

Also included in this repo are the following helper scripts, which you may or may not need:
- `convert_m4a_to_mp3.py` converts all m4a files in the `convert` folder to mp3 files. Useful if you recorded audio using Windows' built in voice recorder.
- `reset_timeslots.py` resets the timeslots of all graduates who have not yet gone on stage in SQL. The first graduate who hasn't gone yet will now have their timeslot set to 30 seconds after the running of this file, with the rest of the graduates following after. Useful if the cermeony has to stop at some point and needs to restart.
