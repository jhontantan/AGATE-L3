import csv
import os
import pandas as pds

from flask import Flask, render_template, request, redirect, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask import flash

# pip freeze > requirements.txt
# pip install -r requirements.txt

app = Flask(__name__)
# Attention le mdp la celui de votre BDD                        V
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:user@127.0.0.1:5432/v_passage"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#  IMPORT
app.config['UPLOAD_EXTENSIONS'] = ['.csv']
app.config['UPLOAD_PATH'] = 'temp'
# app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024   //taille ficher 4MB
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/KeyAgathe'



class v_passage(db.Model):
    __tablename__ = 'v_passage'
    com14 = db.Column(db.String(10), primary_key=True)
    libcom14 = db.Column(db.String(150), nullable=False)
    geom = db.Column(db.String(30000), nullable=False)
    com15 = db.Column(db.String(10), nullable=False)
    libcom15 = db.Column(db.String(150), nullable=False)
    com16 = db.Column(db.String(10), nullable=False)
    libcom16 = db.Column(db.String(150), nullable=False)
    com17 = db.Column(db.String(10), nullable=False)
    libcom17 = db.Column(db.String(150), nullable=False)
    com18 = db.Column(db.String(10), nullable=False)
    libcom18 = db.Column(db.String(150), nullable=False)
    com19 = db.Column(db.String(10), nullable=False)
    libcom19 = db.Column(db.String(150), nullable=False)
    com20 = db.Column(db.String(10), nullable=False)
    libcom20 = db.Column(db.String(150), nullable=False)
    cco15 = db.Column(db.String(9), nullable=True)
    libcco15 = db.Column(db.String(150), nullable=True)
    cco16 = db.Column(db.String(9), nullable=True)
    libcco16 = db.Column(db.String(150), nullable=True)
    cco17 = db.Column(db.String(9), nullable=True)
    libcco17 = db.Column(db.String(150), nullable=True)
    cco18 = db.Column(db.String(9), nullable=True)
    libcco18 = db.Column(db.String(150), nullable=True)
    cco19 = db.Column(db.String(9), nullable=True)
    libcco19 = db.Column(db.String(150), nullable=True)
    cco20 = db.Column(db.String(9), nullable=True)
    libcco20 = db.Column(db.String(150), nullable=True)

    def __repr__(self):
        return '<v_passage %r>' % self.id

    # def __init__(self, name, model, doors):
    #     self.name = name
    #     self.model = model
    #     self.doors = doors
    #


# @Site

@app.route('/')
def index():
    return render_template('index.html', title='Outil Agate')


@app.route('/base')
def test():
    return render_template('base.html')

@app.route('/importation')
def importation():
    return render_template('importation.html')

@app.route('/404')
def page_not_found():
    return render_template('404.html')


from io import StringIO
from io import BytesIO

# IMPORT
@app.route('/', methods=['POST'])
def upload_file():
    # charger le ficher dans le serveur

    uploaded_file = request.files['file']
    filename = uploaded_file.filename
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            flash('error ', 'danger')
            return redirect(url_for('index'))
        flash('Le chargement a été réalisé avec succès ', 'success')
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))

    # traitment ficher
    print(uploaded_file)
    df=pds.read_csv(os.path.join(app.config['UPLOAD_PATH'], filename), sep=";", header=None)
    print(df)
    return redirect(url_for('index'))



# EXPORT

from flask import send_file


import datetime

@app.route('/export', methods=['GET'])
def download_file():
    filename = 'Export_Agate.csv'
    row = ['hello', 'world']
    proxy = StringIO()

    writer = csv.writer(proxy)
    writer.writerow(row)

    # Creating the byteIO object from the StringIO Object
    mem = BytesIO()
    mem.write(proxy.getvalue().encode())
    # seeking was necessary. Python 3.5.2, Flask 0.12.2
    mem.seek(0)
    proxy.close()

    return send_file(
        mem,
        as_attachment=True,
        attachment_filename=filename,
        mimetype='text/csv'
    )
