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
        self._opponentLastMove = None
        self._checkGamesWinner = True
        self._numberTurn = 0
        self._beginMonteCarlo = 15
        self._beginAdvancedMonteCarlo = 5
        self._depthMonteCarlo = 1
        self._advancedDepthMonteCarlo = 3
        self._dangerTime = 810
        self._normalDepth = 2
        self._advancedDepth = 4
        self._middleDepth = 3
        self._numberOfMovesForAdvancedDepth = 30
        self._numberOfMovesForMiddleDepth = 50

    def getMovesFromGames(self):
        with open('games.json') as json_data:
            games = json.load(json_data)
        
        for g in games:
            if self._mycolor == 1 and g["winner"] == "B":
                self._gamesWinner.append(g)
            elif self._mycolor == 2 and g["winner"] == "W":
                self._gamesWinner.append(g)

    def getPlayerName(self):
        return "Coralie X Quentin"

    def getMove(self):
        print("THE MOVE :", self._time)
        print("NUMBER PIERRES : ", self._board._nbBLACK, self._board._nbWHITE)
        if self._opponentLastMove == "PASS":
            if (self.checkVictory() == True):
                return -1

        if self._opponentLastMove == None:
            moves = np.zeros(82)
            for g in self._gamesWinner:
                moves[ self._board.str_to_move(g["moves"][0]) ] += 1
            move = np.argmax(moves)
            self._gamesWinner = [ g for g in self._gamesWinner if g["moves"][0] == self._board.move_to_str(move) ]
            print(self._gamesWinner)
            return move
        
        if self._checkGamesWinner == True and self._opponentLastMove != None:
            game = choice(self._gamesWinner)
            if len(game["moves"]) > self._numberTurn:
                move = game["moves"][self._numberTurn]
                self._gamesWinner = [ g for g in self._gamesWinner if self._numberTurn < len(g["moves"]) and g["moves"][self._numberTurn] == move ]
                return self._board.str_to_move(move)

        if self._time > self._dangerTime:
            print("FAST MOVE : ", self._time)
            move = self.fastMove(self._board)

        else:
            n = len(self._board.generate_legal_moves())
            if n < self._beginMonteCarlo:
                if n < self._beginAdvancedMonteCarlo:
                    depth = self._advancedDepthMonteCarlo
                else:
                    depth = self._depthMonteCarlo
                move = self.littleMonteCarlo(depth)
                return move

            depth = self._normalDepth
            n = len(self._board.generate_legal_moves())
            if (n < self._numberOfMovesForMiddleDepth):
                depth = self._middleDepth
            if (n < self._numberOfMovesForAdvancedDepth):
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
        print("Opponent played ", move) # New here
        self._opponentLastMove = move
        self._numberTurn += 1

        if self._checkGamesWinner == True:
            self._gamesWinner = [ g for g in self._gamesWinner if self._numberTurn < len(g["moves"]) and g["moves"][self._numberTurn - 1] == move ]
            if len(self._gamesWinner) == 0:
                self._checkGamesWinner = False
        print("AFTER: ", self._gamesWinner)
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

    def miniMax(self, b, depth, isMaximize, coup):
        if (b.is_game_over() or depth == 0):
            return (self.getScore(b), coup)
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
    
    def alphaBeta(self, b, depth, isMaximize, coup, alpha, beta):
        if (b.is_game_over() or depth == 0):
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

    def fastMove(self, b):
        moves = b.generate_legal_moves()
        move = choice(moves)
        b.push(move)
        victory = self.checkOneWayVictory()
        maxLoop = 100
        i = 0
        while (victory == False or i < maxLoop):
            b.pop()
            moves = b.generate_legal_moves()
            move = choice(moves)
            b.push(move)
            victory = self.checkOneWayVictory()
            i += 1
        b.pop()
        return move
        
    def checkOneWayVictory(self):
        if self._board.is_game_over():
            return self.checkVictory()
        
        MOVES = self._board.generate_legal_moves()
        move = choice(MOVES)
        self._board.push(move)
        isVictory = self.checkOneWayVictory()
        self._board.pop()
        return isVictory

    def checkVictory(self):
        r = self._board.result()
        if self._mycolor == 1 and r == "0-1":
            return True
        elif self._mycolor == 2 and r == "1-0":
            return True
        else:
            return False
               
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
                    numberVictory += self.checkOneWayVictory() == True
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

    def aWayFromMonteCarlo(self, depth):
        if self._board.is_game_over():
            return 1000
        (N, numberVictory) = self.theMonteCarlo(depth, 0, 0)
        if depth == 0:
            N = 1
        print("ON A :", N, numberVictory)
        return numberVictory / N

    def littleMonteCarlo(self, depth):
        MOVES = self._board.generate_legal_moves()
        n = len(MOVES)
        print(MOVES)
        print(n)
        L = np.zeros(n)
        for i in range(n):
            self._board.push(MOVES[i])
            L[i] = self.aWayFromMonteCarlo(depth)
            print(L[i])
            self._board.pop()
        
        indexMove = np.argmax(L)
        print()
        print(L[indexMove])
        return int(MOVES[indexMove])