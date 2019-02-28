from flask import Flask, request, json, jsonify, g
import os
from pathlib import Path

from . import router, baseLocation
from ..utils.file import readFile, createFile, writeFile
from ..utils.authorisation import verifyLogin


# ngambil alamat file 
quizFileLocation = baseLocation / "data" / "quiz-file.json"
questionFileLocation = baseLocation / "data" / "question-file.json"

#################################################################################
# CREATE QUIZ
#################################################################################
@router.route('/quiz', methods = ['POST'])
@verifyLogin
def createQuiz():
    username = g.username
    body = request.json
    print("======IS NOW LOGGING INNNN======", g.username)
    quizData = {
        "total-quiz-available" : 0,
        "quizzes": []
    }

    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }

    # bedanya kalau pake if, ngecek dl file nya ada atau engga baru dibaca, jadi kalau file nya ada tp kosong error dan ga ke-handle
    # if os.path.exists(quizFileLocation):
    #     quizData = readFile(quizFileLocation)
    # kalau ini langsung baca file nya kalau ga ada ya yaudah gapapa
    try:
        quizData = readFile(quizFileLocation)
    except:
        print("ga ada file yang di-load yahh")

    quizData["quizzes"].append(body)
    quizData["total-quiz-available"] += 1
    # quizData["quiz-creator"] = username
    toBeWritten = str(json.dumps(quizData))
    writeFile(quizFileLocation,toBeWritten)

    response["error"] = False #karena ga ngecek apa2 jg sih ya kecuali kalau nanti mau ngecek quiz id nya
    response["message"] = "quiz berhasil dibikin"
    response["data"] = body
    # response["data"] = quizData

    return jsonify(response)

#################################################################################
# GET ALL QUIZZES
#################################################################################
@router.route('/quiz/seeAllQuizAvailable')
@verifyLogin
def getAllQuiz():
    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }
    try: 
        quizData = readFile(quizFileLocation)
    except:
        response["message"] = "gagal load file quiz"
    else:
        response["error"] = False
        response["message"] = str(len(quizData["quizzes"])) + " quiz(zes) found"
        response["data"] = quizData["quizzes"]

    return jsonify(response)

#################################################################################
# GET QUESTION(S) PER QUIZ-ID
#################################################################################
@router.route('/quiz/<quizId>')
@verifyLogin
def getQuiz(quizId):
    isQuizFound = False
    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }
    try: 
        quizData = readFile(quizFileLocation)
    except:
        print("ga ada file quiz nya loh")
        response["message"] = "error load data"
    else:        
        for quiz in quizData["quizzes"] :
            if (quiz["quiz-id"] == int(quizId)):
                quizDataTemp = quiz
                isQuizFound = True
                response["error"] = False
                response["data"] = quizDataTemp
                break

        # baru nyari question di quiz ybs
        if isQuizFound:
            try:
                questionData = readFile(questionFileLocation)
            except:
                print("file question nya ga ada sih jd ya aku kasih quiz kosong aja ya")
                response["message"] = "ga ada question apa pun lol"
            else:
                for question in questionData["questions"] :
                    if (question["quiz-id"] == int(quizId)):
                        quizDataTemp["question-list"].append(question)
                if len(quizDataTemp["question-list"]) == 0 :
                    response["message"] = "this quiz has 0 question"
                else:
                    response["message"] = str(len(quizDataTemp["question-list"])) + " question(s) found"
        else:
            response["message"] = "gak ada quiz yg km cari ew"
    return jsonify(response)

    '''
    aku yang primitif tp aku suka jd aku simpen hhee sorry
    quizData = readFile(quizFileLocation)

    # nyari kuis nya ada atau engga
    position = -1
    for i in range(len(quizData["quizzes"])) :
        if (quizData["quizzes"][i]["quiz-id"] == int(quizId)):
            position = i
            break
    if (position == -1) :
        res = "wah mas ga ada data nya, kuis yang mana ya?"
        return res
    else:

        for quiz in quizData["quizzes"] :
            if (quiz["quiz-id"] == int(quizId)):
                quizDataTemp = quiz
                break
        
        #nyari questionnya
        questionData = readFile(questionFileLocation)

        for question in questionData["questions"] :
            if (question["quiz-id"] == int(quizId)):
                quizDataTemp["question-list"].append(question)
    

    return jsonify(quizDataTemp)
    '''
#################################################################################
# UPDATE DELETE QUIZ
#################################################################################
@router.route('/quiz/<quizId>', methods=["PUT", "DELETE"])
@verifyLogin
def updateDeleteQuiz(quizId):
    print("======IS NOW LOGGING INNNN======", g.username)
    quizData = readFile(quizFileLocation)

    # nyari quiz yg mau di-update atau di-delete dl
    position = -1
    for i in range(len(quizData["quizzes"])) :
        if (quizData["quizzes"][i]["quiz-id"] == int(quizId)):
            position = i
            break

    if (position == -1) :
        res = "wah mas ga ada data nya, kuis yang mana ya?"
        return res
    else:
        res = str(quizData["quizzes"][position]["quiz-id"]) + " yaaaaaa??? " + str(quizData["quizzes"][position]["quiz-title"])

        # kalau data yg mau di-update atau di-delete udah ketemu, baru deh
        # kalau PUT, berarti quiz-title sama quiz-category di file diganti jd dari yang baru dari body
        if request.method == "PUT" :
            body = request.json
            quizData["quizzes"][position] = {**quizData["quizzes"][position], **body}

        elif request.method == "DELETE" :   
            # ngehapus question di quiz ybs dl
            questionData = readFile(questionFileLocation)

            # kayaknya sih ini ngedelete nya udah semua meski question-id nya sama
            lenQL = 0
            QLInd = []
            for question in questionData["questions"] :
                i = questionData["questions"].index(question) 
                if (question["quiz-id"] == int(quizId)):
                    lenQL += 1
                    QLInd.append(i)
            
            currentDeletingIndex = 0
            deleted = 0
            for i in range(lenQL):
                currentDeletingIndex = QLInd[i] - deleted
                del questionData["questions"][currentDeletingIndex]
                deleted += 1

            toBeWritten = str(json.dumps(questionData))
            writeFile(questionFileLocation,toBeWritten)            

            # ngehapus quiz nya
            del quizData["quizzes"][position]
            quizData["total-quiz-available"] -= 1
        
        toBeWritten = str(json.dumps(quizData))
        writeFile(quizFileLocation,toBeWritten)

    return res
