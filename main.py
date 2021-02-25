import csv
import os
import pandas as pd
import psycopg2
import psycopg2.extras

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, send_file
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask import flash
from os import environ
import sqlalchemy as sqlA
from sqlalchemy import create_engine

# Info bdd
DB_HOST = "localhost"
DB_NAME = "agate"
DB_USER = "postgres"
DB_PASS = "user"

# pip freeze > requirements.txt
# pip install -r requirements.txt

# pour faire fonctionner le tableau, installer npm puis :
# node.js
# npm install handsontable


# dataFrame pandas (tableau deux dimension) vide à utiliser pour traitement de donnes
df = pd.DataFrame()
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://postgres:user@127.0.0.1:5432/agate"
db_uri = environ.get('SQLALCHEMY_DATABASE_URI')

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


# @Site

@app.route('/')
def index():
    return render_template('index.html', title='Outil Agate')


@app.route('/base')
def test():
    return render_template('base.html')


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
    annee = request.form['yearValue']
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            flash('error ', 'danger')
            return redirect(url_for('index'))
        flash('Le chargement a été réalisé avec succès ', 'success')
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        # traitement ficher
        global df
        df = pd.read_csv(os.path.join(app.config['UPLOAD_PATH'], filename), sep=";")
        lienRefGeo(annee)
        return redirect(url_for('index'))

    flash('Choisissez un fichier ', 'danger')
    # On appel la fonction refGeo
    return redirect(url_for('index'))


# RegGeo
@app.route('/testRef')
def lienRefGeo(annee):
    # Trucs utiles
    # conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    # cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    tableName = 'insees_2012_com19_pop'

    # com = 'com' + annee
    # libcom = 'libcom' + annee
    # df.rename(columns={'com': com, 'libcom': libcom}, inplace=True)

    tab = get_types(df)

    creation_temp_table(tableName, annee)

    # Recupération v_passage
    #
    # chaine = ''
    # for i in range(14,int(annee),1):
    #     chaine += 'com'+ str(i) + ', libcom' + str(i) + ', cco'+ str(i) + ', '
    # chaine = chaine.rstrip(chaine[-2])
    # chaine += ' dep, libdep, tcg18, libtcg18, reg, libreg, id_deleg, deleg,'
    # print('Chaine : ')
    # print(chaine)

    return redirect(url_for('index'))


# EXPORT
@app.route('/export', methods=['GET'])
def download_file():
    global df
    df.to_csv('export.csv', sep=";", index=False)
    return send_file('export.csv',
                     mimetype='text/csv',
                     attachment_filename='export.csv',
                     as_attachment=True)


# UPDATE
@app.route('/update', methods=['GET', 'POST'])
def update_dataframe():
    global df
    df_dic = df.to_dict('records')
    json = df.to_json(orient='records')
    return render_template('index.html', title='Outil Agate', data=json)

## Fonctions annexes
def creation_temp_table(name, annee):
    # Setup Connexion + definition du curseur

    engine = create_engine('postgresql+psycopg2://postgres:user@127.0.0.1:5432/agate', pool_recycle=3600)
    conn = engine.connect()

    # Recuperation des types
    df_types = get_types(df)

    # Demander une liste des villes à fusionner
    # listeVille = ['Lyon', 'Marseille']
    # Recuperation com{Annee} et libcom{Anne1e} (Ajout de sécurité nécéssaire si maintenu)


    try:
        frame = df.to_sql((name + '_temp'), conn, if_exists='replace', index=False, dtype=df_types)
    except ValueError as vx:
        print(vx)
    except Exception as ex:
        print(ex)
    else:
        print("PostgreSQL Table %s has been created successfully." % name)
    finally:

        conn.close()

    # Fusion des villes (ébauche)
    # conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    # cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # for i in range(len(listeVille)):
    #     cur.execute("UPDATE (name) SET (colonne)", (name+'_temp'), (listeVille[i]))

def get_types(dfparam):
    res = {}
    for i, j in zip(dfparam.columns, dfparam.dtypes):
        # if "object" in str(j) and i.startswith('com'):
        #     res.update({i: sqlA.types.VARCHAR(length=5)})
        if "object" in str(j):
            res.update({i: sqlA.types.VARCHAR(length=255)})
        elif "int" in str(j):
            res.update({i: sqlA.types.INT()})
    return res
