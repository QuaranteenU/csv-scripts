from pathlib import Path
from pydub import AudioSegment

original = list(Path("convert").glob("*.m4a"))
for file in original:
    audio = AudioSegment.from_file(file)
    num = int(file.stem)
    audio.export("convert/{}.mp3".format(num), format="mp3")
    file.unlink()
