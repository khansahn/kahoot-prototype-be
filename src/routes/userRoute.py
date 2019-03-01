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


