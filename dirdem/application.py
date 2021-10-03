from dirdem import app

from flask import Flask, render_template, request, redirect, url_for, Response, request, jsonify
from flask_assets import Bundle, Environment
from dirdem.utils.smartcontract import w3
from marshmallow import Schema, fields, ValidationError

from dirdem.config.dummy import todos
from dirdem.config.conf import load_setting
from dirdem.dummy.dummy import load_data
# from dirdem.config import *
# import dirdem.config.conf as conf
# import dirdem.config

import os
import random
import json
import logging
import datetime
import time
### CONFIGURATION
app.config.update(load_setting())

### dummy data for development
dummy = {}

### ASSETS
assets = Environment(app)
css = Bundle("src/main.css", output="dist/main.css", filters="postcss")
js = Bundle("src/*.js", output="dist/main.js")

assets.register("css", css)
assets.register("js", js)
css.build()
js.build()


APP_TITLE = "dirĐem"

def is_dummy() -> bool:
    # if (app.config['ENV'] == 'fake') or (app.config['ENV'] == 'dev'):
    if (app.config['ENV'] == 'fake'):
        ### TODO only dev has hotreload
        # if (app.config['ENV'] == 'fake'):
        ### otherwise hot reload is useless
        global dummy
        dummy = load_data()
        return True

    return False


def etherscan_url_prefix():
    ### TODO: set ethernet only if production
    app.config['ethernet'] = "kovan"
    net_prefix = app.config['ethernet'] + "."
    return "https://" + net_prefix + "etherscan.io/address/"


def get_ballot_address_list():
    w3.eth.default_account = w3.eth.accounts[1]
    with open('./smartcontract/build/contracts/BallotList.json', 'r') as f:
        datastore = json.load(f)
    abi = datastore["abi"]
    # contract_address = datastore["contract_address"]
    contract_address = app.config['BALLOT_LIST_ADDRESS']

    ### Create the contract instance with the newly-deployed address
    ballotList = w3.eth.contract(
        address=contract_address,
        abi=abi,
    )

    ballotList_data_raw = ballotList.functions.get_ballots().call()

    ### ballotList is a address[100] - all empty addresses must be removed
    ballotList_data = []
    for ballot_address in ballotList_data_raw:
        if ballot_address != '0x0000000000000000000000000000000000000000':
            ballotList_data.append(ballot_address)

    return ballotList_data


def get_ballot_data(ballot_address_list):
    w3.eth.defaultAccount = w3.eth.accounts[1]
    with open('./smartcontract/build/contracts/Ballot.json', 'r') as f:
        datastore = json.load(f)
    abi = datastore["abi"]

    ballot_data_list = []

    for ballot_address in ballot_address_list:
        contract_address = ballot_address

        ### Create the contract instance
        ballot = w3.eth.contract(
            address=contract_address,
            abi=abi,
        )

        ballot_data = ballot.functions.state().call()

        ballot_data_list.append(ballot_data)

    return ballot_data_list


def prepare_ballots_data(ballots_data_raw):
    ballots_data = [] 

    for ballot_raw in ballots_data_raw:
        ballot = {}

        ballot['address']         = ballot_raw[0]     
        ballot['addressLink']     = etherscan_url_prefix() + ballot_raw[0]
        ballot['title']           = ballot_raw[1]
        ballot['question']        = ballot_raw[2]
        ballot['dateTimeClosing'] = datetime.datetime.fromtimestamp(ballot_raw[3]).isoformat()
        ### ballot['timelimit']   = ballot_raw[4]
        ballot['resultPositive']  = ballot_raw[5]
        ballot['resultNegative']  = ballot_raw[6]
        ballot['closed']          = True if datetime.datetime.now().timestamp() > ballot_raw[3] else False

        ballots_data.append(ballot)
        print(ballot)

    return ballots_data


### ROUTES
@app.route("/")
def homepage():
    return render_template("homepage/index.html", apptitle = APP_TITLE)


@app.route("/ballots")
def index_ballots():
    ballots = []
    if is_dummy():

        url_prefix = etherscan_url_prefix()
        dummies = dummy['ballot']['ballots']

        for fake in dummies:
            ballot = {}
            # ballot['id']              = fake['id']
            ballot['address']         = fake['address']
            ballot['addressLink']     = url_prefix + fake['address']
            ballot['title']           = fake['title']
            ballot['question']        = fake['question']
            ballot['dateTimeClosing'] = fake['dateTimeClosing']
            ballot['resultPositive']  = fake['resultPositive']
            ballot['resultNegative']  = fake['resultNegative']
            ballot['closed']          = fake['closed']

            ballots.append(ballot)
    else:
        ballot = {}

        ballot_address_list = get_ballot_address_list()
        ballots_data_raw = get_ballot_data(ballot_address_list)
        ballots = prepare_ballots_data(ballots_data_raw)

    return render_template("ballot/index.html",
                           apptitle = APP_TITLE,
                           titlePrefix = "Abstimmungen",
                           ballots = ballots
                           )


@app.route("/ballots/create")
def create_ballot():

    ballot_durations_in_minutes = [1, 2, 3, 5, 8, 13, 21,]
    return render_template("ballot/showAndCreate.html",
                           apptitle      = APP_TITLE,
                           titlePrefix   = "Abstimmung anlegen",
			   title         = "",
                           data          = {},
                           close_options = ballot_durations_in_minutes,
                           editable      = True,
                           )


@app.route("/ballots", methods=["POST"])
def store_ballot():
    # return redirect("/ballots/123", code=200)
    # title
    # question
    # dateTimeClosing
    print(request.get_data())
    data = request.get_data()
    id = 124
    return redirect(url_for('show_ballot', id=id, data=data))


@app.route("/ballots/<id>")
def show_ballot(id):
    # print(app.config)
    ### TODO: link / address
    if is_dummy():

        r = random.randint(0, 1)

        url_prefix = etherscan_url_prefix()

        ballot = {}
        ballot['id']              = dummy['ballot']['ballots'][r]['id']
        ballot['address']         = dummy['ballot']['ballots'][r]['address']
        ballot['addressLink']     = url_prefix + dummy['ballot']['ballots'][r]['address']
        ballot['title']           = dummy['ballot']['ballots'][r]['title']
        ballot['question']        = dummy['ballot']['ballots'][r]['question']
        ballot['dateTimeClosing'] = dummy['ballot']['ballots'][r]['dateTimeClosing']
        ballot['resultPositive']  = dummy['ballot']['ballots'][r]['resultPositive']
        ballot['resultNegative']  = dummy['ballot']['ballots'][r]['resultNegative']
        ballot['closed']          = dummy['ballot']['ballots'][r]['closed']
        # print(ballot['addressLink'])
    else:
        ballot = {}
        ballots_data_raw = get_ballot_data([id])
        ballots = prepare_ballots_data(ballots_data_raw)
        ballot = ballots[0]

    return render_template("ballot/showAndCreate.html",
                           data        = ballot,
                           apptitle    = APP_TITLE,
                           titlePrefix = "Abstimmung",
			   title       = ballot['title'],
                           )

# @app.route("/ballots/<id>/edit")
# def edit_ballot():
#     pass

# @app.route("/ballots/<id>", methods=["PATCH"])
# def update_ballot():
# pass

# @app.route("/ballots/<id>", methods=["DELETE"])
# def destroy_ballot():
#     pass


@app.route("/votes/<id>/create/")
def create_vote(id):
    ### TODO
    # if ballot['closed']:
    #     return redirect(url_for('index_ballots'))

    return render_template("votes/create.html",
                           apptitle = APP_TITLE,
                           titlePrefix = "Abstimmen",
			   title           = "qwerqwerqwer",
                           data = {},
                           editable        = True,
                           )


@app.route("/votes", methods=["POST"])
def store_vote():
    print(request.get_data())
    data = request.get_data()
    id = 124
    return redirect(url_for('show_ballot', id=id, data=data))


#############################################################################################################################
# api to set new user every api call
# @app.route("/blockchain/user", methods=["POST"])
# def transaction():
#     w3.eth.defaultAccount = w3.eth.accounts[1]
#     # with open("data.json", "r") as f:
#     with open('./smartcontract/ballot/build/contracts/Ballots.json', 'r') as f:
#         datastore = json.load(f)
#     abi = datastore["abi"]
#     # contract_address = datastore["contract_address"]
#     # contract_address = "0x02500eE183Da01E01db093bF016FD8486b45Fd6c"
#     contract_address = app.config['BALLOT_LIST_ADDRESS']


#     # Create the contract instance with the newly-deployed address
#     ballots = w3.eth.contract(
#         address=contract_address,
#         abi=abi,
#     )
#     body = request.get_json()
#     try:
#         result = UserSchema().load(body)
#     except ValidationError as err:
#         return jsonify(err.messages), 422

#     tx_hash = ballots.functions.setUser(result["name"], result["gender"])
#     tx_hash = tx_hash.transact()
#     # Wait for transaction to be mined...
#     w3.eth.waitForTransactionReceipt(tx_hash)

#     ballots_data = ballots.functions.getUser().call()
#     return jsonify({"data": ballots_data}), 200


















if __name__ == "__main__":
    app.run(debug=True)
