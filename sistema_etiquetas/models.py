from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class DadosEtiqueta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    etiqueta = db.Column(db.String(50), unique=True, nullable=False)
    filial = db.Column(db.String(50))
    pedido_protheus = db.Column(db.String(50))
    pedido_web = db.Column(db.String(50))
    nota_fiscal = db.Column(db.String(50))
    valor_nota_fiscal = db.Column(db.Float)
    chave_nota_fiscal = db.Column(db.String(100))
    total_volumes = db.Column(db.Integer)
    transportadora = db.Column(db.String(100))
    fotos = db.Column(db.Text)
    videos = db.Column(db.Text)