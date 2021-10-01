from dirdem import app

from flask import Flask, render_template, request
from flask_assets import Bundle, Environment

from dirdem.config.dummy import todos
from dirdem.config.conf import load_setting
# from dirdem.config import *
# import dirdem.config.conf as conf
# import dirdem.config

import os

### CONFIGURATION
app.config.update(load_setting())

### ASSETS
assets = Environment(app)
css = Bundle("src/main.css", output="dist/main.css", filters="postcss")
js = Bundle("src/*.js", output="dist/main.js") # new

assets.register("css", css)
assets.register("js", js) # new
css.build()
js.build() # new

APP_TITLE = "dirĐem"

### ROUTES
@app.route("/")
def homepage():
    print(app.config['DB_URI'])
    return render_template("homepage/index.html", apptitle = APP_TITLE)

@app.route("/ballots")
def get_all_ballots():
    print('from-all-ballots')
    title = "tet"
    return render_template("ballot/index.html", title = title)


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
