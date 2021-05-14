import linecache
import os
import pandas as pd
import sqlalchemy as sqla
from flask import Flask, render_template, request, send_file, redirect, url_for, session
from flask import flash
import json
from flask_mail import Mail, Message
from sqlalchemy import create_engine, exc
from threading import Thread
from config import Config
from unidecode import unidecode

# ---------- Informations ---------- #
# Prérequis
# pip freeze > requirements.txt
# pip install -r requirements.txt


# JOINTURE
COM_JOINTURE = 'com14'
CHAMPS_JOINTURE_DEPENDANT_ANNEE = ['com', 'libcom', 'cco', 'libcco']
CHAMPS_JOINTURE = ['id_deleg', 'deleg', 'tcg18', 'libtcg18', 'alp', 'dep', 'libdep', 'reg', 'libreg']
NOM_TABLE_REFGEO = 'v_passage'



# ----- Lancement de l'app ----- #
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/KeyAgathe'
mail = Mail(app)

# ---------- Engine Databse ---------- #
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, pool_recycle=3600)


# ---------- Connexion Admin ------- #

class User:
    def __init__(self, password):
        self.id = 1
        self.username = 'admin'
        self.password = password

    def __repr__(self):
        return f'<User: {self.password}>'


user = [User(password=Config.ADMIN_PASSWORD)]


# @Routes
# INDEX DU SITE WEB
@app.route('/')
def index():
    return render_template('index.html', title='Outil Agate')


@app.route('/404')
def page_not_found():
    return render_template('404.html')


@app.route('/admin', methods=['POST'])
def admin_menu():
    global liste_mots
    if 'username' in session:

        # PARTIE nouveau mot de passe admin #
        if request.form.get("mdp_admin"):
            mdp_admin = request.form.get('mdp_admin')
            mdp_admin2 = request.form.get('mdp_admin2')
            if mdp_admin == mdp_admin2 and mdp_admin != "":

                fo = open('config.py', 'r')
                #ligne = linecache.getline("config.py", 35)

                lines = fo.readlines()
                for line in lines:
                    if "ADMIN_PASSWORD" in line:
                        liste_mots = line.split()

                mot2 = liste_mots[2]
                mdp_admin = str("\'") + mdp_admin + str("\'")
                fo.close()

                modif = open('config.py', 'r+').read().replace(mot2, mdp_admin)
                f1 = open('config.py', 'w')
                f1.write(modif)
                f1.close()
            return render_template('admin.html')

        # PARTIE nouveau mot de passe adresse expeditrice #
        if request.form.get("mdp_adr_exp"):
            mdp_adr_exp = request.form.get('mdp_adr_exp')
            mdp_adr_exp2 = request.form.get('mdp_adr_exp2')

            if mdp_adr_exp == mdp_adr_exp2 and mdp_adr_exp != "":

                fo = open('config.py', 'r')
                #ligne2 = linecache.getline("config.py", 25)
                lignes = fo.readlines()
                for ligne in lignes:
                    if "MAIL_PASSWORD" in ligne:
                        liste_mots = ligne.split()

                mot = liste_mots[2]
                mdp_adr_exp = str("\'") + mdp_adr_exp + str("\'")
                fo.close()

                modif2 = open('config.py', 'r+').read().replace(mot, mdp_adr_exp)
                f1 = open('config.py', 'w')
                f1.write(modif2)
                f1.close()

            return render_template('admin.html')

        if request.form.get("logout"):
            session.pop('username', None)
            return redirect(url_for('index'))

    return redirect(url_for('index'))


@app.route('/connexion', methods=['GET', 'POST'])
def connexion():
    if 'username' in session:
        return render_template('admin.html')
    if request.method == 'POST':
        password = request.form.get('password')
        if user[0].password == password:
            session['username'] = user[0].username
            return render_template('admin.html')
        else:
            flash('error', 'danger')
    return render_template('connexion.html')

# -------------------
# IMPORT D'UN FICHIER
# -------------------
@app.route('/import_operation', methods=['POST'])
def get_operations():
    uploaded_file = request.files['file']
    filename = uploaded_file.filename
    separator = request.form['separateur']

    # Enregistrement du fichier en local
    uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))

    try:
        if filename[-3:] == "csv":
            df_import = pd.read_csv(os.path.join(app.config['UPLOAD_PATH'], filename), sep=separator, nrows=1)
        elif filename[-4:] == "xlsx":
            df_import = pd.read_excel(os.path.join(app.config['UPLOAD_PATH'], filename), engine="openpyxl", nrows=1)
        elif filename[-3:] == "ods":
            df_import = pd.read_excel(os.path.join(app.config['UPLOAD_PATH'], filename), engine="odf", nrows=1)
        else:
            return json.dumps("err_ext")
    except pd.errors.EmptyDataError:
        return json.dumps("err_empty")

    empty_lines = has_empty_header(df_import.columns.tolist())
    empty_columns = df_import.isnull().values.any()

    if empty_lines or empty_columns:
        df = open_full_file(os.path.join(app.config['UPLOAD_PATH'], filename), filename, separator)
        df_import = remove_empty_lines(df, empty_lines, empty_columns)
        save_file(df_import, os.path.join(app.config['UPLOAD_PATH'], filename), filename, separator)

    # df_import.columns = remove_specialchar(df_import.columns.tolist())

    df_res = pd.DataFrame({}, columns=df_import.columns)
    return df_res.to_json()


def has_empty_header(headers):
    for header in headers:
        if "Unnamed" not in header:
            return False
    return True


def open_full_file(path, name, sep):
    if name[-3:] == "csv":
        return pd.read_csv(path, sep=sep)
    elif name[-4:] == "xlsx":
        return pd.read_excel(path, engine="openpyxl")
    elif name[-3:] == "ods":
        return pd.read_excel(path, engine="odf")


def remove_empty_lines(df, empty_lines, empty_columns):
    df_new = pd.DataFrame()
    if empty_columns:
        df_new = df.dropna(axis=1, how='all')
        df_new = df_new.reset_index(drop=True)

    if empty_lines:
        df_new = df_new.dropna(axis=0, how='all')
        new_header = df_new.iloc[0]
        df_new = df_new[1:]
        df_new.columns = remove_specialchar(new_header.tolist())

    return df_new


def save_file(df, path, name, sep):
    if name[-3:] == "csv":
        df.to_csv(path, sep=sep, index=False)
    elif name[-4:] == "xlsx":
        df.to_excel(path, engine="openpyxl", index=False)
    elif name[-3:] == "ods":
        df.to_excel(path, engine="odf", index=False)


@app.route('/import', methods=['POST'])
def upload_file():
    # Récupération des informations du formulaire
    filename = get_name(request.form['filename'])
    year_ref = request.form['year-ref']
    table_name = request.form['table-name']
    commentaire = request.form['commentaire']
    operation = request.form['operation']
    separator = request.form['separateur']
    com = request.form['col_com']

    tab_ops = []
    tab_sum = []
    tab_max = []
    tab_min = []

    # Recuperation des infos relatives aux op/colonnes
    for col in request.form:
        if col.startswith("drpd_") and col[5:] != com:
            if request.form[col] != "ignorer":
                tab_ops.append(col[5:])
            if request.form[col] == "somme":
                tab_sum.append(col[5:])
            elif request.form[col] == "max":
                tab_max.append(col[5:])
            elif request.form[col] == "min":
                tab_min.append(col[5:])
            else:
                print("Op non trouvé")

    # Traitement du fichier
    # Le traitement varie en fonction de l'extension (CSV, XLSX et ODS supportés)
    try:
        if filename[-3:] == "csv":
            df_import = pd.read_csv(os.path.join(app.config['UPLOAD_PATH'], filename), sep=separator,
                                    dtype={com: "string"})
        elif filename[-4:] == "xlsx":
            df_import = pd.read_excel(os.path.join(app.config['UPLOAD_PATH'], filename),
                                      dtype={com: "string"}, engine="openpyxl")
        elif filename[-3:] == "ods":
            df_import = pd.read_excel(os.path.join(app.config['UPLOAD_PATH'], filename),
                                      dtype={com: "string"}, engine="odf")
        else:
            return json.dumps("err_ext")
    except pd.errors.EmptyDataError:
        return json.dumps("err_empty")

    # Homogénéisation des codes INSEE : doit faire 5 caractères maximum
    df_import[com] = clean_codesINSEE(df_import[com].tolist())

    # Les informations sont liés à un référentiel géographique
    data_json = lien_ref_geo(df_import, com, year_ref, commentaire, tab_ops, tab_sum, tab_max, tab_min)

    # Les informations traitées sont renvoyés à l'affichage sous format JSON
    return data_json


def clean_codesINSEE(all_codes):
    new_codes = []
    for code in all_codes:
        if len(code) > 5 and code[0] == "0":
            c = code[0]
            while c == "0":
                code = code[1:]
                c = code[0]
        if len(code) > 5 and code[-1] == "0":
            c = code[-1]
            while c == "0":
                code = code[:-1]
                c = code[-1]
        new_codes.append(code)
    return new_codes


# LIEN ENTRE LES DONNEES IMPORTEES ET UN REFERENTIEL GEOGRAPHIQUE
def lien_ref_geo(df_import, com, year_ref, commentaire, tab_ops, tab_sum, tab_max, tab_min):
    # Rename com -> COM_JOINTURE pour le mettre en index et joindre dessus
    df_import.rename(columns={com: COM_JOINTURE}, inplace=True)

    # Récupération v_passage
    champs_jointure = list_to_str(CHAMPS_JOINTURE)
    champs_jointure_dependant_annee = list_with_year_to_str(CHAMPS_JOINTURE_DEPENDANT_ANNEE, year_ref)

    chaine = 'SELECT ' + COM_JOINTURE + ', ' + champs_jointure_dependant_annee + ', ' + champs_jointure + ' FROM ' + NOM_TABLE_REFGEO
    conn = engine.connect()

    try:
        jointure = pd.read_sql(chaine, conn)
    except sqla.exc.ProgrammingError:
        print("\nUne erreur est survenue lors de la récupération dans v_passage")
        return json.dumps("err_yearref")

    ### Suppression des potentiels doublons
    cols_jointure = jointure.columns.values.tolist()
    cols_dfImport = df_import.columns.values.tolist()
    for col in cols_jointure:
        if col != COM_JOINTURE and col in cols_dfImport:
            del df_import[str(col)]

    # Champs GroupBy
    groupby = list_with_year_to_list_with_choosen_year(CHAMPS_JOINTURE_DEPENDANT_ANNEE, year_ref) + CHAMPS_JOINTURE
    comXX = get_com(groupby)

    ### Gestion des différentes opérations

    # Dataframe intermediaire contenant code INSEE et comXX.
    # Permet les jointures et groupby sans entrainer tous les autres champs
    jointure_op = pd.DataFrame(jointure[[COM_JOINTURE, comXX]], columns=[COM_JOINTURE, comXX])

    # Somme

    df_sum = pd.DataFrame(df_import[[COM_JOINTURE] + tab_sum], columns=[COM_JOINTURE] + tab_sum)
    df_sum = jointure_op.set_index(COM_JOINTURE).join(df_sum.set_index(COM_JOINTURE), how='inner', on=COM_JOINTURE)
    df_sum = df_sum.reset_index()
    df_sum = df_sum.drop(columns=[COM_JOINTURE])
    df_sum = df_sum.groupby(by=comXX, dropna=False, as_index=False).sum()
    try:
        df_sum = pd.DataFrame(df_sum[[comXX] + tab_sum], columns=[comXX] + tab_sum)
    except KeyError:
        return json.dumps("err_jointure")

    # Max
    df_max = pd.DataFrame(df_import[[COM_JOINTURE] + tab_max], columns=[COM_JOINTURE] + tab_max)
    df_max = jointure_op.set_index(COM_JOINTURE).join(df_max.set_index(COM_JOINTURE), how='inner', on=COM_JOINTURE)
    df_max = df_max.reset_index()
    df_max = df_max.drop(columns=[COM_JOINTURE])
    df_max = df_max.groupby(by=comXX, dropna=False, as_index=False).max()
    df_max = pd.DataFrame(df_max[[comXX]+tab_max], columns=[comXX]+tab_max)

    # Min
    df_min = pd.DataFrame(df_import[[COM_JOINTURE] + tab_min], columns=[COM_JOINTURE] + tab_min)
    df_min = jointure_op.set_index(COM_JOINTURE).join(df_min.set_index(COM_JOINTURE), how='inner', on=COM_JOINTURE)
    df_min = df_min.reset_index()
    df_min = df_min.drop(columns=[COM_JOINTURE])
    df_min = df_min.groupby(by=comXX, dropna=False, as_index=False).min()
    df_min = pd.DataFrame(df_min[[comXX]+tab_min], columns=[comXX]+tab_min)

    # Fusion des différentes opérations
    df_op = pd.DataFrame
    # Sum & Max & Min
    if tab_sum and tab_max and tab_min:
        try:
            df_op = df_sum.set_index(comXX).join(df_max.set_index(comXX), how='inner',
                                                            on=comXX)
            df_op = df_op.join(df_min.set_index(comXX), how='inner', on=comXX)
            df_op = df_op.reset_index()
            print("DF_OP_SUM_MAX_MIN")
        except KeyError:
            return json.dumps("err_join_OP")
    # Sum & Max
    elif tab_sum and tab_max:
        try:
            df_op = df_sum.set_index(comXX).join(df_max.set_index(comXX), how='inner',
                                                            on=comXX)
            df_op = df_op.reset_index()
            print("DF_OP_SUM_MAX")
        except KeyError:
            return json.dumps("err_join_OP")
    elif tab_sum and tab_min:
        try:
            df_op = df_sum.set_index(comXX).join(df_min.set_index(comXX), how='inner',
                                                            on=comXX)
            df_op = df_op.reset_index()
            print("DF_OP_SUM_MIN")
        except KeyError:
            return json.dumps("err_join_OP")
    elif tab_max and tab_min:
        try:
            df_op = df_max.set_index(comXX).join(df_min.set_index(comXX), how='inner',
                                                            on=comXX)
            df_op = df_op.reset_index()
            print("DF_OP_SUM_MIN")
        except KeyError:
            return json.dumps("err_join_OP")
    elif tab_sum:
        df_op = df_sum
    elif tab_max:
        df_op = df_max
    elif tab_min:
        df_op = df_min

    ### Jointure des refs

    # On supprime COM_JOINTURE du df jointure
    jointure = jointure.drop(columns=[COM_JOINTURE])

    # Jointure sur com courant de df_op sur jointure
    df_res = jointure.set_index(comXX).join(df_op.set_index(comXX), how='inner',
                                                       on=comXX)

    # On enlève le com courant de l'index (il repasse en colonne)
    df_res = df_res.reset_index()

    # On supprime les données dupliquées à cause de la jointure
    df_res = df_res.drop_duplicates()

    # On remet les colonnes dans l'ordre initial
    df_res = pd.DataFrame(df_res[jointure.columns.tolist() + tab_ops], columns=jointure.columns.tolist() + tab_ops)

    # Ajout de commentaire
    if commentaire:
        df_res['Commentaire'] = ""
        df_res.loc[0, 'Commentaire'] = commentaire

    # Homogénéisation de l'écriture des colonnes
    df_res.columns = remove_specialchar(df_res.columns.tolist())

    return df_res.to_json()


def remove_specialchar(tab):
    clean_tab = []
    for title in tab:
        title = unidecode(title.lower()).replace(" ", "_")
        clean_tab.append(title)

    return clean_tab


# AJOUT D'UNE NOUVELLE TABLE DANS LA BASE DE DONNEES
def mise_en_base(table_name, dataframe):
    # Setup Connexion + definition du curseur
    conn = engine.connect()

    # Recuperation des types
    dataframe_types = df_to_sql(dataframe)

    try:
        dataframe.to_sql(table_name, conn, if_exists='fail', index=False, dtype=dataframe_types)
    except ValueError:
        # print("nom en double")
        print("Deja en base") # <--- C'est ici que ça retourne si c pas en base
        return 1
    except Exception as ex:
        print(ex)  # TODO : à remplacer par un feedback au front
    else:
        print('La mise en base a été réalisée avec succes ')
    finally:
        conn.close()
    return 0

# TODO : df_to_sql amélioration
# Fonction qui retourne le tableau de types postgres associé au tableau de type dataframe entré
def df_to_sql(dfparam):
    res = {}
    for i, j in zip(dfparam.columns, dfparam.dtypes):
        if "object" in str(j):
            res.update({i: sqla.types.TEXT})
        elif "int" in str(j):
            res.update({i: sqla.types.INT()})
    return res

def get_com(liste):
    return liste[0]

# Permet de créer une chaine pour requête sql à partir d'une liste
def list_to_str(liste):
    str = ""
    for i in range(len(liste)):
        if i == (len(liste) - 1):
            str = str + liste[i]
        else:
            str = str + liste[i] + ', '
    return str

# Permet de créer une chaine pour requête sql a partir d'une liste de données relative aux années
def list_with_year_to_str(liste, year):
    string = ""
    for i in range(len(liste)):
        if i == (len(liste) - 1):
            string = string + liste[i] + str(year)
        else:
            string = string + liste[i] + str(year) + ', '
    return string

# Permet de créer une liste de données relative à l'année 'year'
def list_with_year_to_list_with_choosen_year(liste, year):
    res = []
    for i in range(len(liste)):
        res.append(liste[i] + year)
    return res


# -------------------
# EXPORTER UN FICHIER
# -------------------
@app.route('/export', methods=['POST'])
def download_file():
    content = request.json  # Récupération du json envoyé par l'affichage
    db_name = content[-1][0]
    content.remove(content[-1])

    # Séparation des colonnes et du contenu du json
    try:
        columns = content[0]
        content.remove(content[0])

        # Création d'un dataframe à partir du contenu et des colonnes
        df_export = pd.DataFrame.from_records(content)
        df_export.columns = columns
    except IndexError:
        df_export = pd.DataFrame.from_records(content)

    mise_en_base(db_name, df_export)

    # Vide le dossier local de fichiers
    cleanTempDirectory()

    file_name = db_name + ".csv"

    # Conversion du dataframe en CSV et renvoie à l'affichage pour le téléchargement
    path = os.path.join(os.getcwd(), "temp")
    file_name_path = os.path.join(path, file_name)
    df_export.to_csv(file_name_path, sep=";", index=False)
    send_email(file_name_path)

    return send_file(file_name_path,
                     mimetype='text/csv',
                     attachment_filename=file_name,
                     as_attachment=True)


# Vide le dossier de fichier temporaires
def cleanTempDirectory():
    temp_path = os.path.join(os.getcwd(), "temp")  # récupération du chemin du dossier temp
    file_list = os.listdir(temp_path)  # liste les fichiers du dossier temp

    if len(file_list) > 5:
        for file in file_list:
            try:
                filepath = os.path.join(temp_path, file)  # récupération du chemin du fichier
                os.remove(filepath)  # suppression du fichier
            except PermissionError:
                pass


# ---------------------------
# ENVOI AUTOMATIQUE D'UN MAIL
# ---------------------------

def send_email(file_name):
    file_name_affichage = get_name_mail(file_name)
    msg = Message('Outil Agate - Traitement : ' + file_name_affichage, recipients=Config.MAIL_ADRESSES_DEST)
    msg.body = "Un nouveau traitement a été effectué !\nCi-joint le fichier exporté."
    with app.open_resource(file_name) as fp:
        msg.attach(file_name_affichage, "text/csv", fp.read())
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return render_template('index.html')

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

# Recupere le d'un fichier à partir de son chemin
def get_name(name):
    for ind_l in reversed(range(len(name) - 1)):
        if name[ind_l] == '\\':
            return name[ind_l + 1:len(name)]

def get_name_mail(name):
    res = None
    for ind_l in reversed(range(len(name) - 1)):
        if name[ind_l] == '\\':
            res =  name[ind_l + 1:len(name)]
            break

    if not res :
        for ind_l in reversed(range(len(name) - 1)):
            if name[ind_l] == '/':
                return name[ind_l + 1:len(name)]
    return res

# serveur
# if __name__ == "__main__":
# app.run(host='0.0.0.0',port=1060)
