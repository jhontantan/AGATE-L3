import csv
import os
import pandas as pd
import psycopg2
import psycopg2.extras

from flask import Flask, render_template, request, redirect, url_for, send_from_directory
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
# npm install handsontable


# dataFrame pandas (tableau deux dimension) vide à utiliser pour traitement de donnes
df = pd.DataFrame()
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://postgres:user@127.0.0.1:5432/agate"
engine = create_engine('postgresql+psycopg2://postgres:user@127.0.0.1:5432/agate', pool_recycle=3600)
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
    #


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
@app.route('/import', methods=['POST'])
def upload_file():
    # charger le ficher dans le serveur
    uploaded_file = request.files['file']
    filename = uploaded_file.filename
    yearData = request.form['year-data']
    yearRef = request.form['year-ref']
    tableName = request.form['table-name']
    commentaire = request.form['commentaire']

    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            flash('error ', 'danger')
            return redirect(url_for('index'))
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        # traitment ficher
        global df
        df = pd.read_csv(os.path.join(app.config['UPLOAD_PATH'], filename), sep=";", dtype={"com":"string"})
        lienRefGeo(tableName, yearRef, yearData, commentaire)
        return redirect(url_for('index'))

    flash('Choisissez un fichier ', 'danger')
    # On appel la fonction refGeo
    return redirect(url_for('index'))


# RegGeo
@app.route('/testRef')
def lienRefGeo(tableName, yearRef, yearData, commentaire):
    # Trucs utiles
    # conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    # cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    com = 'com14'
    df.rename(columns={'com': com}, inplace=True)

    tab = get_types(df)

    # Création table temporaire
    # cur.execute('DROP TABLE IF EXISTS (%s);', (tableName,))
    # cur.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")

    # print(cur.fetchall())
    # print(cur.fetchone()['name'])

    # conn.commit()
    # conn.close()

    # Fonction qui met en base le csv
    # creation_temp_table(tableName, yearRef, yearData, commentaire)

    # Recupération v_passage

    # Ajouter une variable globale
    chaine = 'SELECT com14, '
    chaine += 'com' + yearRef + ', libcom' + yearRef + ', cco' + yearRef + ', libcco' + yearRef + ','
    chaine += ' id_deleg, deleg, tcg18, libtcg18, alp, dep, libdep,  reg, libreg FROM v_passage'

    # Setup Connexion
    conn = engine.connect()
    # print(df['com'])
    jointure = pd.read_sql(chaine, conn)
    # print("Jointure : ")

    # print("Données : ")
    # print(df.columns.values.tolist())
    # print(df)

    # dfRes = jointure.set_index('com14').join(df.set_index('com14'), how='left', on='com14')
    dfRes = df.set_index('com14').join(jointure.set_index('com14'), how='left', on='com14')
    # print(dfRes.columns.values.tolist())
    # dfRes = dfRes.drop(dfRes.columns['com14'], axis=1)


    groupby = ["com14", "com" + yearRef, "libcom" + yearRef, "cco" + yearRef, "libcom" + yearRef, "id_deleg", "deleg", "tcg18", "libtcg18", "alp", "dep",
               "libdep",
               "reg", "libreg"]
    dfRes.groupby(by=groupby).sum()

    print(dfRes.columns.values.tolist())


    # # Mise en base
    # df_types = get_types(dfRes)
    # try:
    #     frame = dfRes.to_sql((tableName), conn, if_exists='fail', index=False, dtype=df_types)
    # except ValueError as vx:
    #     flash('Une table de ce nom existe déja', 'danger')
    # except Exception as ex:
    #     print(ex)
    # else:
    #     flash('Le chargement a été réalisé avec succès ', 'success')
    # finally:
    #     conn.close()
    print(dfRes)

    return redirect(url_for('index'))


# EXPORT

from flask import send_file


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


import psycopg2.extras


## Fonctions annexes
def creation_temp_table(name, yearRef, yearData, commentaire):
    # Setup Connexion + definition du curseur

    conn = engine.connect()

    # Recuperation des types
    df_types = get_types(df)
    print(yearRef, yearData, commentaire)

    try:
        frame = df.to_sql((name + '_temp'), conn, if_exists='fail', index=False, dtype=df_types)
    except ValueError as vx:
        flash('Une table de ce nom existe déja', 'danger')
    except Exception as ex:
        print(ex)
    else:
        flash('Le chargement a été réalisé avec succès ', 'success')
    finally:
        conn.close()


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
