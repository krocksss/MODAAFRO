# forms.py

from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, BooleanField, 
    TextAreaField, FloatField, SelectField, MultipleFileField,
    URLField
)
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from flask_wtf.file import FileField, FileAllowed

# Nossas imagens serão salvas localmente
IMG_ALLOWED = ['jpg', 'jpeg', 'png', 'webp']

class LoginForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Login')

class CategoriaForm(FlaskForm):
    nome = StringField('Nome da Categoria', validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('Salvar Categoria')

class ProdutoForm(FlaskForm):
    nome = StringField('Nome do Produto', validators=[DataRequired(), Length(min=3, max=200)])
    descricao = TextAreaField('Descrição', validators=[Optional()])
    preco = FloatField('Preço', validators=[DataRequired(), NumberRange(min=0.01)])
    
    # Vamos carregar as categorias dinamicamente na rota
    categorias = SelectField('Categorias', coerce=int, validators=[DataRequired()])
    
    # Campo para novas imagens
    novas_imagens = MultipleFileField('Adicionar Imagens', 
                                    validators=[FileAllowed(IMG_ALLOWED, 'Apenas imagens!')])
    
    # O campo para selecionar a imagem de destaque será renderizado dinamicamente no HTML
    
    destaque = BooleanField('Marcar como Destaque')
    submit = SubmitField('Salvar Produto')


class SiteSettingsForm(FlaskForm):
    sobre_nos = TextAreaField('Sobre Nós', validators=[DataRequired()])
    texto_footer = StringField('Texto do Rodapé', validators=[DataRequired()])
    cor_fundo = StringField('Cor de Fundo (Hex)', validators=[Optional(), Length(max=7)])
    submit = SubmitField('Salvar Configurações')

class BannerForm(FlaskForm):
    imagem = FileField('Imagem do Banner (1200x300 recomendado)', 
                       validators=[FileAllowed(IMG_ALLOWED, 'Apenas imagens!')])
    
    # --- CAMPO NOVO ---
    # Este campo será populado dinamicamente na rota
    produto_selecionado = SelectField('...OU selecione um produto para lincar', 
                                    coerce=int, 
                                    validators=[Optional()], 
                                    default=0)
    
    # --- CAMPO ANTIGO (MODIFICADO) ---
    # Não é mais obrigatório, só é usado se um produto NÃO for selecionado
    link_url = URLField('Link Externo (Se não selecionar um produto. Ex: https://...)', 
                        validators=[Optional()])
    
    ordem = SelectField('Ordem', coerce=int, choices=[(i, str(i)) for i in range(1, 6)], default=1)
    submit = SubmitField('Adicionar Banner')