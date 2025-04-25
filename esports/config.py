import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', "sqlite:///site.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
    DUO_IKEY = os.environ.get('DUO_IKEY')
    DUO_SKEY= os.environ.get('DUO_SKEY')
    DUO_HOST = os.environ.get('DUO_HOST')
    DUO_AKEY = os.environ.get('DUO_AKEY')
    FERNET_KEY = os.environ.get("FERNET_KEY")
    AD_SERVER = os.environ.get('AD_SERVER')
    AD_USER = os.environ.get('AD_USER')
    AD_PASS = os.environ.get('AD_PASS')
    ISE_USERNAME = os.environ.get('ISE_USERNAME')
    ISE_PASSWORD = os.environ.get('ISE_PASSWORD')
    ISE_BASE = os.environ.get('ISE_BASE')
    AD_BASE_DN = os.environ.get('AD_BASE_DN')
    AD_USER_DN_TEMPLATE = os.environ.get('AD_USER_DN_TEMPLATE')
    AD_GROUP_DN = os.environ.get('AD_GROUP_DN')

    # print (DUO_AKEY)