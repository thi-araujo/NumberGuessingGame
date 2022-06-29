#---------------------------------------JOGO ADIVINHAÇÃO DE NÚMEROS----------------------------------------------------

import random
lista_de_tentativas = []
def show_score():
    if len(attempts_list) <= 0:
        print("Ate o momento atual não existe pontuação alta, é sua vez para o ponta pé inicial ")

    else:
        print("A pontuação mais alta é de {} tentativas".format(min(lista_de_tentativas)))