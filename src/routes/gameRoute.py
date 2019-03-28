'''
from flask import Flask, request, json, jsonify
import os
from pathlib import Path
from random import randint

from . import router, baseLocation
from ..utils.file import readFile, createFile, writeFile

# ngambil alamat file 
quizFileLocation = baseLocation / "data" / "quiz-file.json"
questionFileLocation = baseLocation / "data" / "question-file.json"
gameFileLocation = baseLocation / "data" / "game-file.json"

#################################################################################
# CREATE GAME
#################################################################################
@router.route('/game', methods = ['POST'])
def createGame():
    body = request.json

    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }

    try : 
        quizData = readFile(quizFileLocation)
    except:
        response["message"] = "gagal load quiz file mz"
    else:
        isQuizFound = False
        # gameInfo = {}
        for quiz in quizData["quizzes"]:
            if (quiz["quiz-id"] == body["quiz-id"]):
                isQuizFound = True
                gameInfo = quiz
                break
        
        if isQuizFound:
            gameInfo["game-pin"] = randint(10000,999999)
            gameInfo["user-list"] = []
            gameInfo["leaderboard"] = []
            
            response["error"] = False
            response["message"] = "Yaay quiz is found, you're going to play " + gameInfo["quiz-title"]
            response["data"] = gameInfo

            # simpan game ini ke history
            gameData = {
                "game-list": []
            }
            try:
                gameData = readFile(gameFileLocation)
            except:
                print("bakal bikin file game baru")
                
            gameData["game-list"].append(gameInfo)
            toBeWritten = str(json.dumps(gameData))
            writeFile(gameFileLocation,toBeWritten)
        else:            
            response["message"] = "quiz ga ketemu ka"

    return jsonify(response)

#################################################################################
# JOIN GAME
#################################################################################
@router.route('/game/join', methods = ['POST'])
def joinGame():
    body = request.json

    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }

    try:
        gameData = readFile(gameFileLocation)
    except:
        print("gagal load file game")
    else:
        # nyari game nya ada atau ga
        isGameFound = False
        for game in gameData["game-list"] :
            if game["game-pin"] == body["game-pin"] : 
                isGameFound = True
                gameToBePlayed = game
                response["message"] = "ketemuuu kamu join game " + str(gameToBePlayed["game-pin"])
                position = gameData["game-list"].index(gameToBePlayed)
                break

        if isGameFound:
            if body["username"] not in game["user-list"]:
                userData = {
                    "username" : body["username"],
                    "score" : 0
                }
                gameToBePlayed["user-list"].append(body["username"])
                gameToBePlayed["leaderboard"].append(userData)
                gameInfo = gameToBePlayed

                gameData["game-list"][position] = gameInfo
                toBeWritten = str(json.dumps(gameData))
                writeFile(gameFileLocation,toBeWritten)

                response["data"] = gameInfo
                response["message"] += " dengan username " + body["username"]
                response["error"] = False
                
            else:
                response["message"] = "username udah dipakekkkk"
            
        else:
            response["message"] = "game ga adaaaa O____<"

    return jsonify(response)


#################################################################################
# ANSWER GAME
#################################################################################

@router.route('/answer', methods = ['POST'])
def submitAnswer():
    body = request.json

    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }

    try:
        gameData = readFile(gameFileLocation)
    except:
        response["message"] = "gagal load game file"
    else:
        isGameFound = False
        position = -1
        for game in gameData["game-list"] :
            if game["game-pin"] == body["game-pin"] and game["quiz-id"] == body["quiz-id"]: 
                isGameFound = True
                gameToBePlayed = game
                response["message"] = "ketemuuu kamu ngejawab game " + str(gameToBePlayed["game-pin"])
                position = gameData["game-list"].index(gameToBePlayed)
                break

        if isGameFound:
            # udah ketemu game nya, update leaderboard nya
            tempLeaderboard = []
            tempLeaderboard = gameToBePlayed["leaderboard"]

            try:
                questionData = readFile(questionFileLocation)
            except:
                response["message"] = "question file gagal ke load"
            else:
                # ngecek jawaban ke questiondata, sekaligus update score di leaderboard
                # cek dulu quiz dan questionnya ada atau ga
                isQuestionInQuizFound = False
                for question in questionData["questions"] :
                    if (question["quiz-id"] == (body["quiz-id"]) and question["question-id"] == (body["question-id"])) : 
                        isQuestionInQuizFound = True
                        questionPosition = questionData["questions"].index(question)
                        break

                if isQuestionInQuizFound:
                    if (body["username"] in gameToBePlayed["user-list"]):
                        for userData in tempLeaderboard:
                            if (userData["username"] == body["username"]):                    
                                if (question["answer"] == body["answer"]):
                                    response["message"] = "Benarrr"
                                    userData["score"] += 100
                                else:  
                                    response["message"] = "Y salahhhh"
                                    userData["score"] += 0
                                break

                        # write gamefile updated
                        gameData["game-list"][position]["leaderboard"] = tempLeaderboard
                        toBeWritten = str(json.dumps(gameData))
                        writeFile(gameFileLocation,toBeWritten) 
                                
                        response["error"] = False
                        response["data"] = tempLeaderboard
                        
                    else:
                        response["message"] = "km ga join game ini wuoyy"
                        
                else:
                    response["message"] = "ngejawab pertanyaan di kuis apaa gak ada"                     
                
        else:
            response["message"] = "km main game apa ga ketemu"

    return jsonify(response)

#################################################################################
# LEADERBOARDS
#################################################################################
@router.route('/game/leaderboard/<gamePin>')
def viewLeaderboard(gamePin):

    response = {
        "error" : "True",
        "message" : ""
    }

    try:
        gameData = readFile(gameFileLocation)
    except:
        response["message"] = "gagal load game file"
    else:
        isGameFound = False
        for game in gameData["game-list"] :
            if game["game-pin"] == int(gamePin):
                gameFound = game["leaderboard"]
                isGameFound = True                
                break
        
        if isGameFound:
            response["error"] = False
            nData = len(gameFound)
            sortedLeaderboard = []
            while (len(sortedLeaderboard) != nData):
                biggest = gameFound[0]["score"]
                biggestPosition = 0
                for i in range(len(gameFound)):
                    if (gameFound[i]["score"] >= biggest):
                        biggest = gameFound[i]["score"]
                        data = gameFound[i]
                        biggestPosition = i
                sortedLeaderboard.append(data)
                gameFound.pop(biggestPosition)
            
            response["message"] = "Leaderboard game-pin " + gamePin
            response["data"] = sortedLeaderboard
        else:
            response["message"] = "game dgn pin tsb gak adaaa mz"
      
    return jsonify(response)
'''


from flask import Flask, request, json, jsonify
import os
from pathlib import Path
from random import randint

from . import router, baseLocation
from ..utils.file import readFile, createFile, writeFile

from ..utils.models import db, Game, Leaderboard, UserScore, Question

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import exists
from sqlalchemy.orm import load_only

from sqlalchemy import func, and_

# db = SQLAlchemy()

# ngambil alamat file 
quizFileLocation = baseLocation / "data" / "quiz-file.json"
questionFileLocation = baseLocation / "data" / "question-file.json"
gameFileLocation = baseLocation / "data" / "game-file.json"

#################################################################################
# CREATE GAME
#################################################################################
@router.route('/game', methods = ['POST'])
def createGame():
    body = request.json

    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }

    quiz_id = body["quiz_id"]

    game_pin = randint(1000,999999)
    gamePinIsUsed = db.session.query(Game).filter_by(game_pin = game_pin).scalar() is not None
    while(gamePinIsUsed == True):
        game_pin = randint(1000,999999)
        gamePinIsUsed = db.session.query(Game).filter_by(game_pin = game_pin).scalar() is not None
        if (gamePinIsUsed == False):
            break

    try:
        game = Game(
            quiz_id = quiz_id,
            game_pin = game_pin)
        
        db.session.add(game)
        db.session.commit()

        response["message"] = "Game created. Game-id = {}".format(game.game_id) + " Game-pin = {}".format(game.game_pin)
        response["error"] = False
        response["data"] = game.serialise()
    except Exception as e:
        response["message"] =  str(e)
    finally:
        db.session.close()

    return jsonify(response)

#################################################################################
# JOIN GAME
#################################################################################
@router.route('/game/join', methods = ['POST'])
def joinGame():
    body = request.json

    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }

    username =body["username"]
    game_pin = body["game_pin"]

    # cari dl game_id nya, kecuali game_pin nya unik jg hmmm
    gameExist = db.session.query(Game).filter_by(game_pin = game_pin).scalar() is not None

    if (gameExist == True):
        game = Game.query.filter_by(game_pin = game_pin).first()
        game.serialise()

        game_id = game.game_id
        quiz_id = game.quiz_id

        try:
            # harusnya kalau udah ada leaderboard nya update, jangan add lagi 
            # cek leaderboard dgn game_id ini udah ada atau belum
            leaderboardExist = db.session.query(Leaderboard).filter_by(game_id = game_id).scalar() is not None
            print(leaderboardExist)
            if (leaderboardExist == False):
                print("create lb")
                leaderboard = Leaderboard(
                    quiz_id = quiz_id,
                    game_id = game_id)
                
                db.session.add(leaderboard)
                db.session.commit()
            else:
                print("add into", game_id)

                leaderboard = Leaderboard.query.filter_by(game_id = game_id).first()
                # leaderboard.serialise()
                print("add into")

            try: 
                usernameInGame = db.session.query(UserScore).options(load_only("username")).filter_by(game_id = game_id).all()
                usernameInGameListed = [e.getUsernameOnly() for e in usernameInGame]
                print(usernameInGameListed)

                if username not in usernameInGameListed:
                    userscore = UserScore(
                        username = username,
                        score = 0,
                        leaderboard_id = leaderboard.leaderboard_id,
                        game_id = game_id
                    )
                    db.session.add(userscore)
                    db.session.commit()

                    response["message"] = "Joined game as = {}".format(userscore.username) + " in game {}".format(game.game_pin)
                    response["error"] = False
                    response["data"] = game.serialise()

                else:
                    response["message"] = "Username is used"

            except Exception as e:
                response["message"] =  str(e) + "username"
            
            finally:
                db.session.close()

            
        except Exception as e:
            response["message"] =  str(e)  + "leaderboard"
        finally:
            db.session.close()

    else:
        response["message"] = "join game apa gak adadaa"

    return jsonify(response)
    #####



#################################################################################
# ANSWER GAME
#################################################################################

@router.route('/answer', methods = ['POST'])
def submitAnswer():
    body = request.json

    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }

    # quiz_id = body['quiz_id']
    question_id = body['question_id']
    game_id = body['game_id']
    username = body['username']
    # userscore_id = body['userscore_id']
    answer = body['answer']

    # cek game nya ada atau ga
    gameExist = db.session.query(Game).filter_by(game_id = game_id).scalar() is not None
    if gameExist == True:
        # kalau masuk ke sini berarti game nya ada
        # cek leaderboard dan userscore ada ga
        # eh cek aja sih user name nya ada di userscore ga
        userExist = db.session.query(UserScore).filter_by(username = username, game_id = game_id).scalar() is not None
        if (userExist == True):
            # berarti user ada di joined list, update score, cek jawaban dl
            questionExist = db.session.query(Question).filter_by(question_id = question_id).scalar() is not None

            if questionExist == True:
                try: 
                    question = Question.query.filter_by(question_id = question_id).first()
                    question.serialise()
                    userscore = UserScore.query.filter_by(username = username).first()
                    userscore.serialise()
                    if (answer in question.answer):
                        userscore.score += 100
                        print(userscore.serialise())
                    
                    db.session.commit()
                    response["message"] = "score {}".format(userscore.score)
                    response["error"] = False
                    response["data"] = userscore.serialise()
                except Exception as e:
                    response["message"] =  str(e)
                finally:
                    db.session.close()

            else:
                response["message"] = "Ga ada question iniii ????"
            
        else:
            response["message"] = "user ga join game ini"
    else:
        response["message"] =  "ga ada game nya"

    return jsonify(response)
    
#################################################################################
# LEADERBOARDS
#################################################################################
@router.route('/game/leaderboard/<gamePin>')
def viewLeaderboard(gamePin):

    response = {
        "error" : "True",
        "message" : "",
        "data" : {}
    }

    try:
        gameExist = db.session.query(Game).filter_by(game_pin = gamePin).scalar() is not None

        if (gameExist == True) :
            game = Game.query.filter_by(game_pin = gamePin).first()
            game.serialise()
            leaderboard = Leaderboard.query.filter_by(game_id = game.game_id).all()

            response["data"] = ([e.serialise() for e in leaderboard])
            response["message"] = "Here's the leaderboard"
            response["error"] = False
        else:
            response["message"] = "Ga ada game nya ah"
    except Exception as e:
        response["message"] =  str(e)
    finally:
        db.session.close()


    return jsonify(response)
    



