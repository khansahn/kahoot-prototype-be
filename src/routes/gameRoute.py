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
                        position = questionData["questions"].index(question)
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
                        print("///////////MASUKKKK", gameToBePlayed["game-pin"],gameToBePlayed
                        ["user-list"])
                        print(body["username"] in gameToBePlayed["user-list"])
                        
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
                res =  (game["leaderboard"])
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
