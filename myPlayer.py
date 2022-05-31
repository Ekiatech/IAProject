# -*- coding: utf-8 -*-
''' This is the file you have to modify for the tournament. Your default AI player must be called by this module, in the
myPlayer class.

Right now, this class contains the copy of the randomPlayer. But you have to change this!
'''

from re import I
from tabnanny import check
import time
import Goban 
from random import choice
from playerInterface import *
import json
import numpy as np

class myPlayer(PlayerInterface):
    ''' Example of a random player for the go. The only tricky part is to be able to handle
    the internal representation of moves given by legal_moves() and used by push() and 
    to translate them to the GO-move strings "A1", ..., "J8", "PASS". Easy!

    '''

    def __init__(self):
        self._board = Goban.Board()
        self._mycolor = None
        self._time = 0
        self._gamesWinner = []
        self._newGamesWinner = []
        self._opponentLastMove = None
        self._checkGamesWinner = True
        self._exactOuverture = False
        self._numberTurn = 0
        self._beginMonteCarlo = 15
        self._beginAdvancedMonteCarlo = 5
        self._depthMonteCarlo = 1
        self._advancedDepthMonteCarlo = 2
        self._numberMaxOfMovesInMonteCarlo = 120
        self._dangerTime = 810
        self._normalDepth = 2
        self._advancedDepth = 4
        self._middleDepth = 3
        self._numberOfMovesForAdvancedDepth = 30
        self._numberOfMovesForMiddleDepth = 50
        self._numberOfMovesForExtraDepth = 5

    #Récupérer les ouvertures du fichier 'games.json'
    def getMovesFromGames(self):
        with open('games.json') as json_data:
            games = json.load(json_data)
        
        for g in games:
            if self._mycolor == 1 and g["winner"] == "B":
                self._gamesWinner.append(g)
                self._newGamesWinner.append(g)
            elif self._mycolor == 2 and g["winner"] == "W":
                self._gamesWinner.append(g)
                self._newGamesWinner.append(g)

        self._newGamesWinner = choice(self._newGamesWinner)


    def getPlayerName(self):
        return "Let's go"

    #Pour suivre exactement une ouverture
    def getMoveFollowingOuvertureExactly(self):
        #Vérifier s'il s'agit du premier coup de la partie
        if self._opponentLastMove == None:
            moves = np.zeros(82)
            for g in self._gamesWinner:
                moves[ self._board.str_to_move(g["moves"][0]) ] += 1
            move = np.argmax(moves)
            self._gamesWinner = [ g for g in self._gamesWinner if g["moves"][0] == self._board.move_to_str(move) ]
            return move
        
        #Vérifier si on doit encore suivre une ouverture, et l'appliquer
        if self._checkGamesWinner == True and self._opponentLastMove != None:
            game = choice(self._gamesWinner)
            if len(game["moves"]) > self._numberTurn:
                move = game["moves"][self._numberTurn]
                self._gamesWinner = [ g for g in self._gamesWinner if self._numberTurn < len(g["moves"]) and g["moves"][self._numberTurn] == move ]
                return self._board.str_to_move(move)
        return False

    #Pour suivre une ouverture
    def getMoveFollowingOuverture(self):
        #Vérifier s'il s'agit du premier coup de la partie
        if self._opponentLastMove == None:
            move = self._newGamesWinner["moves"][0]
            print(self._newGamesWinner)
            return self._board.str_to_move(move)

        #Vérifier si on doit encore suivre l'ouverture, et l'appliquer
        if self._checkGamesWinner == True and self._opponentLastMove != None:
            MOVES = self._board.generate_legal_moves()
            if self._numberTurn >= len(self._newGamesWinner["moves"]):
                return False
            move = self._board.str_to_move(self._newGamesWinner["moves"][self._numberTurn])
            for m in MOVES:
                if m == move:
                    return move
            self._checkGamesWinner = False
        return False

    #Récupération du move à jouer
    def getMove(self):
        #Victoire si on "PASS"
        if self._opponentLastMove == "PASS":
            if (self.checkVictory() == True):
                return -1
        
        #Verifier si le coup "PASS" fait gagner la partie
        self._board.push(-1)
        if (self.checkVictory() == True):
            self._board.pop()
            return -1
        else:
            self._board.pop()
        
        #Utiliser les ouvertures
        if self._exactOuverture == True:
            move = self.getMoveFollowingOuvertureExactly()
            if move != False:
                return move
        else:
            move = self.getMoveFollowingOuverture()
            if move != False:
                return move

        #Si jamais il ne reste plus assez de temps, jouer rapidement
        if self._time > self._dangerTime:
            print("FAST MOVE : ", self._time)
            move = self.fastMove(self._board)

        #Dans les autres cas jouer un coup a l'aide de alphabeta ou MonteCarlo en fonction
        #du nombre de coups qu'il reste
        else:
            MOVES = self._board.generate_legal_moves()
            n = len(MOVES)
            if n == 1:
                return MOVES[0]

            if n < self._beginMonteCarlo and n > self._numberOfMovesForExtraDepth:
                if n < self._beginAdvancedMonteCarlo:
                    depth = self._advancedDepthMonteCarlo
                else:
                    depth = self._depthMonteCarlo
                move = self.littleMonteCarlo(depth)
                return move

            depth = self._normalDepth
            if (n < self._numberOfMovesForMiddleDepth):
                depth = self._middleDepth
            if (n < self._numberOfMovesForAdvancedDepth):
                depth = self._advancedDepth
            if (n < self._numberOfMovesForExtraDepth):
                depth = self._advancedDepth
            (val, move) = self.alphaBeta(self._board, depth, True, 0, -10000, 10000)
            #(val, move) = self.miniMax(self._board, depth, True, 0, n)
            print("Valeur : ", val, "Coup :", move)

        return move

    def getPlayerMove(self):
        t1 = time.time()
        if self._board.is_game_over():
            print("Referee told me to play but the game is over!")
            return "PASS" 
       
        move = self.getMove()
        self._board.push(move)
        print("THE SCORE JUST AFTER THE PUSH", self._board.compute_score())

        print("My current board :")
        self._board.prettyPrint()

        # New here: allows to consider internal representations of moves
        print("I am playing ", self._board.move_to_str(move))
        print("My current board :")
        self._board.prettyPrint()
        tf = time.time() - t1
        self._time += tf
        self._numberTurn += 1
        # move is an internal representation. To communicate with the interface I need to change if to a string
        return Goban.Board.flat_to_name(move) 

    def playOpponentMove(self, move):
        t1 = time.time()
        print("BEFORE OPPONENT MOVE", self._board.compute_score())
        print("Opponent played ", move) # New here
        self._opponentLastMove = move
        self._numberTurn += 1

        #Restreindre le tableau des self._gamesWinner aux parties avec les mêmes coups (exactement)
        if self._checkGamesWinner == True:
            self._gamesWinner = [ g for g in self._gamesWinner if self._numberTurn < len(g["moves"]) and g["moves"][self._numberTurn - 1] == move ]
            if len(self._gamesWinner) == 0 and self._exactOuverture == True:
                self._checkGamesWinner = False
        self._time += time.time() - t1
        # the board needs an internal represetation to push the move.  Not a string
        self._board.push(Goban.Board.name_to_flat(move))

    def newGame(self, color):
        self._mycolor = color
        self._opponent = Goban.Board.flip(color)
        self.getMovesFromGames()

    def endGame(self, winner):
        if self._mycolor == winner:
            print("I won!!!")
        else:
            print("I lost :(!!")

    #Heuristique utilisée avec getScore3()
    def heuristic(self, b):
        stones_on_board = b.diff_stones_board()
        stones_captured = b.diff_stones_captured()
        coeff_board = 1
        coeff_captured = 1
        return coeff_board * stones_on_board + coeff_captured * stones_captured        

    #Heuristique utilisée actuellement
    def getScore(self, b):
        (scoreB, scoreW) = b.compute_score()
        if self._mycolor == 1:
            return scoreB
        else:
            return scoreW

    def getScore2(self, b):
        (nbB, nbW) = (b._nbBLACK, b._nbWHITE)
        if self._mycolor == 1:
            return nbB - nbW
        else:
            return nbW - nbB
    
    def getScore3(self, b):
        score = self.heuristic(b)
        if self._mycolor == 1:
            return score
        else:
            return -score

    #Algorithme minimax qui renvoie la valeur et le coup à effectuer
    def miniMax(self, b, depth, isMaximize, coup):
        if (b.is_game_over() or depth == 0):
            return (self.getScore(b))
        if (isMaximize):
            val = -1000
            for m in b.generate_legal_moves():
                b.push(m)
                eval = self.miniMax(b, depth - 1, False, 0)[0]
                if val <= eval:
                    coup = m
                val = max(val, eval)
                b.pop()
        else:
            val = 1000
            for m in b.generate_legal_moves():
                b.push(m)
                eval = self.miniMax(b, depth - 1, True, 0)[0]
                if val >= eval:
                    coup = m
                val = min(val, eval)
                b.pop()
        return (val, coup)
    
    #Algorithme alphabeta qui renvoie la valeur et le coup à effectuer
    def alphaBeta(self, b, depth, isMaximize, coup, alpha, beta):
        if (b.is_game_over() or depth == 0):
            #print("the score :", self.getScore(b), self._board.move_to_str(coup))
            return (self.getScore(b), coup)
        if (isMaximize):
            val = -1000
            for m in b.generate_legal_moves():
                b.push(m)
                eval = self.alphaBeta(b, depth - 1, False, 0, alpha, beta)[0]
                if val < eval:
                    coup = m
                val = max(val, eval)
                if val >= beta:
                    b.pop() 
                    return (val, coup)
                alpha = max(alpha, val)
                b.pop()
        else:
            val = 1000
            for m in b.generate_legal_moves():
                b.push(m)
                eval = self.alphaBeta(b, depth - 1, True, 0, alpha, beta)[0]
                if val > eval:
                    coup = m
                val = min(val, eval)
                if alpha >= val:
                    b.pop() 
                    return (val, coup)
                beta = min(beta, val)
                b.pop()
        return (val, coup)

    #Fonction pour jouer très rapidement un coup
    def fastMove(self, b):
        moves = b.generate_legal_moves()
        move = choice(moves)
        b.push(move)
        victory = self.checkOneWayVictory(0)
        maxLoop = 100
        i = 0
        while (victory == False or i < maxLoop):
            b.pop()
            moves = b.generate_legal_moves()
            move = choice(moves)
            b.push(move)
            victory = self.checkOneWayVictory(0)
            i += 1
        b.pop()
        return move
    
    #Verifier si en jouant des coups aléatoires à partir du plateau actuel
    #on gagne ou perd la partie
    def checkOneWayVictory(self, n):
        if self._board.is_game_over():
            return self.checkVictory()
        
        if n > self._numberMaxOfMovesInMonteCarlo:
            return False

        MOVES = self._board.generate_legal_moves()
        move = choice(MOVES)
        self._board.push(move)
        isVictory = self.checkOneWayVictory(n+1)
        self._board.pop()
        return isVictory

    #Renvoie True si on gagne la partie, False si on perd la partie
    def checkVictory(self):
        r = self._board.result()
        if self._mycolor == 1 and r == "0-1":
            return True
        elif self._mycolor == 2 and r == "1-0":
            return True
        else:
            return False
    
    #Fonction qui effectue le MonteCarlo avec une profondeur
    def theMonteCarlo(self, depth, numberVictory, N):
        if self._board.is_game_over():
            result = self.checkVictory()
            if result == True:
                return N, numberVictory+1
            else:
                return N, numberVictory

        if depth == 0:
            MOVES = self._board.generate_legal_moves()
            n = len(MOVES)
            print("Last longueur moves:", n)
            for _ in range(n):
                    N += 1
                    move = choice(MOVES)
                    self._board.push(move)
                    numberVictory += self.checkOneWayVictory(0) == True
                    self._board.pop()
            return (N, numberVictory)
        else:
            MOVES = self._board.generate_legal_moves()
            n = len(MOVES)
            print("LOngueur Moves :", n)
            for m in MOVES:
                self._board.push(m)
                N, numberVictory = self.theMonteCarlo(depth - 1, numberVictory, N)
                self._board.pop()
        return (N, numberVictory)

    #Fonction qui pour chaque coup possible à effectuer renvoie 
    # la probabilite de victoire
    def aWayFromMonteCarlo(self, depth):
        if self._board.is_game_over():
            if self.checkVictory() == True:
                return 1000
            else:
                return 0

        (N, numberVictory) = self.theMonteCarlo(depth, 0, 0)
        if depth == 0:
            N = 1
        if N == 0:
            return 0
        print("ON A :", N, numberVictory)
        return numberVictory / N

    #Fonction qui renvoie le coup à effectuer apres le calcul de MonteCarlo
    def littleMonteCarlo(self, depth):
        MOVES = self._board.generate_legal_moves()
        n = len(MOVES)
        L = np.zeros(n)
        for i in range(n):
            self._board.push(MOVES[i])
            L[i] = self.aWayFromMonteCarlo(depth)
            print(L[i])
            self._board.pop()
        
        #Le coup à prendre est celui avec la plus forte probabilité de gagner
        indexMove = np.argmax(L)
        move = int(MOVES[indexMove])
        if L[indexMove] < 0.00001:
            move = choice(MOVES)
        print(L[indexMove])
        return move