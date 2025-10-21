import os

# Pega o caminho absoluto do diretório onde o script está
basedir = os.path.abspath(os.path.dirname(__file__))

# Define o caminho para a pasta 'instance'
instance_dir = os.path.join(basedir, 'instance')
# Cria a pasta 'instance' se ela não existir
os.makedirs(instance_dir, exist_ok=True)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'uma-chave-secreta-muito-dificil'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    
    # Configure o número de WhatsApp para o checkout
    WHATSAPP_NUMBER = "5511981189800" 