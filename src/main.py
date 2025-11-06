import cv2
import mediapipe as mp
from datetime import datetime 
from tkinter import *
from tkinter import ttk, filedialog
import tkinter as tk
import pygame
import os
import json
import threading
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
import serial
import time
import sys
from serial import Serial 


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.dispositivos.comunica_arduino import envia_pose, envia_string, serial_monitora, enviar_brightness, enviar_hue, enviar_batida
from src.config.poses import dicionario_poses, dicionario_poses_pernas
from src.deteccao_poses.exibicao import calcula_angulo,funcao_texto
from src.utils.distancia import distancia


'''
=========================================================
                Inicialização do Arduino
=========================================================
'''

try:
    arduino = serial.Serial("COM5", baudrate=9600, timeout=0.4) #Alterar porta de acordo com dispositivo
    time.sleep(2)
    print("Conexão estabelecida com o Arduino.")
except Exception as e:
    print(f"Erro ao conectar com o Arduino: {e}")
    exit()


'''
=========================================================
Definições de variáveis globais e setup inicial de música
=========================================================
'''

isPlaying = False
pygame.mixer.init()
folder_path = 'data\musica\lista_musicas'
all_files = os.listdir(folder_path)
playlist = [file[:-4] for file in all_files]
current_song_index = 0

with open("data\musica\data.json", "r", encoding='utf-8') as file: 
    songs_json = json.load(file)

current_song_info = {}
current_time_s = 0
states_count = 0
current_state_time = 0
hue_brightness_index = 0
beats_index = 0
beat_anterior = 0

'''
=========================================================
            Definições de funções de músicas
=========================================================
'''

def toggle_full_screen():
    '''
    Função que faz alterar para tela cheia.
    '''
    is_fullscreen = root.attributes('-fullscreen')
    root.attributes('-fullscreen', not is_fullscreen)


def choose_song():
    '''
    Função que serve para permitir a escolha da música e atualiza a interface.
    '''
    global current_song_index
    global current_song_info
    global isPlaying
    global songs_json
    global current_state_time
    global states_count
    global hue_brightness_index
    global beats_index
    
    song_path = filedialog.askopenfilename(
        initialdir="data\musica\lista_musicas",  
        title="Escolha uma música",
        filetypes=(("MP3 files", "*.mp3"), ("All files", "*.*"))
    )

    if song_path:
        song_name = os.path.basename(song_path)[:-4]

        current_song_info = songs_json[song_name]
        current_state_time = current_song_info["state_time"]
        states_count = 0 
        hue_brightness_index = 0
        beats_index = 0

        song_status.config(text="Ouvindo agora")
        isPlaying = True
        song_label.config(text=f"{song_name}")

        for index, song in enumerate(playlist):
            if song == song_name:
                current_song_index = index

        main_frame.pack_forget()  # Esconde o main_frame
        music_player_frame.pack(fill="both", expand=True)   

        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play(loops=0, start=0.0)


def update_time():
    '''
    Função que acompanha o tempo da música e atualiza suas variáveis.

    Essencial para o envio da batida.
    '''
    global current_time_s
    global states_count
    global hue_brightness_index
    global beats_index
    global isPlaying

    if isPlaying:
        try:
            current_time_s = pygame.mixer.music.get_pos() / 1000

            if current_time_s >= states_count * current_state_time and current_time_s <= current_song_info["total_time_length"]:
                enviar_hue(arduino, current_song_info["hue"][hue_brightness_index])
                enviar_brightness(arduino, current_song_info["brightness"][hue_brightness_index])
                states_count += 1 
                hue_brightness_index += 1
                

            elif current_time_s >= current_song_info["beats"][beats_index]:
                enviar_batida(arduino)
                beats_index += 1

        except:
            isPlaying = False

    root.after(1, update_time)


def play_pause_song():
    '''
    Função para iniciar música e pausar.
    '''
    global isPlaying
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
        play_button.config(text="Tocar")
        song_status.config(text="Música pausada")
        isPlaying = False
    else:
        pygame.mixer.music.unpause()
        play_button.config(text="Pausar")
        song_status.config(text="Ouvindo agora")
        isPlaying = True

def next_song():
    '''
    Função para passar para a próxima música.
    '''
    global current_song_index
    global isPlaying
    global current_song_info
    global current_state_time
    global hue_brightness_index
    global beats_index
    global states_count

    current_song_index += 1
    if current_song_index >= len(playlist):
        current_song_index = 0

    pygame.mixer.music.stop()

    next_song = playlist[current_song_index] 
    current_song_info = songs_json[next_song]   
    current_state_time = current_song_info["state_time"]
    hue_brightness_index = 0
    beats_index = 0
    states_count = 0

    play_button.config(text="Pausar")
    song_status.config(text="Ouvindo agora")
    song_label.config(text=f"{next_song}")

    next_song_path = f"./{folder_path}/{next_song}.mp3"

    pygame.mixer.music.load(next_song_path)
    pygame.mixer.music.play(loops=0, start=0.0)
    isPlaying = True

def previous_song():
    '''
    Função para voltar para a música anterior.
    '''
    global current_song_index
    global isPlaying
    global current_song_info
    global current_state_time
    global hue_brightness_index
    global beats_index
    global states_count

    current_song_index -= 1
    if current_song_index < 0:
        current_song_index = len(playlist) - 1

    pygame.mixer.music.stop()

    previous_song = playlist[current_song_index]    
    current_song_info = songs_json[previous_song]   
    current_state_time = 0
    hue_brightness_index = 0
    beats_index = 0
    states_count = 0

    play_button.config(text="Pausar")
    song_status.config(text="Ouvindo agora")
    song_label.config(text=f"{previous_song}")

    previous_song_path = f"./{folder_path}/{previous_song}.mp3"

    pygame.mixer.music.load(previous_song_path)
    pygame.mixer.music.play(loops=0, start=0.0)
    isPlaying = True

def stop_song():
    '''
    Função para parar música.
    '''
    global isPlaying

    pygame.mixer.music.stop()
    play_button.config(text="Pausar")
    isPlaying = False
    music_player_frame.pack_forget()  # Esconde o music_player_frame
    main_frame.pack(fill="both", expand=True) 


'''
=========================================================
            Chamada de funções de música
=========================================================
'''

# Cria a janela principal
root = tk.Tk()

root.attributes('-fullscreen', False)

bg_color = "#f0f0f0"

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", background=bg_color, font=("Arial", 24), padding=5)
style.configure("TLabel", background=bg_color, font=("Arial", 28))
style.configure("TFrame", background=bg_color)

# Cria o frame principal
main_frame = ttk.Frame(root, padding=10)
main_frame.pack(fill="both", expand=True)

# Rótulo de título
title_label = ttk.Label(main_frame, text="ROBÔ DANÇANTE")
title_label.pack(pady=10)  # Adiciona espaçamento vertical ao redor do título

# Botão para escolher a música
choose_song_button = ttk.Button(main_frame, text="Escolher música", command=choose_song)
choose_song_button.pack(pady=10)  # Adiciona espaçamento vertical ao redor do botão

# Cria o frame do player de música (inicialmente oculto)
music_player_frame = ttk.Frame(root, padding=10)

song_status = ttk.Label(music_player_frame)
song_status.pack(pady=5)  # Adiciona espaçamento vertical

song_label = ttk.Label(music_player_frame)  
song_label.pack(pady=5)

# Frame para organizar os botões lado a lado
buttons_frame = ttk.Frame(music_player_frame)
buttons_frame.pack(pady=5)

# Botão para música anterior
previous_button = ttk.Button(buttons_frame, text="Anterior", command=previous_song)
previous_button.pack(side="left", padx=5)

# Botão para pausar ou tocar a música
play_button = ttk.Button(buttons_frame, text="Pausar", command=play_pause_song)
play_button.pack(side="left", padx=5)

# Botão para próxima música
next_button = ttk.Button(buttons_frame, text="Próxima", command=next_song)
next_button.pack(side="left", padx=5)

'''
=========================================================
       Definições de variáveis globais da interface
=========================================================
'''

pose_atual_braco = None
pose_atual_perna = None

'''
=========================================================
        Chamada de funções de detecção de poses
=========================================================
'''

def start_video_processing():
    video = cv2.VideoCapture(0) # Inicia captura de vídeo
   
    if not video.isOpened(): # Verifica que a captura foi inicada
        print("Erro: Não foi possível acessar a câmera.")
        exit()

    mp_pose = mp.solutions.pose # Importa a solução Pose do MediaPipe
    pose = mp_pose.Pose(min_tracking_confidence=0.5, min_detection_confidence=0.5) # Parametros da função
    mp_draw = mp.solutions.drawing_utils # Importa as ferramentas de desenho do MediaPipe

   # Define o label (interface) do Tkinter
    video_label = ttk.Label(root, anchor="center")  # Coloca o vídeo no label principal (root)
    video_label.pack(side="bottom", fill="both", expand=True, padx=10, pady=10)  # Posiciona o vídeo

    def update_video():
        ret, frame = video.read() # Inicializa leitura do vídeo

        if not ret: # Verifica se leitura foi feita
            print("Falha ao capturar o vídeo.")
            return

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # Converção de cores BGR para RGB (RGB: Padrão do MediaPipe)
        result = pose.process(frame_rgb) # Processa o quadro de imagem e rastrea os pontos

        # Verifica se os landmarks foram encontrados
        if result.pose_landmarks:

            # Chama as variáveis globais das posições atuais 
            global pose_atual_braco
            global pose_atual_perna

            # Chama as variáveis globais da música
            global beats_index
            global beat_anterior

            # Desenha os landmarks na imagem
            mp_draw.draw_landmarks(frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            h, w, _ = frame.shape # Captura as dimensões do frame
            landmarks = result.pose_landmarks.landmark # Traça desenho entre pontos rastreados

            #-----------------------------------------------------------------------------------------------------------------------------------
            # Calcula as coordenadas dos pontos específicos
            
            # Pé Direito
            peDY = int(landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX].y * h)
            peDX = int(landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX].x * w)
            peDZ = int(landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX].z)

            # Pé Esquerdo
            peEY = int(landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX].y * h)
            peEX = int(landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX].x * w)
            peEZ = int(landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX].z)

            # Mão direita
            maoDY = int(landmarks[mp_pose.PoseLandmark.RIGHT_INDEX].y * h)
            maoDX = int(landmarks[mp_pose.PoseLandmark.RIGHT_INDEX].x * w)
            maoDZ = int(landmarks[mp_pose.PoseLandmark.RIGHT_INDEX].z)
            # Mão esquerda
            maoEY = int(landmarks[mp_pose.PoseLandmark.LEFT_INDEX].y * h)
            maoEX = int(landmarks[mp_pose.PoseLandmark.LEFT_INDEX].x * w)
            maoEZ = int(landmarks[mp_pose.PoseLandmark.LEFT_INDEX].z)

            # Torso direito
            torsoDX = int(landmarks[mp_pose.PoseLandmark.RIGHT_HIP].x * w)
            torsoDY = int(landmarks[mp_pose.PoseLandmark.RIGHT_HIP].y * h)

            # Torso Esquerdo
            torsoEX = int(landmarks[mp_pose.PoseLandmark.LEFT_HIP].x * w)
            torsoEY = int(landmarks[mp_pose.PoseLandmark.LEFT_HIP].y * h)

            # Ombro Direito
            ombroDX = int(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x * w)
            ombroDY = int(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * h)

            # Ombro Esquerdo
            ombroEX = int(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x * w)
            ombroEY = int(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y * h)

            # Cotovelo Direito
            cotoveloDX = int(landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].x * w)
            cotoveloDY = int(landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW].y * h)

            # Cotovelo Esquerdo
            cotoveloEX = int(landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].x * w)
            cotoveloEY = int(landmarks[mp_pose.PoseLandmark.LEFT_ELBOW].y * h)

            # Joelho Direito
            joelhoDX = int(landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].x * w)
            joelhoDY = int(landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].y * h)

            # Joelho Esquerdo
            joelhoEX = int(landmarks[mp_pose.PoseLandmark.LEFT_KNEE].x * w)
            joelhoEY = int(landmarks[mp_pose.PoseLandmark.LEFT_KNEE].y * h)

            #-----------------------------------------------------------------------------------------------------------------------------------
            # Calcula os ângulos e exibe (CALCULO DE ANGULO APENAS PARA EXIBIÇÃO: Entre vetor e vetor vertical)

            # Perna direita (baixo)
            anguloPDB = calcula_angulo(peDX, peDY, joelhoDX, joelhoDY)
            cv2.putText(frame, str(anguloPDB), (int((peDX+joelhoDX)/2)-40, int((peDY+joelhoDY)/2)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            # Perna direita (cima)
            anguloPDC = calcula_angulo(joelhoDX, joelhoDY, torsoDX, torsoDY)
            cv2.putText(frame, str(anguloPDC), (int((joelhoDX+torsoDX)/2)-40, int((joelhoDY+torsoDY)/2)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            # Perna esquerda (baixo)
            anguloPEB = calcula_angulo(peEX, peEY, joelhoEX, joelhoEY)
            cv2.putText(frame, str(anguloPEB), (int((peEX+joelhoEX)/2)+40, int((peEY+joelhoEY)/2)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            # Perna esquerda (cima)
            anguloPEC = calcula_angulo(joelhoEX, joelhoEY, torsoEX, torsoEY)
            cv2.putText(frame, str(anguloPEC), (int((joelhoEX+torsoEX)/2)+40, int((joelhoEY+torsoEY)/2)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            # Braço (cima) direito
            anguloBDC = calcula_angulo(cotoveloDX, cotoveloDY, ombroDX, ombroDY)
            cv2.putText(frame, str(anguloBDC), (int((cotoveloDX+ombroDX)/2)-40, int((cotoveloDY+ombroDY)/2)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            # Braço (baixo) direito
            anguloBDB = calcula_angulo(maoDX, maoDY, cotoveloDX, cotoveloDY)
            cv2.putText(frame, str(anguloBDB), (int((cotoveloDX + maoDX) / 2)-40, int((cotoveloDY + maoDY) / 2)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            # Braço (cima) esquerdo
            anguloBEC = calcula_angulo(cotoveloEX, cotoveloEY, ombroEX, ombroEY)
            cv2.putText(frame, str(anguloBEC), (int((cotoveloEX+ombroEX)/2)+40, int((cotoveloEY+ombroEY)/2)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            # Braço (baixo) esquerdo
            anguloBEB = calcula_angulo(maoEX, maoEY, cotoveloEX, cotoveloEY)
            cv2.putText(frame, str(anguloBEB), (int((cotoveloEX + maoEX) / 2)+40, int((cotoveloEY + maoEY) / 2)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            #-----------------------------------------------------------------------------------------------------------------------------------
            # Exibição visual

            texto = str(peDX) + "," + str(peDY) + "," + str(peDZ)
            cv2.putText(frame, texto, (peDX, peDY),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            texto = str(maoDX) + "," + str(maoDY) + "," + str(maoDZ)
            cv2.putText(frame, texto, (maoDX, maoDY),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            

            #-----------------------------------------------------------------------------------------------------------------------------------
            # DETECÇÃO DA POSES DOS BRAÇOS

            # Verifica se tem posição com mãos para frente, caso contrário, percorre dicionário de poses.

            if distancia(ombroDX,maoDX,ombroDY,maoDY) <70 and distancia(ombroEX,maoEX,ombroEY,maoEY) <70 and distancia(ombroDX,cotoveloDX,ombroDY,cotoveloDY) <70 and distancia(ombroEX,cotoveloEX,ombroEY,cotoveloEY) <70:
                cor = (255, 105, 180)
                texto = "Bracos: "+ 'ambos_frente'
                coord1 = 10
                coord2 = 300
                pose_atual_braco = 'arm05'
                funcao_texto(texto.replace("_", " "), cor, frame, coord1, coord2)

            elif distancia(ombroDX,maoDX,ombroDY,maoDY) <70 and distancia(ombroDX,cotoveloDX,ombroDY,cotoveloDY) <70:
                if anguloBEC>=90:
                    cor = (255, 105, 180)
                    texto = "Bracos: "+ 'D_frente e E_dobrado'
                    coord1 = 10
                    coord2 = 300
                    pose_atual_braco = 'arm08'
                    funcao_texto(texto.replace("_", " "), cor, frame, coord1, coord2)
                else:
                    cor = (255, 105, 180)
                    texto = "Bracos: "+ 'D_frente e E_reto'
                    coord1 = 10
                    coord2 = 300
                    pose_atual_braco = 'arm07'
                    funcao_texto(texto.replace("_", " "), cor, frame, coord1, coord2)

            elif distancia(ombroEX,maoEX,ombroEY,maoEY) <70 and distancia(ombroEX,cotoveloEX,ombroEY,cotoveloEY) <70:
                if anguloBDC >=90:
                    cor = (255, 105, 180)
                    texto = "Bracos: "+ 'E_frente e D_dobrado'
                    coord1 = 10
                    coord2 = 300
                    pose_atual_braco = 'arm08'
                    funcao_texto(texto.replace("_", " "), cor, frame, coord1, coord2)
                else:
                    cor = (255, 105, 180)
                    texto = "Bracos: "+ 'E_frente e D_reto'
                    coord1 = 10
                    coord2 = 300
                    pose_atual_braco = 'arm07'
                    funcao_texto(texto.replace("_", " "), cor, frame, coord1, coord2)

            else:                
                for movimento, angulos in dicionario_poses.items():
                    if angulos["condicao"](anguloBEC, anguloBEB, anguloBDC, anguloBDB):
                        cor = (255, 105, 180)
                        texto = "Bracos: "+ movimento
                        coord1 = 10
                        coord2 = 300
                        pose_atual_braco = angulos["nome"]
                        funcao_texto(texto.replace("_", " "), cor, frame, coord1, coord2)
            #-----------------------------------------------------------------------------------------------------------------------------------

            # DETECÇÃO DA POSES DAS PERNAS

            # Verifica se tem posição com pernas para frente, caso contrário, percorre dicionário de poses.

            if distancia(peDX,joelhoDX,peDY,joelhoDY) <70:
                cor = (255, 105, 180)
                texto = "Pernas: "+ 'direita_tras'
                coord1 = 10
                coord2 = 250
                pose_atual_braco = 'leg02'
                funcao_texto(texto.replace("_", " "), cor, frame, coord1, coord2)

            elif distancia(peEX,joelhoEX,peEY,joelhoEY) <70:
                cor = (235, 105, 180)
                texto = "Pernas: "+ 'esquerda_tras'
                coord1 = 10
                coord2 = 250
                pose_atual_braco = 'leg02'
                funcao_texto(texto.replace("_", " "), cor, frame, coord1, coord2)

            else:                
                for movimento, angulos in dicionario_poses_pernas.items():
                    if angulos["condicao"](anguloPEC, anguloPDC):
                        cor = (255, 105, 180)
                        texto = "Pernas: "+ movimento
                        coord1 = 10
                        coord2 = 250
                        pose_atual_perna = angulos["nome"]
                        funcao_texto(texto.replace("_", " "), cor, frame, coord1, coord2)


            # Somente envia a pose quando uma batida da música for detectada.

            if beats_index > beat_anterior:
                print('Movimento ' + str(pose_atual_perna) + " " + str(pose_atual_braco))
                envia_pose(arduino, pose_atual_perna, pose_atual_braco)

            beat_anterior = beats_index

        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # Converte o frame para Image (padrão do Tkinter)
        frame_img = Image.fromarray(frame_bgr)
        frame_tk = ImageTk.PhotoImage(frame_img)

        # Atualiza a imagem no Tkinter label
        video_label.img = frame_tk 
        video_label.configure(image=frame_tk)

        # Chama a função de novo a cada 1ms
        root.after(1, update_video)

    update_video()


'''
=========================================================
          Inicialização e Execução do Sistema
=========================================================
'''

thread = threading.Thread(target=start_video_processing, daemon=True)
thread.start()
thread2 = threading.Thread(target=serial_monitora, args=[arduino], daemon=True)
thread2.start()

update_time() 
root.mainloop() 