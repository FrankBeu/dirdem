from dirdem import app

from flask import Flask, render_template, request, redirect, url_for
from flask_assets import Bundle, Environment

from dirdem.config.dummy import todos
from dirdem.config.conf import load_setting
from dirdem.dummy.dummy import load_data
# from dirdem.config import *
# import dirdem.config.conf as conf
# import dirdem.config

import os
import random

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
    if (app.config['ENV'] == 'fake') or (app.config['ENV'] == 'dev'):
        ### TODO only dev has hotreload
        # if (app.config['ENV'] == 'fake'):
        ### otherwise hot reload is useless
        global dummy
        dummy = load_data()
        return True

    return False

# class Utility:

def etherscan_url_prefix():
    ### TODO: set ethernet only if production
    app.config['ethernet'] = "kovan"
    net_prefix = app.config['ethernet'] + "."
    return "https://" + net_prefix + "etherscan.io/address/"


# util = Utility()

### ROUTES
@app.route("/")
def homepage():
    return render_template("homepage/index.html", apptitle = APP_TITLE)


@app.route("/ballots")
def index_ballots():
    ballots = []
    if is_dummy():

        r = random.randint(0, 1)

        url_prefix = etherscan_url_prefix()
        dummies = dummy['ballot']['ballots']

        for fake in dummies:
            ballot = {}
            ballot['id']              = fake['id']
            ballot['address']         = fake['address']
            ballot['addressLink']     = url_prefix + fake['address']
            ballot['title']           = fake['title']
            ballot['question']        = fake['question']
            ballot['dateTimeClosing'] = fake['dateTimeClosing']
            ballot['resultPositive']  = fake['resultPositive']
            ballot['resultNegative']  = fake['resultNegative']
            ballot['closed']          = fake['closed']

            ballots.append(ballot)


        # print(ballot['addressLink'])
    else:
        ballot = {}
        ballot['title'] = id


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
        ballot['addressLink']    = url_prefix + dummy['ballot']['ballots'][r]['address']
        ballot['title']           = dummy['ballot']['ballots'][r]['title']
        ballot['question']        = dummy['ballot']['ballots'][r]['question']
        ballot['dateTimeClosing'] = dummy['ballot']['ballots'][r]['dateTimeClosing']
        ballot['resultPositive']  = dummy['ballot']['ballots'][r]['resultPositive']
        ballot['resultNegative']  = dummy['ballot']['ballots'][r]['resultNegative']
        ballot['closed']          = dummy['ballot']['ballots'][r]['closed']
        # print(ballot['addressLink'])
    else:
        ballot = {}
        ballot['title'] = id

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


@app.route("/search", methods=["POST"])
def search_todo():
    search_term = request.form.get("search")

    if not len(search_term):
        return render_template("todo.html", todos=[])

    res_todos = []
    for todo in todos:
        if search_term in todo["title"]:
            res_todos.append(todo)

    return render_template("todo.html", todos=res_todos)




if __name__ == "__main__":
    app.run(debug=True)
