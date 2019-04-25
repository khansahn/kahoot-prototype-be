####################################################################################
###############///////////////////////////////////////////////######################
####################################################################################

from flask import Flask, request, json, jsonify, g, make_response
import os
from pathlib import Path

from . import router, baseLocation
from ..utils.authorisation import verifyLogin

from ..utils.models import db, Quiz, RegisteredUser, Game, Leaderboard, Question


from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import exists

# db = SQLAlchemy()

# from kahoot-server.app import db


#################################################################################
# CREATE QUIZ
#################################################################################
@router.route('/quiz', methods = ['POST'])
@verifyLogin
def createQuiz():
    username = g.username
    body = request.json

    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }

    errorCode = 404

    try:
        user = RegisteredUser.query.filter_by(username = username).first()
        quiz = Quiz(
            quiz = body["quiz"],
            quiz_category = body["quiz_category"],
            creator_id = user.user_id)
        
        db.session.add(quiz)
        
        db.session.commit()

        response["message"] =  "Quiz added. Quiz-id = {}".format(quiz.quiz_id)
        response["error"] = False
        response["data"] = quiz.serialise()

        errorCode = 200
    
    except Exception as e:
        response["message"] =  str(e)
        errorCode = 404

    finally:
        db.session.close()


    return jsonify(response), errorCode



#################################################################################
# GET QUIZ BY ID
#################################################################################
@router.route('/quiz/<quizId>')
@verifyLogin
def getQuizById(quizId):
    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }
   
    # cek quiz ada atau engga
    quizExist = db.session.query(Quiz).filter_by(quiz_id = quizId, status_enabled = True).scalar() is not None

    if (quizExist == True):
        try:
            quiz = Quiz.query.filter_by(quiz_id = quizId).first()

            response["message"] = "Quiz found"
            response["error"] = False
            response["data"] = quiz.serialise()
        except Exception as e:
            response["message"] =  str(e)
        finally:
            db.session.close()

    else:
        response["message"] = "Nothing found"

    return jsonify(response)



#################################################################################
# GET ALL QUIZZES
#################################################################################
@router.route('/quiz/seeAllQuizAvailable')
# @verifyLogin
def getAllQuiz():
    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }
   
    # cek quiz ada atau engga
    quizExist = db.session.query(Quiz).order_by(Quiz.quiz_id).all() is not None

    if (quizExist == True):
        try:
            quizzes = Quiz.query.filter_by(status_enabled = True).order_by(Quiz.quiz_id).all()

            data = ([e.serialise() for e in quizzes])
            quizCount = len(data)
            response["message"] = "Quiz(zes) found : " + str(quizCount)
            response["error"] = False
            response["data"] = data
        except Exception as e:
            response["message"] =  str(e)
        finally:
            db.session.close()

    else:
        response["message"] = "Nothing found"

    return jsonify(response)




#################################################################################
# GET ALL QUIZZES MADE BY USER
#################################################################################
@router.route('/quiz/seeAllQuizCreatedBy/<username>')
@verifyLogin
def getAllQuizCreatedBy(username):
    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }
    
    # get user id
    usernameExist = db.session.query(RegisteredUser).filter_by(username = username).scalar() is not None
    if usernameExist == True:
        userLog = db.session.query(RegisteredUser).filter_by(username = username).first()
        userLog.serialise()
    else:
        response["message"] = "User does not exist"
        response["error"] = True
        
        return jsonify(response)

    # cek quiz ada atau engga
    quizExist = db.session.query(Quiz).filter_by(creator_id = userLog.user_id).order_by(Quiz.quiz_id).all() is not None

    if (quizExist == True):
        try:
            quizzes = Quiz.query.filter_by(creator_id = userLog.user_id,status_enabled = True).order_by(Quiz.quiz_id).all()

            data = ([e.serialise() for e in quizzes])
            quizCount = len(data)
            response["message"] = "Quiz(zes) found : " + str(quizCount)
            response["error"] = False
            response["data"] = data
        except Exception as e:
            response["message"] =  str(e)
        finally:
            db.session.close()

    else:
        response["message"] = "Nothing found"

    return jsonify(response)
    
#################################################################################
# GET QUESTION(S) PER QUIZ-ID
#################################################################################
@router.route('/quiz/<quizId>')
# @verifyLogin
def getQuiz(quizId):    
    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }

    errorCode = 404
    
    # cek quiz ada atau engga
    quizExist = db.session.query(Quiz).filter_by(quiz_id = quizId).scalar() is not None

    if (quizExist == True):
        try:
            quiz = Quiz.query.filter_by(quiz_id = quizId, status_enabled = True).first()
            response["message"] = "Quiz is found"
            response["error"] = False
            response["data"] = (quiz.serialise())
            errorCode = 200
        except Exception as e:
            response["message"] =  str(e)
            errorCode = 404

        finally:
            db.session.close()

    else :
        response["message"] = "Quiz is not found"
        errorCode = 404


    return jsonify(response), errorCode



#################################################################################
# GET QUESTION(S) PER GAME-PIN
#################################################################################
@router.route('/quiz/game/<gamePin>')
# @verifyLogin
def getQuizPerGamePin(gamePin):    
    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }
    
    # cek game ada atau engga
    gameExist = db.session.query(Game).filter_by(game_pin = gamePin).scalar() is not None

    if (gameExist == True):
        game = Game.query.filter_by(game_pin = gamePin).first()
        print(game)
        try:
            quiz = Quiz.query.filter_by(quiz_id = game.quiz_id).first()
            data = quiz.serialise()
            ql = []
            for e in data["question_list"] :
                question = Question.query.filter_by(question_id = e["question_id"]).first()
                ql.append(question.serialise())

            data["question_list"] = ql
            
            response["message"] = "Quiz" +quiz.quiz+ " is found for game " + str(game.game_pin)
            response["error"] = False
            response["data"] = data
        except Exception as e:
            response["message"] =  str(e)
        finally:
            db.session.close()

    else :
        response["message"] = "Quiz is not found"

    return jsonify(response)

#################################################################################
# UPDATE DELETE QUIZ
#################################################################################
@router.route('/quiz/<quizId>', methods=["PUT", "DELETE"])
@verifyLogin
def updateDeleteQuiz(quizId):
    print("======IS NOW LOGGING INNNN======", g.username)
    user = RegisteredUser.query.filter_by(username = g.username).first()

    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }
    
    # cek quiz ada atau engga
    quizExist = db.session.query(Quiz).filter_by(quiz_id = quizId).scalar() is not None

    if (quizExist == True):
        response["error"] = False

        # kalau data yg mau di-update atau di-delete udah ketemu, baru deh
        # kalau PUT, berarti quiz-title sama quiz-category di file diganti jd dari yang baru dari body
        if request.method == "PUT" :
            try:
                ## MASIH BELUM KEUPDATE SEMUA ANAK2NYA, HARUS DI CEK DI SEMUA PARENT - CHILD - GRANDCHILD
                ## udah ko, integrating sessionnya
                body = request.json
                db.session.query(Quiz).filter_by(quiz_id = quizId).update(body)
                
                statusEnabled = body['status_enabled']

                Game.query.filter_by(quiz_id = quizId).update(dict(status_enabled=statusEnabled))
                db.session.commit()
                Leaderboard.query.filter_by(quiz_id = quizId).update(dict(status_enabled=statusEnabled))
                db.session.commit()         
                Question.query.filter_by(quiz_id = quizId).update(dict(status_enabled=statusEnabled))
                db.session.commit()

                quiz = Quiz.query.filter_by(quiz_id = (quizId)).first()

                response["message"] =  "Quiz updated. QuiSSASASASz = " + str(quiz.quiz)
                response["data"] = quiz.serialise()

            except Exception as e:
                response["message"] = str(e)
                response["error"] = True
            finally:
                db.session.close()

        elif request.method == "DELETE" :   # ini pake update version
            try:
                quiz = Quiz.query.filter_by(quiz_id = quizId).first()
                quiz.status_enabled = False

                Game.query.filter_by(quiz_id = quizId).update(dict(status_enabled=False))        
                Leaderboard.query.filter_by(quiz_id = quizId).update(dict(status_enabled=False))
                Question.query.filter_by(quiz_id = quizId).update(dict(status_enabled=False))

                db.session.commit()
                response["message"] =  "Quiz disabled. Quiz = " + str(quiz.quiz)
            except Exception as e:
                response["message"] = str(e)
                response["error"] = True            
            finally:
                db.session.close()
        else:
            response["message"] = "nyangkut"

    else:
        response["message"] = "quiz gak ketemuu mau update/delete apaan hue"

    return jsonify(response)
