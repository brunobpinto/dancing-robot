from math import *

__all__ = ['distancia']

def distancia(coordx_1,coordx_2,coordy_1,coordy_2):
    '''
    Função que calcula distancia entre dois pontos.
    '''
    dist = sqrt((coordx_1-coordx_2)**2 + (coordy_1-coordy_2)**2)

    return dist 