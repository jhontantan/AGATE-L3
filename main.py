import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

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
app.config['SECRET_KEY'] = '325245hkhf486axcv5719bf9397cbn70xv'



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
    return render_template('index.html')

@app.route('/base')
def test():
    return render_template('base.html')

@app.route('/importation')
def importation():
    return render_template('importation.html')

@app.route('/404')
def page_not_found():
    return render_template('404.html')

# IMPORT
@app.route('/importation', methods=['POST'])
def upload_file():
    uploaded_file = request.files['file']
    filename = uploaded_file.filename
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            return redirect(url_for('page_not_found'))
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
    return redirect(url_for('index'))
 #flash('Document uploaded successfully.')
 #'file uploaded successfully'
