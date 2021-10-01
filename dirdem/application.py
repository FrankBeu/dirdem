from dirdem import app

from flask import Flask, render_template, request
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
dummy = load_data()

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


### ROUTES
@app.route("/")
def homepage():
    return render_template("homepage/index.html", apptitle = APP_TITLE)


@app.route("/ballots")
def index_ballots():
    return render_template("ballot/index.html",
                           apptitle = APP_TITLE,
                           titlePrefix = "Abstimmungen"
                           )


@app.route("/ballots/create")
def create_ballot():
    return render_template("ballot/showAndCreate.html",
                           apptitle = APP_TITLE,
                           titlePrefix = "Abstimmung anlegen",
			   title           = "",
                           data = {},
                           editable        = True,
                           )


@app.route("/ballots", methods=["POST"])
def store_ballot():
    pass


@app.route("/ballots/<id>")
def show_ballot(id):
    print(app.config)
    ### TODO: link / address
    if is_dummy():

        r = random.randint(0, 1)

        ### TODO: set ethernet only if production
        app.config['ethernet'] = "kovan"
        net_prefix = app.config['ethernet'] + "."
        etherscan_url_prefix = "https://" + net_prefix + "etherscan.io/address/"

        ballot = {}
        ballot['id']              = dummy['ballot']['ballots'][r]['id']
        ballot['address']         = dummy['ballot']['ballots'][r]['address']
        ballot['address-link']    = etherscan_url_prefix + dummy['ballot']['ballots'][r]['address']
        ballot['title']           = dummy['ballot']['ballots'][r]['title']
        ballot['question']        = dummy['ballot']['ballots'][r]['question']
        ballot['dateTimeClosing'] = dummy['ballot']['ballots'][r]['dateTimeClosing']
        ballot['resultPositive']  = dummy['ballot']['ballots'][r]['resultPositive']
        ballot['resultNegative']  = dummy['ballot']['ballots'][r]['resultNegative']
        ballot['closed']          = dummy['ballot']['ballots'][r]['closed']
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
