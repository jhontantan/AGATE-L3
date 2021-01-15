import os
from flask import Flask, render_template
# from flask_sqlalchemy import SQLAlchemy


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # Des trucs qui seront surrement la
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:user@localhost/Agate'
    # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # db = SQLAlchemy(app)

    app.config.from_mapping(SECRET_KEY='dev')

    # -------------------------- #
    # ---------- Test ---------- #
    # -------------------------- #
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # ---------------------------- #
    # ---------- Routes ---------- #
    # ---------------------------- #
    @app.route('/')
    def index():
        return render_template('index.html')

    return app
