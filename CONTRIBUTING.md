# Contributing
Main thing to keep in mind is code style, other than that if your code adds value to the project it'll be merged in eventually. To make sure style is enforced, make sure to run `black .` in the root directory before committing.

## Things you could add
- Make black run as a pre-commit hook to ensure it's always enforced and people don't forget.
- Combine `average_school_timezones.py`, `generate_schedule.py`, `merge_schedule_with_contacts.py`, `get_minecraft_uuids.py`, and `generate_quote_audio.py` into one file that creates the final dataset and necessary files immediately.
- Add a requirements.txt file (at time of writing my virtualenv isn't working so I couldn't do this myself)
