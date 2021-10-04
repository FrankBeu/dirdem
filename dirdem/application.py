from dirdem import app

from flask import Flask, render_template, request, redirect, url_for, request
from flask_assets import Bundle, Environment

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
import web3

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

# w3 = Web3(HTTPProvider("https://kovan.infura.io/v3/YOUR_PROJECT_ID"))
# acct = w3.eth.account.privateKeyToAccount(privateKey)

# w3 = web3.Web3(web3.Web3.HTTPProvider("http://127.0.0.1:8545"))
w3 = web3.Web3(web3.Web3.HTTPProvider(app.config['WEB3_PROVIDER']))
w3.eth.default_account = w3.eth.accounts[0]


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
    app.config['ETHERNET'] = "kovan"
    net_prefix = app.config['ETHERNET'] + "."
    return "https://" + net_prefix + "etherscan.io/address/"


def get_ballot_address_list():
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

    return ballots_data


def create_ballot_smartcontract(title, question, dateTimeClosing):
    timelimit = int(dateTimeClosing) * 60

    ballot_address = deploy_ballot(title, question, timelimit)

    add_ballot_to_ballotList(ballot_address)
    print(ballot_address)

    return ballot_address


def deploy_ballot(title, question, timelimit):
    with open('./smartcontract/build/contracts/Ballot.json', 'r') as f:
        contract_interface = json.load(f)

    ### Instantiate and deploy contract
    Ballot = w3.eth.contract(
        abi=contract_interface["abi"], bytecode=contract_interface["bytecode"]
    )
    ### Get transaction hash from deployed contract
    tx_hash = Ballot.constructor(title, question, timelimit).transact()
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)


    # ballot = w3.eth.contract(
    #     abi=contract_interface["abi"], address=tx_receipt['contractAddress']
    #     )

    address = tx_receipt["contractAddress"]
    print(address)

    return address



def add_ballot_to_ballotList(ballot_address):
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

    tx_hash = ballotList.functions.add_ballot(ballot_address).transact()
    w3.eth.wait_for_transaction_receipt(tx_hash)


def vote_on_ballot(address, vote, id):

    print(address, vote, id)

    with open('./smartcontract/build/contracts/Ballot.json', 'r') as f:
        datastore = json.load(f)
    abi = datastore["abi"]

    contract_address = address

    ### Create the contract instance
    ballot = w3.eth.contract(
        address=contract_address,
        abi=abi,
    )

    tx_hash = ballot.functions.vote(id, vote).transact()
    w3.eth.waitForTransactionReceipt(tx_hash)


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
    ballot_address = create_ballot_smartcontract(request.form['title'], request.form['question'], request.form['dateTimeClosing'])

    return redirect(url_for('show_ballot', id=ballot_address))


@app.route("/ballots/<id>")
def show_ballot(id):
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
    ballot = {}
    ballots_data_raw = get_ballot_data([id])
    ballots = prepare_ballots_data(ballots_data_raw)
    ballot = ballots[0]

    if ballot['closed']:
        return redirect(url_for('index_ballots'))

    return render_template("votes/create.html",
                           apptitle    = APP_TITLE,
                           titlePrefix = "Abstimmen",
			   title       = ballot['title'],
                           data        = ballot,
                           editable    = True,
                           )


@app.route("/votes", methods=["POST"])
def store_vote():
    ballot_address = request.form['address']
    vote = True if request.form['result'] == 'true' else False

    vote_on_ballot(ballot_address, vote, request.form['identification'])

    return redirect(url_for('show_ballot', id=ballot_address))




if __name__ == "__main__":
    app.run(debug=True)
