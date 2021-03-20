import os
import pandas as pd
import sqlalchemy as sqla

from flask import Flask, render_template, request, redirect, url_for, send_file
from flask import flash
from sqlalchemy import create_engine

# Info bdd
DB_HOST = "localhost"
DB_NAME = "agate"
DB_USER = "postgres"
DB_PASS = "user"

# JOINTURE
COM_JOINTURE = 'com14'
CHAMPS_JOINTURE = 'id_deleg, deleg, tcg18, libtcg18, alp, dep, libdep,  reg, libreg'
NOM_TABLE_REFGEO = 'v_passage'

# pip freeze > requirements.txt
# pip install -r requirements.txt

# Dataframe global
df = pd.DataFrame()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://postgres:user@127.0.0.1:5432/agate"
engine = create_engine('postgresql+psycopg2://postgres:user@127.0.0.1:5432/agate', pool_recycle=3600)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


#  IMPORT
app.config['UPLOAD_EXTENSIONS'] = ['.csv']
app.config['UPLOAD_PATH'] = 'temp'
# app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024   //taille ficher 4MB
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/KeyAgathe'


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
            flash("Erreur d'import ", 'danger')
            return redirect(url_for('index'))
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        # traitement ficher
        global df
        df = pd.read_csv(os.path.join(app.config['UPLOAD_PATH'], filename), sep=";", dtype={"com": "string"})
        lienRefGeo(tableName, yearRef, yearData, commentaire)
        return redirect(url_for('index'))
    flash('Choisissez un fichier ', 'danger')
    return redirect(url_for('index'))


# RegGeo
# TODO : lienRefGeo : mieux gérer les types lors de l'export en bdd et ajout commentaire
@app.route('/testRef')
def lienRefGeo(tableName, yearRef, yearData, commentaire):
    # Rename com -> COM_JOINTURE pour le mettre en index et joindre dessus
    df.rename(columns={'com': COM_JOINTURE}, inplace=True)

    ### Recupération v_passage

    chaine = 'SELECT ' + COM_JOINTURE + ', com' + yearRef + ', libcom' + yearRef + ', cco' + yearRef + ', libcco' + \
             yearRef + ', ' + CHAMPS_JOINTURE + ' FROM ' + NOM_TABLE_REFGEO

    conn = engine.connect()

    jointure = pd.read_sql(chaine, conn)

    ### Jointure
    dfRes = jointure.set_index(COM_JOINTURE).join(df.set_index(COM_JOINTURE), how='inner', on=COM_JOINTURE)

    # Suppression COM_JOINTURE du dataframe
    dfRes = dfRes.reset_index()
    dfRes = dfRes.drop(columns=[COM_JOINTURE])

    ### GroupBy
    groupby = ["com" + yearRef, "libcom" + yearRef, "cco" + yearRef, "id_deleg", "deleg", "tcg18",
               "libtcg18", "alp", "dep", "libdep", "reg", "libreg"]

    # Somme
    dfRes = dfRes.groupby(by=groupby, dropna=False, as_index=False).sum()

    print(dfRes)

    ### Mise en base
    mise_en_base(tableName, dfRes)

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
