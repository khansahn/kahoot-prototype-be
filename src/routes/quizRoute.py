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
    fileIsEmpty = True
    isQuizIdIsUsed = False
    try:
        quizData = readFile(quizFileLocation)
        fileIsEmpty = False
    except:
        fileIsEmpty = True
    else:
        # isQuizIdIsUsed = False
        for quiz in quizData["quizzes"] :
            if (body["quiz-id"] == quiz["quiz-id"]):
                isQuizIdIsUsed = True
                response["message"] = "quiz id udah dipake, ganti dong"
                break
            
    if fileIsEmpty or isQuizIdIsUsed == False:
        quizData["quizzes"].append(body)
        quizData["total-quiz-available"] += 1
        toBeWritten = str(json.dumps(quizData))
        writeFile(quizFileLocation,toBeWritten)

        response["error"] = False
        response["message"] = "kuis berhasil dibuat"
        response["data"] = body


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
        response["message"] = "error load data quiz file"
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
                response["message"] = "ga ada question apa pun lol gagal load question file"
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

#################################################################################
# UPDATE DELETE QUIZ
#################################################################################
@router.route('/quiz/<quizId>', methods=["PUT", "DELETE"])
@verifyLogin
def updateDeleteQuiz(quizId):
    print("======IS NOW LOGGING INNNN======", g.username)

    response = {
        "error" : True,
        "message" : ""
    }

    try:
        quizData = readFile(quizFileLocation)
    except:
        response["message"] = "gagal load quiz file"
    else: 
        # nyari quiz nya ada atau engga
        isQuizFound = False
        for quiz in quizData["quizzes"] :
            if (int(quizId) == quiz["quiz-id"]):
                isQuizFound = True
                position = quizData["quizzes"].index(quiz)
                break

        if (isQuizFound):
            response["error"] = False
            response["message"] = str(quizData["quizzes"][position]["quiz-id"]) + " yaaaaaa??? " + str(quizData["quizzes"][position]["quiz-title"])

            # kalau data yg mau di-update atau di-delete udah ketemu, baru deh
            # kalau PUT, berarti quiz-title sama quiz-category di file diganti jd dari yang baru dari body
            if request.method == "PUT" :
                body = request.json
                quizData["quizzes"][position] = {**quizData["quizzes"][position], **body}
                response["data"] = quizData["quizzes"][position]

            elif request.method == "DELETE" :   
                # ngehapus question di quiz ybs dl
                try: 
                    questionData = readFile(questionFileLocation)
                except:
                    response["message"] = "gagal load question file"
                else:
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

                response["data"] = "quiz-id " + str(quizId) + " is deleted"
            
            toBeWritten = str(json.dumps(quizData))
            writeFile(quizFileLocation,toBeWritten)


        else:
            response["message"] = "quiz gak ketemuu mau update/delete apaan hue"

    return jsonify(response)
