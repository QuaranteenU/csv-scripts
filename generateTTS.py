import csv
import os
from gtts import gTTS
from pydub import AudioSegment
from io import BytesIO

with open("data/final schedule with uuids.csv", encoding="utf-8") as scheduleFile:
    graduates = [
        {k: v for k, v in row.items()}
        for row in csv.DictReader(scheduleFile, skipinitialspace=True)
    ]

for grad in graduates:
    if grad["Senior quote?"] != "":
        speech = gTTS(text=grad["Senior quote?"], lang="en")
        speech.save("audio/{} tts.mp3".format(grad["Audio File Name"]))

        nameAudio = AudioSegment.from_mp3(
            "audio/{}.mp3".format(grad["Audio File Name"])
        )
        ttsAudio = AudioSegment.from_mp3(
            "audio/{} tts.mp3".format(grad["Audio File Name"])
        )
        combinedAudio = nameAudio + ttsAudio
        finalAudio = combinedAudio[: min(29500, len(combinedAudio))]
        finalAudio.export("audio/{}.mp3".format(grad["Audio File Name"]), format="mp3")

        os.remove("audio/{} tts.mp3".format(grad["Audio File Name"]))
        print(
            "Generated for {} ({})".format(
                grad["Your Full Name"], grad["Audio File Name"]
            )
        )
