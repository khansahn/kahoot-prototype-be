from flask import jsonify, make_response
from . import router


@router.errorhandler(403)
def errorhandler403(e):
    response = {
        "error" : 403,
        "message" : "belum login atau login expired"
    }
    return jsonify(response), 403

@router.errorhandler(404)
def errorhandler404(e):
    response = {
        "error" : 404,
        "message" : "halaman yg anda tuju, indak adooo"
    }
    return jsonify(response), 404

@router.errorhandler(500)
def errorhandler500(e):
    response = {
        "error" : 500,
        "message" : "punten server lg error hhe"
    }
    return jsonify(response), 500