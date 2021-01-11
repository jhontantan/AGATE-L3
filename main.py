from flask import Flask, url_for

app = Flask(__name__)


@app.route('/')
def affiche_logo():
    return '<img src=' + url_for('static', filename='logo_Agate.jpg') + '>'


def hello_world():
    return 'Hello Word !'





@app.route('/profil/<username>/<age>')
def profil(username, age):
    return 'Bravo ' + username + ' vous avez ' + age + ' ans !'
