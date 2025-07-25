import hashlib
import json
import uuid
from flask import Flask, request
import pymongo

VERSION = "0.0.3-release"
WIDTH = 31
mongo = pymongo.MongoClient("mongodb://db:27017")
app = Flask(__name__)
db = mongo['db']
userdb = db['users']


class match:
    def __init__(self, gamerId):
        self.match_id = str(uuid.uuid4()).split("-")[0]
        self.match_type = 0
        self.chess_board = []
        self.gamerA = gamerId
        self.gamerB = 0
        self.black_gamer = 0
        self.white_gamer = 0
        self.playerNow = self.black_gamer
        tmp = []
        for i in range(WIDTH):
            tmp.append(0)
        for i in range(WIDTH):
            self.chess_board.append(tmp.copy())
        self.finished = 0
        self.winner = "0"

    def checkWin(self, x, y):
        flag_x = 0
        flag_y = 0
        flag_positive = 0
        flag_negative = 0
        player = self.chess_board[y][x]
        if player == 0:
            return False
        # X轴正方向判断
        for i in range(x + 1, max(31, x + 5)):
            if (player != self.chess_board[y][i]):
                break
            elif (i == x + 4):

                return True

            else:
                flag_x += 1
                # X轴负方向判断
        for i in range(x - 1, min(-1, x - 5), -1):
            if (player != self.chess_board[y][i]):
                break
            elif (i == x - 4):
                return True

            else:
                flag_x += 1

        if flag_x >= 4:
            return True
        # Y轴正方向判断
        for i in range(y + 1, max(31, y + 5)):
            if (player != self.chess_board[i][x]):
                break
            elif (i == y + 4):
                return True
            else:
                flag_y += 1

        # Y轴负方向判断
        for i in range(y - 1, min(-1, y - 5), -1):
            if (player != self.chess_board[i][x]):
                break
            elif (i == y - 4):
                return True
            else:
                flag_y += 1

        if flag_y >= 4:
            return True

        # y = x 方向判断：x++ y--
        for i, j in zip(range(x + 1, min(31, x + 5)), range(y - 1, max(-1, y - 5), -1)):
            if player != self.chess_board[j][i]:
                break
            elif i == x + 4:

                return True
            else:
                flag_positive += 1

                # y = x 方向判断：x-- y++
        for i, j in zip(range(x - 1, max(-1, x - 5), -1), range(y + 1, min(31, y + 5))):
            if player != self.chess_board[j][i]:
                break
            elif i == x - 4:
                return True
            else:
                flag_positive += 1

        if flag_positive >= 4:
            return player

        # y = -x 方向判断：x++ y++
        for i, j in zip(range(x + 1, min(31, x + 5)), range(y + 1, min(31, y + 5))):
            if player != self.chess_board[j][i]:
                break
            elif i == x + 4:
                return True
            else:
                flag_negative += 1

        # y = -x 方向判断：x-- y--
        for i, j in zip(range(x - 1, max(-1, x - 5), -1), range(y - 1, max(-1, y - 5), -1)):
            if player != self.chess_board[j][i]:
                break
            elif i == x - 4:
                return True
            else:
                flag_negative += 1

        if flag_negative >= 4:
            return True
        return False

    def setChess(self, gamerId, x, y):
        if self.chess_board[y][x] == 0:
            if self.playerNow == gamerId:
                if gamerId == self.black_gamer:
                    self.chess_board[y][x] = 1
                    self.playerNow = self.white_gamer
                elif gamerId == self.white_gamer:
                    self.chess_board[y][x] = 2
                    self.playerNow = self.black_gamer
                return "OK"
            else:
                return "NO"
        else:
            return "NO"

    def getChess(self):
        tmp = ""
        for i in self.chess_board:
            for j in i:
                tmp += str(j)
        #with open("{}.txt".format(self.match_id), "a+") as f:
        #    f.write("\n"+tmp)
        return tmp

    def getPlayerNow(self):
        return self.playerNow

    def checkWinner(self):
        for y in range(len(self.chess_board)):
            for x in range(len(self.chess_board[y])):
                if (self.checkWin(x, y)):
                    if self.chess_board[y][x] == 1:
                        self.finished = 1
                        return "black"
                    elif self.chess_board[y][x] == 2:
                        self.finished = 1
                        return "white"
        return False


matches = []
print(
    f"""
    Chess Server {VERSION}
    Commit-2024-6-1-26efd3eb5031171ac6315146ccdb14d8d57b84e6
    This Program is licensed under MIT License.
    For more information, see the LICENSE file.
    
    This is a subproject of 5-Chess, a homework assignment for the Fundamentals of Programming (I) course 
    at Nanjing University of Science and Technology.
    See client at https://github.com/ExSaltedFishPro/5chess
""")


def verify(userId, password):
    data = userdb.find_one({"username": userId})
    if not data:
        return 0
    if data["hash"] == hashlib.md5(password.encode()).hexdigest():
        return 1
    else:
        return 0


@app.route('/')
def version():
    return 'chessServer-{}'.format(VERSION)


@app.route('/api/<name>', methods=['POST'])
def api(name):
    if name == "newGame":
        userId = request.form.get('userId')
        password = request.form.get('password')
        if not verify(userId, password):
            return "unauthorized"
        newMatch = match(userId)
        matches.append(newMatch)
        return newMatch.match_id
    if name == "joinGame":
        userId = request.form.get('userId')
        matchId = request.form.get('matchId')
        password = request.form.get('password')
        if not verify(userId, password):
            return "unauthorized"
        for i in matches:
            if i.match_id == matchId:
                i.gamerB = userId
                return "0"
    if name == "chooseColor":
        userId = request.form.get('userId')
        matchId = request.form.get('matchId')
        password = request.form.get('password')
        if not verify(userId, password):
            return "unauthorized"
        color = request.form.get('color')
        for i in matches:
            if i.match_id == matchId and userId in [i.gamerA, i.gamerB]:
                if color == "white":
                    if i.white_gamer == 0:
                        i.white_gamer = userId
                        return "white"
                    else:
                        i.playerNow = userId
                        i.black_gamer = userId
                        return "black"
                if color == "black":
                    if i.black_gamer == 0:
                        i.playerNow = userId
                        i.black_gamer = userId
                        return "black"
                    else:
                        i.white_gamer = userId
                        return "white"
                return "0"
    if name == "register":
        userId = request.form.get('userId')
        password = request.form.get('password')
        if userdb.find_one({"username": userId}):
            return "registered"
        userdb.insert_one({
            'username': userId,
            'hash': hashlib.md5(password.encode()).hexdigest()
        })
        return "OK"
    return "1"


@app.route('/game/<id>/<operation>', methods=['POST'])
def game(id, operation):
    if operation == "setChess":
        userId = request.form.get('userId')
        password = request.form.get('password')
        if not verify(userId, password):
            return "unauthorized"
        matchId = id
        location = request.form.get('location')
        x = int(location.split(",")[0])
        y = int(location.split(",")[1])
        for i in matches:
            if i.match_id == matchId:
                return i.setChess(userId, x, y)
        return "NotExist"
    elif operation == "getBoard":
        for i in matches:
            if i.match_id == id:
                tmp = i.checkWinner()
                if tmp:
                    return tmp
                return i.getChess()
        return "NotExist"
    elif operation == "getStatus":
        for i in matches:
            if id == i.match_id:
                if 0 in [i.gamerA, i.gamerB]:
                    return "Unstarted"
                elif i.finished == 1:
                    return "Over"
                else:
                    return "OK"
    elif operation == "getPlayerNow":
        for i in matches:
            if id == i.match_id:
                if i.finished:
                    return "FINISHED!"
                return str(i.getPlayerNow())
        return "NotExist"
    elif operation == "getForceBoard":
        for i in matches:
            if i.match_id == id:
                return i.getChess()
        return "NotExist"


@app.route('/info')
def info():
    info = []
    for i in matches:
        data = {"id": i.match_id,
                "gamerA": str(i.gamerA),
                "gamerB": str(i.gamerB),
                "status": ""}
        if i.finished == 1:
            data["status"] = "Finished"
        elif 0 in [i.gamerA, i.gamerB]:
            data["status"] = "Unstarted"
        else:
            data["status"] = "Playing"
        info.append(data)
    return json.dumps(info)



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
