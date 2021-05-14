class Config:

    # ----- Database ----- #
    # Database
    DB_HOST = "127.0.0.1"
    DB_PORT = "5432"
    DB_NAME = "agate"
    DB_USER = "postgres"
    DB_PASS = "user"
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://" + DB_USER + ":" + DB_PASS + "@" + DB_HOST + ":" + DB_PORT + "/" + DB_NAME
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ----- Import ----- #

    UPLOAD_EXTENSIONS = ['.csv', '.xlsx', 'ods']
    UPLOAD_PATH = 'temp'

    # ----- Mail ----- #
    MAIL_SERVER = 'smtp.office365.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False

    MAIL_USERNAME = 'adressedetest73@outlook.fr' # 'traitement-geomatique@agate-territoires.fr'
    MAIL_PASSWORD = 'agate123' # 'Won06597'

    # Options pour le debug
    MAIL_DEBUG = True
    MAIL_SUPPRESS_SEND = False

    MAIL_DEFAULT_SENDER = ('Outil Agate', 'adressedetest73@outlook.fr') # ('Outil Agate', 'traitement-geomatique@agate-territoires.fr')
    MAIL_MAX_EMAILS = None
    MAIL_ASCII_ATTACHMENTS = True

    ADMIN_PASSWORD = '123456789b'