class Config:
    # ----- Database ----- #
    DB_HOST = "127.0.0.1"
    DB_PORT = "5432"
    DB_NAME = "agate"
    DB_USER = "postgres"
    DB_PASS = "user"

    # Ne pas modifier
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://" + DB_USER + ":" + DB_PASS + "@" + DB_HOST + ":" + DB_PORT + "/" + DB_NAME
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ----- Import ----- #
    # Ne pas modifier
    UPLOAD_EXTENSIONS = ['.csv', '.xlsx', 'ods']
    UPLOAD_PATH = 'temp'

    # ----- Jointure ----- #
    # COM sur lequel est faite la jointure
    COM_JOINTURE = 'com14'
    # Champs récupéré dans v_passage qui dépendent d'une année
    CHAMPS_JOINTURE_DEPENDANT_ANNEE = ['com', 'libcom', 'cco', 'libcco']
    # Champs récupéré dans v_passage indépendant de l'année
    CHAMPS_JOINTURE = ['id_deleg', 'deleg', 'tcg18', 'libtcg18', 'alp', 'dep', 'libdep', 'reg', 'libreg']
    # Nom de la table contenant les informations relative au referentiel
    NOM_TABLE_REFGEO = 'v_passage'

    # ----- Mail ----- #
    MAIL_SERVER = 'smtp.office365.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False

    # Adresse utilisée par l'application lors de l'envoie de mail
    MAIL_USERNAME = 'traitement-geomatique@agate-territoires.fr'

    # Mot de passe de l'adresse mail
    MAIL_PASSWORD = 'Won06597'

    # Remplir avec ('Pseudonyme application', 'MAIL_USERNAME')
    MAIL_DEFAULT_SENDER = (
        'Outil Agate', 'traitement-geomatique@agate-territoires.fr')

    # Adresses
    MAIL_ADRESSES_DEST = ['geomatique@agate-territoires.fr']

    # Ne pas modifier
    MAIL_MAX_EMAILS = None
    MAIL_ASCII_ATTACHMENTS = True

    # Mot de passe administrateur
    ADMIN_PASSWORD = 'e10adc3949ba59abbe56e057f20f883e'  # Actuellement : 123456
