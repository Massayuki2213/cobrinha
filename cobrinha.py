"""Cobrinha — jogo da cobrinha no terminal, estilo cmd.

Controles: setas ou WASD para mover, R para reiniciar, Q ou ESC para sair.
Sem dependencias externas: roda direto com `python cobrinha.py` no Windows.
"""

import msvcrt
import os
import random
import sys
import time

LARGURA = 40
ALTURA = 20
VELOCIDADE_INICIAL = 0.12  # segundos por passo
VELOCIDADE_MINIMA = 0.05
ACELERACAO = 0.004  # quanto mais rapido a cada comida

RESET = "\x1b[0m"
VERDE = "\x1b[92m"
VERMELHO = "\x1b[91m"
AMARELO = "\x1b[93m"
CIANO = "\x1b[96m"

CIMA, BAIXO, ESQUERDA, DIREITA = (0, -1), (0, 1), (-1, 0), (1, 0)
OPOSTA = {CIMA: BAIXO, BAIXO: CIMA, ESQUERDA: DIREITA, DIREITA: ESQUERDA}

SETAS = {"H": CIMA, "P": BAIXO, "K": ESQUERDA, "M": DIREITA}
WASD = {"w": CIMA, "s": BAIXO, "a": ESQUERDA, "d": DIREITA}


def ler_acao():
    """Le a ultima tecla pressionada sem bloquear o jogo."""
    acao = None
    while msvcrt.kbhit():
        ch = msvcrt.getwch()
        if ch in ("\x00", "\xe0"):  # prefixo das setas no Windows
            acao = SETAS.get(msvcrt.getwch(), acao)
        elif ch.lower() in WASD:
            acao = WASD[ch.lower()]
        elif ch in ("\x1b", "q", "Q"):
            acao = "sair"
        elif ch in ("r", "R"):
            acao = "reiniciar"
    return acao


def sortear_comida(cobra):
    livres = [
        (x, y)
        for x in range(LARGURA)
        for y in range(ALTURA)
        if (x, y) not in cobra
    ]
    return random.choice(livres) if livres else None


def desenhar(cobra, comida, pontos, recorde, fim_de_jogo):
    corpo = set(cobra)
    cabeca = cobra[0]

    linhas = [CIANO + "+" + "-" * LARGURA + "+" + RESET]
    for y in range(ALTURA):
        celulas = []
        for x in range(LARGURA):
            pos = (x, y)
            if pos == cabeca:
                celulas.append(VERDE + "@" + RESET)
            elif pos in corpo:
                celulas.append(VERDE + "o" + RESET)
            elif pos == comida:
                celulas.append(VERMELHO + "*" + RESET)
            else:
                celulas.append(" ")
        linhas.append(CIANO + "|" + RESET + "".join(celulas) + CIANO + "|" + RESET)
    linhas.append(CIANO + "+" + "-" * LARGURA + "+" + RESET)

    placar = f" Pontos: {AMARELO}{pontos}{RESET}   Recorde: {AMARELO}{recorde}{RESET}"
    linhas.append(placar)
    if fim_de_jogo:
        linhas.append(VERMELHO + " FIM DE JOGO!" + RESET + "  [R] jogar de novo   [Q] sair ")
    else:
        linhas.append(" Setas/WASD para mover   [R] reiniciar   [Q] sair ")

    sys.stdout.write("\x1b[H" + "\n".join(linhas) + "\n")
    sys.stdout.flush()


def jogar(recorde):
    """Roda uma partida e retorna (pontos, sair?)."""
    meio = (LARGURA // 2, ALTURA // 2)
    cobra = [meio, (meio[0] - 1, meio[1]), (meio[0] - 2, meio[1])]
    direcao = DIREITA
    comida = sortear_comida(cobra)
    pontos = 0
    velocidade = VELOCIDADE_INICIAL

    while True:
        inicio = time.monotonic()
        desenhar(cobra, comida, pontos, max(recorde, pontos), fim_de_jogo=False)

        # espera o tempo do passo, reagindo ao teclado nesse meio tempo
        while time.monotonic() - inicio < velocidade:
            acao = ler_acao()
            if acao == "sair":
                return pontos, True
            if acao == "reiniciar":
                return pontos, False
            if isinstance(acao, tuple) and acao != OPOSTA[direcao]:
                direcao = acao
            time.sleep(0.005)

        nova_cabeca = (cobra[0][0] + direcao[0], cobra[0][1] + direcao[1])
        bateu_na_parede = not (0 <= nova_cabeca[0] < LARGURA and 0 <= nova_cabeca[1] < ALTURA)
        bateu_no_corpo = nova_cabeca in cobra[:-1]  # a cauda sai do lugar no mesmo passo

        if bateu_na_parede or bateu_no_corpo:
            desenhar(cobra, comida, pontos, max(recorde, pontos), fim_de_jogo=True)
            while True:
                acao = ler_acao()
                if acao == "sair":
                    return pontos, True
                if acao == "reiniciar":
                    return pontos, False
                time.sleep(0.02)

        cobra.insert(0, nova_cabeca)
        if nova_cabeca == comida:
            pontos += 1
            velocidade = max(VELOCIDADE_MINIMA, velocidade - ACELERACAO)
            comida = sortear_comida(cobra)
            if comida is None:  # encheu a tela: vitoria total
                desenhar(cobra, comida, pontos, max(recorde, pontos), fim_de_jogo=True)
                return pontos, True
        else:
            cobra.pop()


def main():
    os.system("")  # habilita codigos ANSI no console do Windows
    sys.stdout.write("\x1b]0;Cobrinha\x07")  # titulo da janela
    sys.stdout.write("\x1b[2J\x1b[?25l")  # limpa a tela e esconde o cursor
    recorde = 0
    try:
        while True:
            pontos, sair = jogar(recorde)
            recorde = max(recorde, pontos)
            if sair:
                break
            sys.stdout.write("\x1b[2J")
    finally:
        sys.stdout.write("\x1b[?25h" + RESET + "\n")  # mostra o cursor de novo
        sys.stdout.flush()
    print(f"Ate a proxima! Recorde da sessao: {recorde}")


if __name__ == "__main__":
    main()
