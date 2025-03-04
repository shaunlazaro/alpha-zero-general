from __future__ import print_function
import sys
sys.path.append('..')
from Game import Game
import numpy as np
import requests
import json
placementStr = open("placement.json").read()

class ttGame(Game):
    _valid_chars = [0,4,5,6,7,8,9,10,11,12,13,16,17,18,19,21,22,23,24,26,30,31,32,33,34,35,37,38]
    
    def __init__(self):
        self._num_chars = len(self._valid_chars)

    def getBoardSize(self):
        return (self._num_chars+1,5,10)

    def getInitBoard(self):
        board = np.zeros(self.getBoardSize())
        board[-1,:,:5] = 1
        board[-1,:,5:] = -1
        return board

    def getActionSize(self):
        return self._num_chars*5*5

    def getValidMoves(self, board, player):
        if player == 1:
            pBoard = board[:self._num_chars,:,:5].copy()
        else:
            pBoard = board[:self._num_chars,:,5:].copy()

        seenCharIndexes = np.where(pBoard == 1)[0]

        for h in range(5):
            for v in range(5):
                pBoard[:,h,v] = 0 if (1 in pBoard[:,h,v]) else 1

        for char_i in seenCharIndexes:
            pBoard[char_i,:,:] = 0
        return pBoard.flatten()


    def getNextState(self, board, player, action): # player == 1 or -1
        #assert player == board[-1,0,0], f"{player}, {board[-1,0,0]}"
        move = np.zeros(self.getActionSize())
        move[action] = 1
        move = move.reshape((self._num_chars,5,5))
        newBoard = np.copy(board)
        if player == 1:
            newBoard[:self._num_chars,:,:5] += move
        else:
            newBoard[:self._num_chars,:,5:] += move

        return (newBoard, -player)

    def _maxPrestige(self, charType):
        #there is currently a unity side hack to fix this to 10 star
        return -1

    def _createPlacementJsonStr(self, board):
        formatData = []
        setValuesP1 = np.where(board[:self._num_chars,:,:5] == 1)
        setValuesP2 = np.where(board[:self._num_chars,:,5:] == 1)
        if board[-1,0,0] == -1:
            setValuesP1, setValuesP2 = setValuesP2, setValuesP1

        setValues = [[*setValuesP1[0],*setValuesP2[0]],[*setValuesP1[1],*setValuesP2[1]],[*setValuesP1[2],*setValuesP2[2]]]
        for char_i,h,v in zip(*setValues):
            curCharType = self._valid_chars[char_i]
            formatData.extend([v*5+h+1, curCharType, 240, self._maxPrestige(curCharType)])
        return placementStr % tuple(formatData)

    def _checkServerWin(self, board):
        assert board[-1,0,0] == 1
        placementJsonStr = self._createPlacementJsonStr(board)
        while True:
            try:
                response = requests.get("http://192.168.0.24:8007/simulate/1337/", data=placementJsonStr, timeout=10)
                if response.status_code == 200:
                    break
                else:
                    print(f"response code {response.status_code}")
            except KeyboardInterrupt:
                print("exiting")
                sys.exit()
            except:
                print("timed out")
        
        assert response.status_code == 200
        return response.content == b"True"

    def getGameEnded(self, board, player):
        numPlaced = np.sum(board)
        assert np.sum(board) <= 10
        if numPlaced < 10:
            return 0
        assert self._isBoardValid(board), self.stringRepresentation(board)
        isP1Win = self._checkServerWin(board)
        return 1 if isP1Win == (board[-1,0,0] == 1) else -1

    def getCanonicalForm(self, board, player):
        newBoard = np.copy(board)
        if player == 1:
            return newBoard
        newBoard[:,:,:5], newBoard[:,:,5:] = newBoard[:,:,5:], newBoard[:,:,:5].copy()
        return newBoard

    def getSymmetries(self, board, pi):
        return [(board, pi)]

    def _isBoardValid(self, board):
        setValuesP1 = np.where(board[:self._num_chars,:,:5] == 1)
        setValuesP2 = np.where(board[:self._num_chars,:,5:] == 1)
        def checkForPlayer(setValues):
            seenChars = set()
            seenPos = set()
            for char_i, h, v in zip(*setValuesP1):
                pos = v*5+h+1
                char = self._valid_chars[char_i]
                if pos in seenPos or char in seenChars:
                    return False
                seenPos.add(pos)
                seenChars.add(char)
            return True
        return checkForPlayer(setValuesP1) and checkForPlayer(setValuesP2)

    def stringRepresentation(self, board):
        ret = []
        ret.append(f"Player {board[-1,0,0]}")
        setValuesP1 = np.where(board[:self._num_chars,:,:5] == 1)
        for char_i, h, v in zip(*setValuesP1):
            ret.append(f"{h+1+v*5}: {self._valid_chars[char_i]}")

        ret.append(f"Player {board[-1,-1,-1]}")
        setValuesP2 = np.where(board[:self._num_chars,:,5:] == 1)
        for char_i, h, v in zip(*setValuesP2):
            ret.append(f"{h+1+v*5}: {self._valid_chars[char_i]}")
        return "\n".join(ret)

    @staticmethod
    def display(board):
        n = board.shape[0]
        print("")
        print(">S--------------------<")
        _num_chars = len(ttGame._valid_chars)
        ret = []
        ret.append(f"Player {board[-1,0,0]}")
        setValuesP1 = np.where(board[:_num_chars,:,:5] == 1)
        for char_i, h, v in zip(*setValuesP1):
            ret.append(f"{h+1+v*5}: {ttGame._valid_chars[char_i]}")

        ret.append(f"Player {board[-1,-1,-1]}")
        setValuesP2 = np.where(board[:_num_chars,:,5:] == 1)
        for char_i, h, v in zip(*setValuesP2):
            ret.append(f"{h+1+v*5}: {ttGame._valid_chars[char_i]}")
        print("\n".join(ret))

        print("<E-------------------->")



