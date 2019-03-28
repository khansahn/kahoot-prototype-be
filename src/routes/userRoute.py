'''
from flask import Flask, request, json, jsonify
import os
from pathlib import Path

from ..utils.crypt import encrypt, decrypt
from ..utils.authorisation import generateToken
from ..utils.file import readFile, createFile, writeFile
from . import router, baseLocation

# ngambil alamat file 
registeredUserFileLocation = baseLocation / "data" / "registered-user-file.json"

print(os.getenv("SECRET_KEY"))

@router.route('/alaala')
def alaala():
    return "HOY"
#####################################################################################################
# REGISTER USER
#####################################################################################################
@router.route('/user', methods=['POST'])
def registerUser():
    body = request.json

    if body["todo"] == "encrypt":
        body["password"] = encrypt(body["password"])
    elif body["todo"] == "decrypt":
        body["password"] = decrypt(body["password"])

    registeredUserData = {
        "registeredUsers" : []
    }

    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }
    position = -1
    try:
        registeredUserData = readFile(registeredUserFileLocation)
    except: 
        response["message"] = "error load data tp asa gak papa lol yaa bikin baru we"
    else:
        # cek username atau email nya udah pernah dipake belum               
        for i in range(len(registeredUserData["registeredUsers"])) :
            registeredUser = registeredUserData["registeredUsers"][i]
            if (registeredUser["username"] == body["username"]) :
                # res = "Username nya udah dipake maz"
                response["message"] = "Username nya udah dipake maz"
                position = i
                break
            if (registeredUser["email"] == body["email"]):
                # res = "Km udah pernah daftar pake email ini loh"
                response["message"] = "Km udah pernah daftar pake email ini loh"
                position = i
                break
            if (registeredUser["user-id"] == body["user-id"]):
                # res = "ganti ah user-id nya udah ada yg make"
                response["message"] = "ganti ah user-id nya udah ada yg make"
                position = i
                break
    if (position == -1):
        registeredUserData["registeredUsers"].append(body) 
        toBeWritten = str(json.dumps(registeredUserData))
        writeFile(registeredUserFileLocation,toBeWritten)
            
        response["message"] = "BERHASIL REGIST, METYAAA"
        del body["password"]
        del body["todo"]
        response["data"] = body
        response["error"] = False
        # atau mau response["data"] = registeredUserData
    # else : 
        # res = res
    return jsonify(response)

#####################################################################################################
# LOGIN USER
#####################################################################################################
@router.route('/user/login', methods = ['POST'])
def loginUser():
    body = request.json

    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }
    try:
        registeredUserData = readFile(registeredUserFileLocation)
    except:
        response["message"] = "wooow ga ada file yg udah pernah registtt seremmm"
    else:
        # nyari yang di-login udah ada di regist atau belum
        position = -1
        for i in range(len(registeredUserData["registeredUsers"])) :
            registeredUser = registeredUserData["registeredUsers"][i]
            if (registeredUser["username"] == body["username"]) :
                position = i
                response["error"] = False
                if (decrypt(registeredUser["password"]) == body["password"]) :
                    response["message"] = "Login berhasssil"
                    data = {
                        "token" : generateToken(body["username"]),
                        "username" : body["username"]
                    }
                    response["data"] = data
                    break
                else:
                    response["message"] = "Passwordnya salah ih"
                    response["error"] = False

         # kalau user yang di login ga ada di registered user
        if (position == -1) :
            response["message"] = "Regist dl ah"
            # response["status"] = False
    
    return jsonify(response)
'''

###########################################################################################
###########################################################################################
###########################################################################################

from flask import Flask, request, json, jsonify, make_response
import os
from pathlib import Path

from ..utils.crypt import encrypt, decrypt
from ..utils.authorisation import generateToken

from ..utils.models import db, RegisteredUser

from . import router, baseLocation

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import exists
from sqlalchemy import func

# db = SQLAlchemy()

print(os.getenv("SECRET_KEY"))

@router.route('/alaala')
def alaala():
    return "HOY"
#####################################################################################################
# REGISTER USER
#####################################################################################################
@router.route('/user', methods=['POST'])
def registerUser():
    body = request.json

    if body["todo"] == "encrypt":
        body["password"] = encrypt(body["password"])
    elif body["todo"] == "decrypt":
        body["password"] = decrypt(body["password"])

    username = body["username"]
    email = body["email"]
    password = body["password"]
    fullname = body["fullname"]

    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }

    # cek username udah dipake belum
    usernameExist = db.session.query(RegisteredUser).filter_by(username = username).scalar() is not None
    emailExist = db.session.query(RegisteredUser).filter_by(email = email).scalar() is not None
    
    if (usernameExist == True or emailExist == True):
        response["message"] = "username/email is already exist"
    else:
        try:            
            user = RegisteredUser(
                username = username,
                email = email,
                password = password,
                fullname = fullname)

            db.session.add(user)
            db.session.commit()

            response["message"] =  "User created. User-id = {}".format(user.user_id)
            response["error"] = False
            response["data"] = user.serialise()
        except Exception as e:
            response["message"] = str(e)
        finally:
            db.session.close()

    
    return jsonify(response)



#####################################################################################################
# LOGIN USER
#####################################################################################################
@router.route('/user/login', methods = ['POST'])
def loginUser():
    body = request.json

    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }
    errorCode = 404

    # cek username ada atau engga
    usernameExist = db.session.query(RegisteredUser).filter_by(username = body["username"]).scalar() is not None

    if (usernameExist == True) :
        try:
            user = db.session.query(RegisteredUser).filter_by(username = body["username"]).first()
            user.serialise()
            if (decrypt(user.password) == body["password"]):
                data = {
                    "token" : generateToken(body["username"]),
                    "username" : body["username"]
                }
                response["message"] = "Login berhasil"
                response["error"] = False
                response["data"] = data
                errorCode = 200

            else:
                response["message"] = "Incorrect gov eh pass"
                errorCode = 401

        except Exception as e:
            response["message"] = str(e)

        finally:
            db.session.close()

    else:
        response["message"] = "Username is not registered"
        errorCode = 401
    return jsonify(response), errorCode


def setCookies(username):
    resp = make_response('')
    resp.set_cookie('username',username)
    return resp


###############################################################################
########//////////////////////////////////////////////////////////////#########
###############################################################################


@router.route('/getAllRegisteredUsers', methods=['GET'])
def getAllRegisteredUsers():
    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }
    
    # cek username ada atau engga
    usernameExist = db.session.query(RegisteredUser).order_by(RegisteredUser.user_id).all() is not None

    if (usernameExist == True) :
        try:
            registeredUsers = RegisteredUser.query.order_by(RegisteredUser.user_id).all()

            data = ([e.returnToUser() for e in registeredUsers])
            registeredUsersCount  = len(data)
            response["message"] = "User(s) found : " + str(registeredUsersCount)
            response["error"] = False
            response["data"] = data
        except Exception as e:
            response["message"] = str(e)
        finally:
            db.session.close()

    else:
        response["message"] = "User is not found"
    
    return jsonify(response)

@router.route('/getUserByUsername/<username>')
def getUserById(username):
    response = {
        "error" : True,
        "message" : "",
        "data" : {}
    }

    # cek username ada atau engga
    usernameExist = db.session.query(RegisteredUser).filter_by(username = username).scalar() is not None

    if (usernameExist == True) :
        try:
            user = RegisteredUser.query.filter_by(username = username).first()

            response["message"] ="User found"
            response["error"] = False
            response["data"] = (user.returnToUser())
        except Exception as e:
            response["message"] = str(e)
        finally:
            db.session.close()

    else :
        response["message"] = "Username is not found"

    return jsonify(response)

