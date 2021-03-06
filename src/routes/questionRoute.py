from flask import Flask, request, json, jsonify, g, abort, make_response
import os
from pathlib import Path

from . import router, baseLocation
from ..utils.file import readFile, createFile, writeFile
from ..utils.authorisation import verifyLogin

from ..utils.models import db, RegisteredUser,Quiz,Question

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
                bodyRaw = request.json
                body = {
                    "quiz_id": bodyRaw['quiz_id'],
                    "question_id" : bodyRaw['question_id'],
                    "question" : bodyRaw['question'],
                    "answer" :bodyRaw['answer'],
                    "opta": bodyRaw['options']['optA'],
                    "optb": bodyRaw['options']['optB'],
                    "optc": bodyRaw['options']['optC'],
                    "optd": bodyRaw['options']['optD'],
                    "status_enabled": bodyRaw['status_enabled']  
                }
                db.session.query(Question).filter_by(question_id = questionId).update(body)

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
            answer = answer,
            optA = options['optA'],
            optB = options['optB'],
            optC = options['optC'],
            optD = options['optD']
        )

        db.session.add(question)
        db.session.commit()
        question.serialise()
      
        return question
        
    except Exception as e:  
        return str(e)
