from pydub import AudioSegment

if __name__ == '__main__':
    # Load audio file
    audio = AudioSegment.from_file("../../Darde-Moshtarak 1.mp3", format="mp3")
    print(audio)
