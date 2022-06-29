#---------------------------------------JOGO ADIVINHAÇÃO DE NÚMEROS----------------------------------------------------

import random
lista_de_tentativas = []
def show_score():
    if len(attempts_list) <= 0:
        print("Ate o momento atual não existe pontuação alta, é sua vez para o ponta pé inicial ")

    else:
        print("A pontuação mais alta é de {} tentativas".format(min(lista_de_tentativas)))

def start_game():
    random_number = int(random.randint(1, 10))
    print("Olá Jogador Seja Bem Vindo ao Jogo de Adivinção")

    nome_jogador = input("Digite seu Nome: ")

    quer_jogar = input("Olá, {}, você gostaria de jogar o Jogo de Adivinhação? (Digite Sim/Não) ".format(nome_jogador))


