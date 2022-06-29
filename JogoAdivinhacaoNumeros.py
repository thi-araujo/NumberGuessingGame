#---------------------------------------JOGO ADIVINHAÇÃO DE NÚMEROS----------------------------------------------------

import random
attempts_list = []
def show_score():
    if len(attempts_list) <= 0:
        print("Ate o momento atual não existe pontuação alta, é sua vez para o ponta pé inicial ")