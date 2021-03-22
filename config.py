class Config:

    # ----- Database ----- #
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://postgres:user@127.0.0.1:5432/agate"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ----- Import ----- #
    ## app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024   //taille ficher 4MB
    UPLOAD_EXTENSIONS = ['.csv', '.xlsx', 'ods']
    UPLOAD_PATH = 'temp'

    # ----- Mail ----- #
    MAIL_SERVER = 'smtp.office365.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False

    MAIL_USERNAME = 'adressedetest73@outlook.fr'  # traitement-geomatique@agate-territoires.fr
    MAIL_PASSWORD = 'motdepasse73' # Won06597

    # Options pour le debug
    MAIL_DEBUG = True
    MAIL_SUPPRESS_SEND = False

    MAIL_DEFAULT_SENDER = ('Outil Agate', 'adressedetest73@outlook.fr')
    MAIL_MAX_EMAILS = None
    MAIL_ASCII_ATTACHMENTS = True