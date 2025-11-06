import math
import cv2

__all__ = ['calcula_angulo', 'funcao_texto']


def calcula_angulo(a_x: float, a_y: float, b_x: float, b_y: float):
    '''
    Função que calcula angulo entre um vetor e um vetor vertical a partir de 2 pontos.

    Calculo efetuado a partir da seguinte fórmula: cos θ = (u.v)/(|u||v|)

    O ponto (a) deve ser o ponto mais baixo, que se mexe em relação a referência
    O ponto (b) deve ser o ponto de origem (o ponto mais alto, que não mexe)

    Exemplo: Ponto (a) é o mão direita (ponto de refêrencia móvel) e ponto (b) é o ombro direito (ponto imóvel)
    '''

    # Calculo dos vetores
    vetor_ab = (b_x - a_x, b_y - a_y) # Tupla com coordenadas do vetor
    vetor_vertical = (0,-1) # Vetor (0,-1) pois preciso pegar o ângulo entre a reta (passando pelos dois pontos) e uma reta vertical

    # Calculo dos componentes da formula
    produto_escalar = vetor_ab[0] * vetor_vertical[0] + vetor_ab[1] * vetor_vertical[1] # (u.v)
    norma_ab = math.sqrt(vetor_ab[0]**2 + vetor_ab[1]**2) # (|u|)
    norma_v_vertical = math.sqrt(vetor_vertical[0]**2 + vetor_vertical[1]**2) # (|v|)

    if norma_ab * norma_v_vertical ==0 :
        return 0
    
    cos_angulo = produto_escalar / (norma_ab * norma_v_vertical) # cos θ 
    angulo_radianos = math.acos(cos_angulo) # arcos(cos(θ))
    angulo_graus = math.degrees(angulo_radianos) # Porque a função acos retorna em radiano


    return round(angulo_graus, 2) # Retorna apenas duas casas decimais


def funcao_texto(texto, cor, img, coord1,coord2):
   '''
   Função que posiciona a legenda na tela de exibição do mediapipe.

   Argumentos da função:
   texto => texto que será exibido na tela
   cor => cor do retangulo que ficará atrás do texto
   img => próprio da função
   coord1 e coord2 => define posicionamento do texto
   '''

   # Definição das propriedades do texto
   font = cv2.FONT_HERSHEY_SIMPLEX
   font_scale = 0.7 
   thickness = 2

   # Obtendo o tamanho do texto
   (text_width, text_height), baseline = cv2.getTextSize(texto, font, font_scale, thickness)

   # Coordenadas do canto superior esquerdo
   x, y = coord1, coord2

   # Calculando o retângulo com base no tamanho do texto
   top_left = (x, y - text_height - baseline)
   bottom_right = (x + text_width, y + baseline)

   # Desenhando o retângulo
   cv2.rectangle(img, top_left, bottom_right, cor, -1)

   cv2.putText(img, texto, (x, y), font, font_scale, (255, 255, 255), thickness)