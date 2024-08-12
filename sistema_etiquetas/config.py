import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'sua_chave_secreta_aqui'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://danielmtavares:Dnr71830@mysql.danielmtavares.com.br:3306/danielmtavares'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    POSTGRES_URI = 'postgresql://daniel_tavares_usr:N$3CU=N"r<LYS:pA9}@rds-ecommerce.solfacil.com.br:5432/logistica_prd'