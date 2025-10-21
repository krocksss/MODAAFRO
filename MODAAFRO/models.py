from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

db = SQLAlchemy()

# --- Modelos de Autenticação ---

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# --- Modelos da Loja ---

# Tabela de associação para Categoria <-> Produto (Muitos para Muitos)
produto_categoria = db.Table('produto_categoria',
    db.Column('produto_id', db.Integer, db.ForeignKey('produto.id'), primary_key=True),
    db.Column('categoria_id', db.Integer, db.ForeignKey('categoria.id'), primary_key=True)
)

class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    preco = db.Column(db.Float, nullable=False)
    destaque = db.Column(db.Boolean, default=False) # Para "produtos em destaque"
    
    # Relacionamento (Muitos para Muitos)
    categorias = db.relationship('Categoria', secondary=produto_categoria,
                                 lazy='subquery', backref=db.backref('produtos', lazy=True))
    
    # Relacionamento (Um para Muitos)
    imagens = db.relationship('ImagemProduto', backref='produto', lazy=True, cascade="all, delete-orphan")
    
    # Armazena o path da imagem de destaque
    imagem_destaque_url = db.Column(db.String(300))

class ImagemProduto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url_imagem = db.Column(db.String(300), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)

# --- Modelos de Customização do Site ---

class SiteSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Chave/Valor para guardar qualquer configuração
    # Ex: 'cor_fundo', 'texto_footer', 'sobre_nos'
    chave = db.Column(db.String(100), unique=True)
    valor = db.Column(db.Text)

class Banner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    imagem_url = db.Column(db.String(300), nullable=False)
    link_url = db.Column(db.String(300)) # Link para produto ou URL externa
    ordem = db.Column(db.Integer)