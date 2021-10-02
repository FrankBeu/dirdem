import json
from smartcontract_utils import w3
from flask import Flask, Response, request, jsonify
from marshmallow import Schema, fields, ValidationError

import logging

def check_gender(data):
    valid_list = ["male", "female", "other"]
    if data not in valid_list:
        raise ValidationError(f"Invalid gender. Valid choices are {valid_list}")


class UserSchema(Schema):
    name = fields.String(required=True)
    gender = fields.String(required=True, validate=check_gender)


app = Flask(__name__)

CONTRACT_ADDRESS = "0x02500eE183Da01E01db093bF016FD8486b45Fd6c"

# api to set new user every api call
@app.route("/blockchain/user", methods=["POST"])
def transaction():
    w3.eth.defaultAccount = w3.eth.accounts[1]
    # with open("data.json", "r") as f:
    with open("./backend/user/build/contracts/user.json", "r") as f:
        datastore = json.load(f)
    abi = datastore["abi"]
    # contract_address = datastore["contract_address"]
    # contract_address = "0x02500eE183Da01E01db093bF016FD8486b45Fd6c"
    contract_address = CONTRACT_ADDRESS

    # Create the contract instance with the newly-deployed address
    user = w3.eth.contract(
        address=contract_address,
        abi=abi,
    )
    body = request.get_json()
    try:
        result = UserSchema().load(body)
    except ValidationError as err:
        return jsonify(err.messages), 422

    tx_hash = user.functions.setUser(result["name"], result["gender"])
    tx_hash = tx_hash.transact()
    # Wait for transaction to be mined...
    w3.eth.waitForTransactionReceipt(tx_hash)

    user_data = user.functions.getUser().call()
    return jsonify({"data": user_data}), 200

@app.route("/user", methods=["GET"])
def getUser():
    w3.eth.defaultAccount = w3.eth.accounts[1]
    # with open("data.json", "r") as f:
    with open("./backend/user/build/contracts/user.json", "r") as f:
        datastore = json.load(f)
    abi = datastore["abi"]
    # contract_address = datastore["contract_address"]
    contract_address = CONTRACT_ADDRESS

    # Create the contract instance with the newly-deployed address
    user = w3.eth.contract(
        address=contract_address,
        abi=abi,
    )

    user_data = user.functions.getUser().call()
    return jsonify({"data": user_data}), 200
