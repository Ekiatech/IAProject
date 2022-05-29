# -*- coding: utf-8 -*-
''' This is the file you have to modify for the tournament. Your default AI player must be called by this module, in the
myPlayer class.

Right now, this class contains the copy of the randomPlayer. But you have to change this!
'''

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
        print("THE MOVE :")
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

        if self._time > 810:
            print("FAST MOVE : ", self._time)
            move = self.fastMove(self._board)

        else:
            depth = 2
            n = len(self._board.generate_legal_moves())
            if (n < 20):
                depth = 4
            elif n < 10:
                depth = 8
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
                if val <= eval:
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
                if val >= eval:
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
        print("THE MOVE ===============", move)
        b.push(move)
        victory = self.checkVictory(b)
        maxLoop = 100
        i = 0
        while (victory == False or i < maxLoop):
            b.pop()
            moves = b.generate_legal_moves()
            move = choice(moves)
            b.push(move)
            victory = self.checkVictory(b)
            i += 1
        b.pop()
        return move
        
    def checkVictory(self, b):
        if b.is_game_over():
            r = b.result
            if self._mycolor == 1 and r == "0-1":
                return True
            elif self._mycolor == 2 and r == "1-0":
                return True
            else:
                return False

        for m in b.generate_legal_moves():
            b.push(m)
            victory = self.checkVictory(b)
            if victory == False:
                return False
            b.pop()

        return True

    def checkOneWayVictory(self):
        MOVES = self._board.generate_legal_moves
        n = len(MOVES)
        L = []
        for t in range(n//5):
            L.append(choice(MOVES))
            for j in L:
                while(not self._board.is_game_over):
                    self._board.b.push(t)



    def littleMonteCarlo(self):
        MOVES = self._board.generate_legal_moves
        n = len(MOVES)
        L = np.zeros(n)
        for m in MOVES:
            self._board.push(m)


