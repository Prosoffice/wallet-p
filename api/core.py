from typing import Tuple
from flask import current_app, jsonify
from flask.wrappers import Response


def create_response(data=None, success:int=0, token=None, status: int = 400, message: str = "") -> Tuple[Response, int]:

    response = {"success": success, "message": message, "token": token, "data": data}
    return jsonify(response), status


def create_validation_err_response(data: dict = None, status: int = 400, success: int = 0) -> Tuple[Response, int]:
    if type(data) is not dict and data is not None:
        raise TypeError("Data should be a dictionary")
    result = {}
    d = {}
    for key in data:
        d[key] = data[key][0]
    result['success'] = 0
    result['data'] = d
    return jsonify(result), status





