import os
from time import sleep
from io import StringIO
from io import BytesIO

import pandas as pd
import sqlalchemy as sqla

from flask import Flask, render_template, request, redirect, url_for, send_file
from flask import flash
from sqlalchemy import create_engine
from flask_mail import Mail, Message
from config import Config

# ---------- Informations ---------- #
# Prérequis
# pip freeze > requirements.txt
# pip install -r requirements.txt

# Database
DB_HOST = "127.0.0.1"
DB_PORT = "5432"
DB_NAME = "agate"
DB_USER = "postgres"
DB_PASS = "root"

# JOINTURE
COM_JOINTURE = 'com14'
CHAMPS_JOINTURE = ['id_deleg', 'deleg', 'tcg18', 'libtcg18', 'alp', 'dep', 'libdep', 'reg', 'libreg']
NOM_TABLE_REFGEO = 'v_passage'

# Mail
MAIL_ADRESSES_DEST = ['adressedetest73@outlook.fr'] # geomatique@agate-territoires.fr
# ---------------------------------- #

# Dataframe global
df = pd.DataFrame()

# ----- Lancement de l'app ----- #
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/KeyAgathe'
mail = Mail(app)

# ---------- Engine Databse ---------- #
engine = create_engine('postgresql+psycopg2://postgres:user@127.0.0.1:5432/agate', pool_recycle=3600)

# @Routes
@app.route('/')
def index():
    return render_template('index.html', title='Outil Agate')


@app.route('/base')
def test():
    return render_template('base.html')


@app.route('/404')
def page_not_found():
    return render_template('404.html')


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
    operation = request.form['operation']
    separator = request.form['separateur']

    uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
    # traitement ficher
    df_import = pd.DataFrame()
    df_import = pd.read_csv(os.path.join(app.config['UPLOAD_PATH'], filename), sep=";",
                            dtype={"com": "string"})
    data: pd.DataFrame = lienRefGeo(df_import, tableName, yearRef, yearData, commentaire)

    return data.to_json()

# RegGeo
def lienRefGeo(dfImport, tableName, yearRef, yearData, commentaire):
    # Rename com -> COM_JOINTURE pour le mettre en index et joindre dessus
    dfImport.rename(columns={'com': COM_JOINTURE}, inplace=True)

    ### Récupération v_passage

    champs_jointure = list_to_str(CHAMPS_JOINTURE)

    chaine = 'SELECT ' + COM_JOINTURE + ', com' + yearRef + ', libcom' + yearRef + ', cco' + yearRef + ', libcco' + \
             yearRef + ', ' + champs_jointure + ' FROM ' + NOM_TABLE_REFGEO

    conn = engine.connect()

    jointure = pd.read_sql(chaine, conn)

    ### Jointure
    dfRes = jointure.set_index(COM_JOINTURE).join(dfImport.set_index(COM_JOINTURE), how='inner', on=COM_JOINTURE)

    # Suppression COM_JOINTURE du dataframe
    dfRes = dfRes.reset_index()
    dfRes = dfRes.drop(columns=[COM_JOINTURE])

    ### GroupBy
    groupby = ["com" + yearRef, "libcom" + yearRef, "cco" + yearRef, "libcco" + yearRef] + CHAMPS_JOINTURE

    ### Type de GroupBy
    if (operation == "somme"):
        dfRes = dfRes.groupby(by=groupby, dropna=False, as_index=False).sum()
    elif (operation == "max"):
        dfRes = dfRes.groupby(by=groupby, dropna=False, as_index=False).max()
    elif (operation == "min"):
        dfRes = dfRes.groupby(by=groupby, dropna=False, as_index=False).min()
    else:
        flash("Veuillez indiquer l'opération que vous souhaitez executer : Somme / Max / Min", 'danger')

    print(dfRes)

    ### Mise en base
    mise_en_base(tableName, dfRes)

    return dfRes


# EXPORT
@app.route('/export', methods=['GET'])
def download_file():
    global df  # TODO: remove
    df.to_csv('export.csv', sep=";", index=False)
    return send_file('export.csv',
                     mimetype='text/csv',
                     attachment_filename='export.csv',
                     as_attachment=True)

# MAIL
@app.route('/send')
def send():
   msg = Message('Outil Agate - Traitement : [ajouter nom table]', recipients=MAIL_ADRESSES_DEST)
   msg.body = "A remplir avec des infos complémentaire suivant le besoin du client"

   with app.open_resource("export.csv") as fp:
      msg.attach("export.csv", "text/csv", fp.read())

   mail.send(msg)
   return "Mail envoyé"

# UPDATE
@app.route('/update', methods=['GET', 'POST'])
def update_dataframe():
    global df  # TODO: remove
    df_dic = df.to_dict('records')
    json = df.to_json(orient='records')
    return render_template('index.html', title='Outil Agate', data=json)


# Fonction qui met en base le dataframe sous le nom 'tableName'
def mise_en_base(tableName, dataframe):

    conn = engine.connect()

    # Recuperation des types
    dataframe_types = get_types(dataframe)

    try:
        dataframe.to_sql((tableName), conn, if_exists='fail', index=False, dtype=dataframe_types)
    except ValueError as vx:
        flash('Une table de ce nom existe déja', 'danger')
    except Exception as ex:
        print(ex)
    else:
        flash('La mise en base a été réalisée avec succes ', 'success')
    finally:
        conn.close()


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