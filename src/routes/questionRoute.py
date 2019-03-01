from flask import Flask, request, json, jsonify, g, abort
import os
from pathlib import Path

from . import router, baseLocation
from ..utils.file import readFile, createFile, writeFile
from ..utils.authorisation import verifyLogin



# ngambil alamat file 
quizFileLocation = baseLocation / "data" / "quiz-file.json"
questionFileLocation = baseLocation / "data" / "question-file.json"

#################################################################################
# CREATE QUESTION
#################################################################################
@router.route('/question', methods = ['POST']) #default method itu GET
@verifyLogin
def createQuestion():
    print("======IS NOW LOGGING INNNN======", g.username)
    body = request.json
    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }

    questionData = {
        "questions": []
    }

    try:
        quizData = readFile(quizFileLocation)
    except:
        response["message"] = "error load data quiz belum ada quiz apa pun!!!"
    else:
        # ngecek dl question id sama quiz id sih kalau mau
        isQuizFound = False
        quizIdToCreateQuestion = ''
        for quiz in quizData["quizzes"] :
            if quiz["quiz-id"] == int(body["quiz-id"]):
                isQuizFound = True
                response["error"] = False
                quizIdToCreateQuestion = str(quiz["quiz-id"])
                break
    
        print("###############", isQuizFound)
        isQuestionIdIsUsed = False
        if isQuizFound == True:            
            try: 
                questionData = readFile(questionFileLocation)
            except:
                print("nambahin question pertama di kuis ini yaaa")
            else:
                response["message"] = "nambah question di quiz " + str(body["quiz-id"])
                print("asdaksjdhkasjdhkas",quizIdToCreateQuestion)
                for question in questionData["questions"]:
                    if int(question["quiz-id"]) == int(quizIdToCreateQuestion) :
                        if question["question-id"] == int(body["question-id"]) :
                            isQuestionIdIsUsed = True
                            response["error"] = True
                            response["message"] = "question-id udah dipake, ganti dong hhe"
                            break

            if (isQuestionIdIsUsed == False):
                questionData["questions"].append(body)
                toBeWritten = str(json.dumps(questionData))
                writeFile(questionFileLocation,toBeWritten)

                response["error"] = False
                response["data"] = body

        else: # quiz nya ga ketemu
            response["message"] = "quiz yg mana ya ga ketemu"

    return jsonify(response)

#################################################################################
# GET ALL QUESTIONS
#################################################################################
@router.route('/question/seeAllQuestionAvailable')
@verifyLogin
def getAllQuestion():
    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }
    try: 
        questionData = readFile(questionFileLocation)
    except:
        response["message"] = "gagal load file question"
    else:
        response["error"] = False
        response["message"] = str(len(questionData["questions"])) + " question(s) found"
        response["data"] = questionData["questions"]

    return jsonify(response)


#################################################################################
# GET SPECIFIC QUESTION IN SPECIFIC QUIZ-ID 
#################################################################################
@router.route('/quiz/<quizId>/question/<questionId>')
@verifyLogin
def getThatQuestion(quizId,questionId):
    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }

    try: 
        questionData = readFile(questionFileLocation)
    except:
        response["message"] = "file question gagal di-load"
    else:
        isQuestionFound = False
        for question in questionData["questions"] :
            if (question["question-id"] == int(questionId) and question["quiz-id"] == int(quizId)) :
                response["data"] = question
                response["message"] = "ketemu pertanyaannya"
                isQuestionFound = True
                break
        if isQuestionFound == False:
            response["message"] = "gak ada pertanyaan no " + str(questionId) + " di kuis " + str(quizId)

    return jsonify(response)

    '''
    atau pake cara ini hue aku pusing
    try:
        for question in questionData["questions"] :
            if (question["question-id"] == int(questionId) and question["quiz-id"] == int(quizId)) :
                response["data"] = question
                response["message"] = "ketemu pertanyaannya"
                isQuestionFound = True
                break
        if isQuestionFound == False:
            response["message"] = "gak ada pertanyaan no " + str(questionId) + " di kuis " + str(quizId)
            abort(404)

    '''

#################################################################################
# UPDATE DELETE QUESTION
#################################################################################
@router.route('/quiz/<quizId>/question/<questionId>', methods=["PUT", "DELETE"])
@verifyLogin
def updateDeleteQuestion(quizId,questionId):
    print("======IS NOW LOGGING INNNN======", g.username)

    response = {
        "error" : True,
        "message" : ""
    }

    try:
        questionData = readFile(questionFileLocation)
    except:
        response["message"] = "gagal load question file"
    else:
        isQuestionInQuizXFound = False

        for question in questionData["questions"] :
            if (question["quiz-id"] == int(quizId) and question["question-id"] == int(questionId)) :
                isQuestionInQuizXFound = True
                position = questionData["questions"].index(question)
                break

        if isQuestionInQuizXFound:
            response["error"] = False
            response["message"] = str(questionData["questions"][position]["quiz-id"]) + " yang nomor " + str(questionData["questions"][position]["question-id"])

            # kalau ketemu data nya baru dipisah antara PUT dan DELETE nyaaa
            if request.method == "PUT" :
                body = request.json
                questionData["questions"][position] = {**questionData["questions"][position], **body}

                response["data"] = questionData["questions"][position]

            elif request.method == "DELETE" :
                del questionData["questions"][position]

                response["data"] = questionId + " di " + quizId + " dihapus"
                

            toBeWritten = str(json.dumps(questionData))
            writeFile(questionFileLocation,toBeWritten)
        else:
            response["message"] = "question yang mana ya ga ketemu"
    
    '''
    questionData = readFile(questionFileLocation)

    # nyari question yang mau di-update atau di-delete
    position = -1
    for i in range(len(questionData["questions"])) :
        if (questionData["questions"][i]["quiz-id"] == int(quizId) and questionData["questions"][i]["question-id"] == int(questionId)):
            position = i
            break

    if (position == -1) :
        res = "ih ga ada datanya ah kak"
        return res
    else : 
        res = str(questionData["questions"][position]["quiz-id"]) + " yang nomor " + str(questionData["questions"][position]["question-id"])

        # kalau ketemu data nya baru dipisah antara PUT dan DELETE nyaaa
        if request.method == "PUT" :
            body = request.json
            questionData["questions"][position] = {**questionData["questions"][position], **body}

        elif request.method == "DELETE" :
            del questionData["questions"][position]
            

        toBeWritten = str(json.dumps(questionData))
        writeFile(questionFileLocation,toBeWritten)
    '''

    return jsonify(response)

#################################################################################
# GET QUESTION IN SPECIFIC QUIZ-ID ((deprecated krn fungsinya di file quizRoute))
#################################################################################
# @router.route('/quiz/<quizId>/question2/<questionId>')
# def getThatQuestion2(quizId, questionId):
#     quizData = getQuiz(int(quizId)).json
    
#     for question in quizData["question-list"] :
#         if (question["question-id"] == int(questionId)):
#             return jsonify(question)

#     return "hmm maz ko ga ada yh"