from flask import Flask, request, abort, jsonify
import jwt

from src.routes import router
# from src.routes import router

app = Flask(__name__)   #buat manggil flask
app.register_blueprint(router)

@app.route('/addition/<int:firstNumber>/<int:secondNumber>')
def addition(firstNumber,secondNumber):
    response = {
        "data" : str(firstNumber + secondNumber),
        "message" : "berhasil"
    }
    return jsonify(response)

