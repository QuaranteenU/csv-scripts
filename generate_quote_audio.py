import csv
from pathlib import Path
from gtts import gTTS
from pydub import AudioSegment
from io import BytesIO

with open("data/final schedule with uuids.csv", encoding="utf-8") as scheduleFile:
    graduates = [
        {k: v for k, v in row.items()}
        for row in csv.DictReader(scheduleFile, skipinitialspace=True)
    ]

audioFileNameToQuote = {}
audioFileNameToName = {}
for grad in graduates:
    audioFileNameToQuote[grad["Audio File Name"]] = grad["Senior quote?"]
    audioFileNameToName[grad["Audio File Name"]] = grad["Your Full Name"]

files = list(Path("audio").glob("*.mp3"))
for file in files:
    audioFileName = file.stem
    quote = audioFileNameToQuote[audioFileName]
    if quote != "":
        speech = gTTS(text=quote, lang="en")
        speech.save("audio/{} tts.mp3".format(audioFileName))

        nameAudio = AudioSegment.from_mp3(file)
        ttsAudio = AudioSegment.from_mp3("audio/{} tts.mp3".format(audioFileName))
        combinedAudio = nameAudio + ttsAudio
        finalAudio = combinedAudio[: min(29500, len(combinedAudio))]
        finalAudio.export("audio/{}.mp3".format(audioFileName), format="mp3")

        Path("audio/{} tts.mp3".format(audioFileName)).unlink()
        print(
            "Generated for {} ({})".format(
                audioFileNameToName[audioFileName], audioFileName
            )
        )
