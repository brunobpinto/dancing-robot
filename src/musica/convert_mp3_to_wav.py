from pydub import AudioSegment
import os

def convert_mp3_to_wav(mp3_file, wav_file):
    audio = AudioSegment.from_mp3(mp3_file)
    audio.export(wav_file, format="wav")


folder_path = 'data/musica/lista_musicas'
all_files = os.listdir(folder_path)
playlist = [file[:-4] for file in all_files]

for song in playlist:
    mp3_file = f"data/musica/lista_musicas/{song}.mp3"  
    wav_file = f"data/musica/wav/{song}.wav"  
    convert_mp3_to_wav(mp3_file, wav_file)
