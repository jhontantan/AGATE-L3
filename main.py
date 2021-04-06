import os
from time import sleep
from io import StringIO
from io import BytesIO

import pandas as pd
import sqlalchemy as sqla
import json

from flask import Flask, render_template, request, redirect, url_for, send_file
from sqlalchemy import create_engine, exc
from flask_mail import Mail, Message
from config import Config

# PREREQUIS
# pip freeze > requirements.txt
# pip install -r requirements.txt

# BASE DE DONNEES
DB_HOST = "127.0.0.1"
DB_PORT = "5432"
DB_NAME = "agate"
DB_USER = "postgres"
DB_PASS = "root"

# JOINTURE
COM_JOINTURE = 'com14'
CHAMPS_JOINTURE = ['id_deleg', 'deleg', 'tcg18', 'libtcg18', 'alp', 'dep', 'libdep', 'reg', 'libreg']
NOM_TABLE_REFGEO = 'v_passage'

# ADRESSE MAIL
MAIL_ADRESSES_DEST = ['adressedetest73@outlook.fr']  # geomatique@agate-territoires.fr

# --------------- #
# LANCEMENT FLASK
# --------------- #

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/KeyAgathe'
mail = Mail(app)

# ---------- Engine Databse ---------- #
engine = create_engine(
    ('postgresql+psycopg2://' + DB_USER + ':' + DB_PASS + '@' + DB_HOST + ':' + DB_PORT + '/' + DB_NAME),
    pool_recycle=3600)


# INDEX DU SITE WEB
@app.route('/')
def index():
    return render_template('index.html', title='Outil Agate')


# PAGE 404
@app.route('/404')
def page_not_found():
    return render_template('404.html')


# -------------------
# IMPORT D'UN FICHIER
# -------------------
@app.route('/import', methods=['POST'])
def upload_file():
    # Récupération des informations du formulaire
    uploaded_file = request.files['file']
    filename = uploaded_file.filename
    yearData = request.form['year-data']
    yearRef = request.form['year-ref']
    tableName = request.form['table-name']
    commentaire = request.form['commentaire']
    operation = request.form['operation']
    separator = request.form['separateur']

    # Traitement du fichier
    uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))

    # Le traitement varie en fonction de l'extension (CSV, XLSX et ODS supportés)
    if filename[-3:] == "csv":
        df_import = pd.read_csv(os.path.join(app.config['UPLOAD_PATH'], filename), sep=separator,
                                dtype={"com": "string"})
    elif filename[-4:] == "xlsx":
        df_import = pd.read_excel(os.path.join(app.config['UPLOAD_PATH'], filename),
                                  dtype={"com": "string"}, engine="openpyxl")
    elif filename[-3:] == "ods":
        df_import = pd.read_excel(os.path.join(app.config['UPLOAD_PATH'], filename),
                                  dtype={"com": "string"}, engine="odf")
    else:
        return json.dumps("err_ext")

    # Les informations sont liés à un référentiel géographique et importés en base de données
    data_json = lien_ref_geo(df_import, tableName, yearRef, yearData, operation, commentaire)

    # Les informations traitées sont renvoyés à l'affichage sous format JSON
    return data_json


# LIEN ENTRE LES DONNEES IMPORTEES ET UN REFERENTIEL GEOGRAPHIQUE
def lien_ref_geo(dfImport, tableName, yearRef, yearData, operation, commentaire):
    # Rename com -> COM_JOINTURE pour le mettre en index et joindre dessus
    dfImport.rename(columns={'com': COM_JOINTURE}, inplace=True)

    # Récupération v_passage
    champs_jointure = list_to_str(CHAMPS_JOINTURE)

    chaine = 'SELECT ' + COM_JOINTURE + ', com' + yearRef + ', libcom' + yearRef + ', cco' + yearRef + ', libcco' + \
             yearRef + ', ' + champs_jointure + ' FROM ' + NOM_TABLE_REFGEO

    conn = engine.connect()

    # Jointure
    try :
        jointure = pd.read_sql(chaine, conn)
    except sqla.exc.ProgrammingError:
        print("\nUne erreur est survenue lors de la jointure")
        return json.dumps("err_yearref")

    # Suppression COM_JOINTURE du dataframe
    dfRes = jointure.set_index(COM_JOINTURE).join(dfImport.set_index(COM_JOINTURE), how='inner', on=COM_JOINTURE)
    dfRes = dfRes.reset_index()
    dfRes = dfRes.drop(columns=[COM_JOINTURE])

    # GroupBy
    groupby = ["com" + yearRef, "libcom" + yearRef, "cco" + yearRef, "libcco" + yearRef] + CHAMPS_JOINTURE

    # Type de GroupBy
    if operation == "somme":
        dfRes = dfRes.groupby(by=groupby, dropna=False, as_index=False).sum()
    elif operation == "max":
        dfRes = dfRes.groupby(by=groupby, dropna=False, as_index=False).max()
    elif operation == "min":
        dfRes = dfRes.groupby(by=groupby, dropna=False, as_index=False).min()

    # Mise en base
    result = mise_en_base(tableName, dfRes)

    if result == 1:
        return json.dumps("err_name")

    return dfRes.to_json()


# AJOUT D'UNE NOUVELLE TABLE DANS LA BASE DE DONNEES
def mise_en_base(tableName, dataframe):
    # Setup Connexion + definition du curseur
    conn = engine.connect()

    # Recuperation des types
    dataframe_types = get_types(dataframe)

    try:
        dataframe.to_sql(tableName, conn, if_exists='fail', index=False, dtype=dataframe_types)
    except ValueError as vx:
        print("nom en double")
        return 1
    except Exception as ex:
        print(ex)
    else:
        print('La mise en base a été réalisée avec succes ')  # TODO : à remplacer par un feedback au front
    finally:
        conn.close()

    return 0


# TODO : get_types amélioration
# Fonction qui retourne le tableau de types postgres associé au tableau de type dataframe entré
def get_types(dfparam):
    res = {}
    for i, j in zip(dfparam.columns, dfparam.dtypes):
        # if "object" in str(j) and i.startswith('com'):
        #     res.update({i: sqla.types.VARCHAR(length=5)})
        if "object" in str(j):
            res.update({i: sqla.types.VARCHAR(length=255)})
        elif "int" in str(j):
            res.update({i: sqla.types.INT()})
    return res


# prend une liste de strings et retourne la concat de cette liste avec des ','
def list_to_str(liste):
    str = ""
    for i in range(len(liste)):
        if i == (len(liste) - 1):
            str = str + liste[i]
        else:
            str = str + liste[i] + ', '
    return str


# -------------------
# EXPORTER UN FICHIER
# -------------------
@app.route('/export', methods=['POST'])
def download_file():
    content = request.json  # Récupération du json envoyé par l'affichage

    # Séparation des colonnes et du contenu du json
    columns = content[0]
    content.remove(content[0])

    # Création d'un dataframe à partir du contenu et des colonnes
    df_export = pd.DataFrame.from_records(content)
    df_export.columns = columns

    # Conversion du dataframe en CSV et renvoie à l'affichage pour le téléchargement
    df_export.to_csv('export.csv', sep=";", index=False)
    return send_file('export.csv',
                     mimetype='text/csv',
                     attachment_filename='export.csv',
                     as_attachment=True)


# ---------------------------
# ENVOI AUTOMATIQUE D'UN MAIL
# ---------------------------
@app.route('/send')
def send():
    msg = Message('Outil Agate - Traitement : [ajouter nom table]', recipients=MAIL_ADRESSES_DEST)
    msg.body = "A remplir avec des infos complémentaire suivant le besoin du client"

    with app.open_resource("export.csv") as fp:
        msg.attach("export.csv", "text/csv", fp.read())

    mail.send(msg)
    return "Mail envoyé"
