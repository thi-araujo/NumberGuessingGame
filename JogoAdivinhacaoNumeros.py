#---------------------------------------JOGO ADIVINHAÇÃO DE NÚMEROS----------------------------------------------------

import random

lista_tentativa = []

def show_score():
    if len(lista_tentativa) <= 0:
        print("Ate o momento atual não existe pontuação alta, é sua vez para o ponta pé inicial ")
	else:
		print("A pontuação mais alta atual é de {} tentativas".format(min(lista_tentativa)))

def start_game():
	random_number = int(random.randint(1, 10))
	print("Olá Jogador! Seja Bem Vindo ao Jogp de Adivinhação!")

player_name = input("Digite seu nome: ")

wanna_play = input("Olá, {}, voce gostaria de jogar o Game de Adivinhação? (Digite: Sim/Não) ".format(player_name))

# Esta é a Função show_score

tentativa = 0

show_score()

while wanna_play.lower() == "sim":
    try:
        guess = input("Escolha um número entre 1 e 10")
    if int(guess) < 1 or int(guess) > 10:
        raise ValueError("Por favor, adivinhe um número dentro do intervalo fornecido")
    if int(guess) == random_number:
        print("Excelente! Você compreendeu!")

tentativa += 1

lista_tentativa.append(tentativa)
print("Foram necessárias {} tentativas".format(tentativa))

tentativa = 0

jogar_de_novo = input("Gostaria de jogar novamente? Digite Sim/Não")
tentativa = 0
show_score()
random_number = int(random.randint(1,10))

    if jogar_de_novo.lower() == "Não":
        print("Isso é legal, tenha um excelente dia!")
        break

    elif int(guess) > random_number:
        print("É mais baixo")

    tentativa += 1

    elif int(guess) < random_number:

    print("É mais alto")

    tentativa += 1

    except ValueError as err:
    print("Oh não!!! Esse não é um valor válido. Por favor, tente novamente....")
    print("({})".format(err))



    else:
        print("Isso é legal tenha uma ótima tentativa e um excelente jogo")

    if __name__ == '__main__':
        start_game()




def show_score():
    if len(lista_tentativa) <= 0:
        print("Ate o momento atual não existe pontuação alta, é sua vez para o ponta pé inicial ")
	else:
		print("A pontuação mais alta atual é de {} tentativas".format(min(lista_tentativa)))



#===============================================FIM DO JOGO=====================================================================