import librosa
import os
import numpy as np
import matplotlib.pyplot as plt
import json

def normalize_to_100(values):
    '''
    Função para normalizar os valores entre 0 e 100.

    Explicação do cálculo:
    (val - min_val) / (max_val - min_val) --> Normaliza valores entre 0 e 1
    Multiplicando por 100 --> Normaliza valores entre 0 e 100
    '''
    min_val = min(values)
    max_val = max(values)
    
    # Avoid division by zero if min and max are the same
    if max_val == min_val:
        return [0] * len(values)  # or return [100] if you want all values to be the same

    normalized_values = [int((val - min_val) / (max_val - min_val) * 100) for val in values]
    return normalized_values

def normalize_to_255(values):
    '''
    Função para normalizar os valores entre 0 e 255.

    Explicação do cálculo:
    (val - min_val) / (max_val - min_val) --> Normaliza valores entre 0 e 1
    Multiplicando por 255 --> Normaliza valores entre 0 e 255
    '''
    min_val = min(values)
    max_val = max(values)
    
    # Avoid division by zero if min and max are the same
    if max_val == min_val:
        return [0] * len(values)  # or return [255] if you want all values to be the same

    normalized_values = [int((val - min_val) / (max_val - min_val) * 255) for val in values]
    return normalized_values

def perform_stft(y):
    '''
    Calcula a Transformada de Fourier de Curto Prazo (STFT) de um sinal de áudio.
    Transforma o sinal de áudio em um domínio tempo-frequência (frequências e magnitudes ao longo do tempo).

    Retorna um array bidimensional que contém os coeficientes complexos da STFT: 
       linhas --> representam as frequências (ou bins de frequencia)
       colunas --> representam o tempo (janelas)
    '''
    # Perform Short-Time Fourier Transform (STFT)
    D = librosa.stft(y)
    return D

def get_audio_length(y, sr):
    ''' 
    Calcula a duração total do aúdio em segundos.

    y --> Array com amplitudes do sinal em cada ponto
    sr --> Número de amostras por segundo
    '''
    # Calculate the length of the audio in seconds
    length_in_seconds = len(y) / sr
    return length_in_seconds

def get_frequencies(y, sr):
    D = perform_stft(y)

    # Get the frequency bins corresponding to the STFT (up to Nyquist frequency)
    frequencies = librosa.fft_frequencies(sr=sr, n_fft=D.shape[0])

    # Only use the positive half of the frequencies (because negative frequencies are redundant)
    frequencies = frequencies[:D.shape[0] // 2 + 1]

    # Find the dominant frequency in each frame
    dominant_frequencies = []
    for t in range(D.shape[1]):
        # Find the index of the maximum value in the magnitude of the STFT for this time frame
        magnitude = np.abs(D[:, t])
        dominant_index = np.argmax(magnitude[:len(frequencies)])  # Ensure we only look at the positive frequencies
        dominant_frequencies.append(frequencies[dominant_index])
    
    # Group frequencies in bins of 5 and take the average of each bin
    grouped_frequencies = []
    for i in range(0, len(dominant_frequencies), 100):
        # Take the slice of 5 values (or less if near the end of the list)
        freq_group = dominant_frequencies[i:i + 5]
        # Calculate the average of the group
        avg_frequency = np.mean(freq_group)
        grouped_frequencies.append(float(avg_frequency))

    return grouped_frequencies

def get_magnitudes(y, len_frequencies):
    D = perform_stft(y)

    # Create second plot: Average Magnitude over time in dB
    average_magnitudes_db = []
    for t in range(D.shape[1]):
        magnitude = np.abs(D[:, t])
        # Convert to dB (relative to the minimum magnitude)
        magnitude_db = librosa.amplitude_to_db(magnitude, ref=np.min)
        average_magnitude_db = np.mean(magnitude_db[:len_frequencies])  # Average magnitude (in dB) over all frequencies
        average_magnitudes_db.append(average_magnitude_db)

    # Group frequencies in bins of 100 and take the average of each bin
    grouped_magnitudes = []
    for i in range(0, len(average_magnitudes_db), 100):
        # Take the slice of 100 values (or less if near the end of the list)
        mag_group = average_magnitudes_db[i:i + 100]
        # Calculate the average of the group
        avg_mag = np.mean(mag_group)
        grouped_magnitudes.append(float(avg_mag))
    
    return grouped_magnitudes

def get_beat_track(file_path):
    # read audio file
    x, sr = librosa.load(file_path)
    tempo, beat_times = librosa.beat.beat_track(y=x, sr=sr, units='time')

    return beat_times

def make_json():
    # List to store the playlist (paths to songs)
    folder_path = 'data/musica/wav'
    all_files = os.listdir(folder_path)
    playlist = [file[:-4] for file in all_files]

    djson = {}

    for song in playlist:
        djson[song] = {}

        file_path = f"data/musica/wav/{song}.wav"  
        y, sr = librosa.load(file_path, sr=None)

        hue = normalize_to_255(get_frequencies(y, sr))
        size = len(hue)
        brightness = normalize_to_100(get_magnitudes(y, size))
        total_time_length = get_audio_length(y, sr)
        state_time = total_time_length / size

        beats = get_beat_track(file_path)

        djson[song]["hue"] = hue
        djson[song]["brightness"] = brightness
        djson[song]["state_time"] = state_time
        djson[song]["total_time_length"] = total_time_length
        djson[song]["beats"] = beats.tolist()
    
    json_content = json.dumps(djson, ensure_ascii=False)
    file = open("data/musica/data.json", "w", encoding='utf-8')
    file.write(json_content)
    file.close()

if __name__ == '__main__':
    make_json()