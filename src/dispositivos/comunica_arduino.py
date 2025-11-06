import serial

__all__ = ['envia_pose', 'envia_string', 'serial_monitora', 'enviar_hue', 'enviar_brightness', 'enviar_batida']


def envia_pose(arduino, pose_perna, pose_braco):
    ''' 
    Função que envia a pose (string) para o Arduino.

    O Arduino recebe as poses no seguinte padrão: "Movimento pose_da_perna pose_do_braço"

   "Movimento" --> string em que é a primeira palavra e define a string interia como string de poses.
    pose_da_perna --> variável com a pose atual das pernas
    pose_do_braço --> variável com a pose atual dos braços
    '''
    arduino.write(('Movimento ' + str(pose_perna) + " " + str(pose_braco) +"\n").encode("UTF-8") )  
    return 


def envia_string(arduino, string):
    '''
    Função que envia uma string qualquer ao Arduino.
    '''
    arduino.write((str(string) +"\n").encode("UTF-8") )  
    return


def serial_monitora(arduino):
  '''
  Função que monitora serial do Arduino, printando qualquer texto enviado do Arduino ao Python.
  '''
  while True:
    if arduino != None:
      texto_recebido = arduino.readline().decode().strip()
      if texto_recebido != "":
        print(texto_recebido)


def enviar_hue(arduino,hue):
    '''
    Função que envia para o Arduino a variável hue da música.
     '''
    envia_string(arduino, "Hue %d\n"%hue)


def enviar_brightness(arduino, brightness):
    '''
    Função que envia para o Arduino a variável de brightness da música.
    '''
    envia_string(arduino, "Brightness %d\n"%brightness)

def enviar_batida(arduino):
    '''
    Função que envia para o Arduino um indicador de que houve uma batida na música.
    '''
    envia_string(arduino, "Batida\n")
