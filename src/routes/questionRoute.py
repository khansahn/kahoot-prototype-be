'''
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
    
        isQuestionIdIsUsed = False
        if isQuizFound == True:            
            try: 
                questionData = readFile(questionFileLocation)
            except:
                print("nambahin question pertama di kuis ini yaaa")
            else:
                response["message"] = "nambah question di quiz " + str(body["quiz-id"])
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

'''


from flask import Flask, request, json, jsonify, g, abort, make_response
import os
from pathlib import Path

from . import router, baseLocation
from ..utils.file import readFile, createFile, writeFile
from ..utils.authorisation import verifyLogin

from ..utils.models import db, RegisteredUser,Quiz,Question,Options

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import exists
from sqlalchemy import func

# db = SQLAlchemy()


# ngambil alamat file 
quizFileLocation = baseLocation / "data" / "quiz-file.json"
questionFileLocation = baseLocation / "data" / "question-file.json"

#################################################################################
# CREATE QUESTION
#################################################################################
@router.route('/question', methods = ['POST']) #default method itu GET
@verifyLogin
def createQuestion():
    body = request.json
    
    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }

    errorCode = 404

    quizExist = db.session.query(Quiz).filter_by(quiz_id = body['quiz-id']).scalar() is not None

    if quizExist == True :
        try:
            res = createQuestionSingle(body['quiz-id'],body['question'],body['answer'],body['options'])
            response["data"] = res.serialise()
            response["message"] = "Question Created"
            response["error"] = False
            errorCode = 200
        except Exception as e:
            response["message"] =  str(e)
            errorCode = 400
        finally:
            db.session.expunge_all()
            db.session.close()

    else:
        response["message"] = "Quiz enggak ada"
        errorCode = 404
    
    
    db.session.close()

    return jsonify(response), errorCode

@router.route('/questionMultiple', methods = ['POST']) #default method itu GET
@verifyLogin
def createQuestionMultiple():
    body = request.json
    
    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }

    errorCode = 404

    quizExist = db.session.query(Quiz).filter_by(quiz_id = body['quiz-id']).scalar() is not None

    if quizExist == True :
        try: 
            questionIdMade = []
            questionMade = []
            for question in body['question-list']:
                res = createQuestionSingle(body['quiz-id'],question['question'],question['answer'],question['options'])
                questionIdMade.append(res.question_id)
                questionMade.append(res.serialise())

            response["data"] = questionMade
            response["message"] = "Question(s) Created"
            response["error"] = False
            errorCode = 200
        except Exception as e:
            response["message"] =  str(e)
            errorCode = 400
        finally:
            db.session.close()

    else:
        response["message"] = "Quiz enggak ada"

    return jsonify(response), errorCode


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
        questions = Question.query.order_by(Question.question_id).all()
        data = [e.serialise() for e in questions]
        response["data"] = data
        response["message"] = "Question(s) found : " + str(len(data))
        response["error"] = False
    except Exception as e:
        response["message"] =  str(e)
    finally:
        db.session.close()

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

    errorCode = 404

    quizExist = db.session.query(Quiz).filter_by(quiz_id = quizId).scalar() is not None

    if (quizExist == True):

        questionExist = db.session.query(Question).filter_by(question_id = questionId).scalar() is not None
        if (questionExist == True):
            try:
                question = Question.query.filter_by(question_id = questionId).first()

                response["message"] =  "Question found. Qestuonnn = " + str(question.question)
                response["data"] = question.serialise()
                response["error"] = False
                errorCode = 200
            except Exception as e:
                response["message"] = str(e)
            finally:
                db.session.close()

        else:
            response["message"] =  "Question is not founddd"
            response["error"] = True

    else:
        response["message"] =  "Quiz is not found"
        response["error"] = True

    return jsonify(response), errorCode


#################################################################################
# UPDATE DELETE QUESTION
#################################################################################
@router.route('/quiz/<quizId>/question/<questionId>', methods=["PUT", "DELETE"])
@verifyLogin
def updateDeleteQuestion(quizId,questionId):
    print("======IS NOW LOGGING INNNN======", g.username)

    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }

    quizExist = db.session.query(Quiz).filter_by(quiz_id = quizId).scalar() is not None
    questionExist = db.session.query(Question).filter_by(question_id = questionId).scalar() is not None

    if (quizExist == True and questionExist == True):
        if request.method == "PUT" :
            try:
                body = request.json
                db.session.query(Question).filter_by(question_id = questionId).update(body)

                statusEnabled = body['status_enabled']
                Options.query.filter_by(question_id = questionId).update(dict(status_enabled=statusEnabled)) 

                db.session.commit()
                question = Question.query.filter_by(question_id = (questionId)).first()

                response["message"] =  "Question updated. Qestuonnn = " + str(question.question)
                response["data"] = question.serialise()
                response["error"] = False

            except Exception as e:
                response["message"] = str(e)
                response["error"] = True
            finally:
                db.session.close()
        
        elif request.method == "DELETE" :
            try:
                question = Question.query.filter_by(question_id = questionId).first()
                question.status_enabled = False
                db.session.commit()

                Options.query.filter_by(question_id = questionId).update(dict(status_enabled=False)) 

                db.session.commit()
                response["message"] =  "Question disabled. Question = " + str(question.question)
                response["error"] = False
            except Exception as e:
                response["message"] = str(e)
                response["error"] = True            
            finally:
                db.session.close()

    else:
        response["message"] = "Question / quiz ga ketemuu"
   
    return jsonify(response)

############# FUNGSI BANTUAN #############
def createQuestionSingle(quizId,question,answer,options):

    try: 
        question = Question(
            quiz_id = quizId,
            question = question,
            answer = [8]
        )

        db.session.add(question)
        db.session.commit()
        question.serialise()

        getAnswerId = []
        # tambahin si optionnya
        for i in range(len(options)):
            option = Options(
                question_id = question.question_id,
                option = options[i])        
            db.session.add(option)
            db.session.commit()
            # option.serialise()

            if (i in answer):
                getAnswerId.append(str(option.option_id))

        question.answer = getAnswerId
        Question.query.filter_by(question_id = question.question_id).update(dict(answer=getAnswerId)) 

        db.session.commit()
        return question
        
    except Exception as e:  
        return str(e)
