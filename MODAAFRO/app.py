# app.py

from flask import (
    Flask, render_template, request, redirect, url_for, 
    jsonify, flash, send_from_directory, abort
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, login_user, logout_user, login_required, current_user
)
from werkzeug.utils import secure_filename
import os
import uuid # Para nomes de arquivos únicos

# Importar de arquivos locais
from config import Config
from models import db, Admin, Categoria, Produto, ImagemProduto, SiteSettings, Banner
from forms import (
    LoginForm, ProdutoForm, CategoriaForm, SiteSettingsForm, BannerForm,
    IMG_ALLOWED
)


# --- Configuração Inicial ---

app = Flask(__name__)
app.config.from_object(Config)

# Cria a pasta de UPLOADS se não existir
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Inicializar DB e LoginManager
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_admin'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'error' # Categoria para flash message

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Admin, int(user_id))

# --- Funções Helper ---

def get_site_context():
    """Função helper para carregar dados globais do site."""
    categorias = Categoria.query.order_by(Categoria.nome).all()
    settings_db = SiteSettings.query.all()
    settings = {s.chave: s.valor for s in settings_db}
    settings.setdefault('whatsapp_number', app.config['WHATSAPP_NUMBER'])
    settings.setdefault('texto_footer', '© 2025 Sua Loja.')
    settings.setdefault('sobre_nos', 'Bem-vindo à nossa loja.')
    return {
        "categorias": categorias,
        "settings": settings
    }

def save_image(file_storage):
    """Salva um arquivo de imagem e retorna seu nome único."""
    if not file_storage or file_storage.filename == '':
        return None
    
    # Pega a extensão
    ext = file_storage.filename.rsplit('.', 1)[1].lower()
    if ext not in IMG_ALLOWED:
        return None # Ou lançar um erro
        
    # Cria um nome de arquivo único
    filename = secure_filename(f"{uuid.uuid4().hex}.{ext}")
    
    # Salva o arquivo
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file_storage.save(file_path)
    
    return filename # Retorna apenas o nome do arquivo (ex: 'abc123def.jpg')

def delete_image(filename):
    """Exclui um arquivo de imagem da pasta de uploads."""
    if not filename:
        return
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Erro ao excluir imagem {filename}: {e}") # Logar o erro


# --- Comandos CLI (Já existentes) ---
@app.cli.command("init-db")
def init_db_command():
    """Cria as tabelas do banco de dados."""
    with app.app_context():
        db.create_all()
        print("Banco de dados inicializado.")

@app.cli.command("create-admin")
def create_admin_command():
    """Cria o usuário administrador inicial."""
    with app.app_context():
        if Admin.query.filter_by(username='admin').first():
            print("Usuário 'admin' já existe.")
            return
        
        admin_user = Admin(username='admin')
        admin_user.set_password('admin123') # Mude isso para uma senha segura!
        db.session.add(admin_user)
        
        # Adiciona configurações iniciais
        db.session.add(SiteSettings(chave='cor_fundo', valor='#FFFFFF'))
        db.session.add(SiteSettings(chave='texto_footer', valor='© 2025 Sua Loja. Todos os direitos reservados.'))
        db.session.add(SiteSettings(chave='sobre_nos', valor='Escreva aqui sobre sua loja.'))

        db.session.commit()
        print("Usuário 'admin' criado com senha 'admin123'.")


# --- Rotas do Cliente (Públicas) ---

@app.route('/')
def index():
    """Página Inicial (Homepage)"""
    context = get_site_context()
    banners = Banner.query.order_by(Banner.ordem).all()
    produtos_destaque = Produto.query.filter_by(destaque=True).limit(8).all()
    
    return render_template('index.html', 
                           **context, 
                           banners=banners, 
                           produtos=produtos_destaque)
@app.route('/sobre')
def sobre():
    """Página Sobre Nós"""
    context = get_site_context() # Pega as configs (incluindo 'sobre_nos')
    return render_template('sobre.html', **context)

@app.route('/produto/<int:produto_id>')
def get_produto_data(produto_id):
    """API para buscar dados do produto."""
    produto = db.session.get(Produto, produto_id)
    if not produto:
        return jsonify({"error": "Produto não encontrado"}), 404

    produto_data = {
        "id": produto.id,
        "nome": produto.nome,
        "descricao": produto.descricao,
        "preco": f"{produto.preco:.2f}",
        "imagem_destaque": url_for('uploaded_file', filename=produto.imagem_destaque_url) if produto.imagem_destaque_url else None,
        "imagens": [url_for('uploaded_file', filename=img.url_imagem) for img in produto.imagens]
    }
    return jsonify(produto_data)
@app.route('/loja')
def loja():
    """Página da Loja, com filtro e pesquisa."""
    context = get_site_context()
    
    # Pega os parâmetros da URL (ex: /loja?q=camiseta&categoria=1)
    query_pesquisa = request.args.get('q')
    query_categoria = request.args.get('categoria_id')

    # Começa com uma query base para todos os produtos
    query_produtos = Produto.query.order_by(Produto.nome)
    
    categoria_selecionada = None

    # 1. Filtro por Categoria
    if query_categoria:
        try:
            categoria_id = int(query_categoria)
            categoria_selecionada = db.session.get(Categoria, categoria_id)
            if categoria_selecionada:
                # Filtra produtos que ESTÃO ('any') na categoria selecionada
                query_produtos = query_produtos.filter(Produto.categorias.any(id=categoria_id))
            else:
                flash("Categoria não encontrada.") # Opcional
        except ValueError:
            pass # Ignora se o ID da categoria não for um número

    # 2. Filtro por Pesquisa (Query)
    if query_pesquisa:
        # 'ilike' é case-insensitive (ignora maiúsculas/minúsculas)
        search_term = f"%{query_pesquisa}%"
        query_produtos = query_produtos.filter(
            db.or_(
                Produto.nome.ilike(search_term),
                Produto.descricao.ilike(search_term)
            )
        )

    # Finalmente, executa a query
    produtos_encontrados = query_produtos.all()

    return render_template('loja.html',
                           **context,
                           produtos=produtos_encontrados,
                           categoria_selecionada=categoria_selecionada,
                           query_pesquisa=query_pesquisa)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve os arquivos de upload."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# --- Rotas do Admin (Protegidas) ---

@app.route('/admin/login', methods=['GET', 'POST'])
def login_admin():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard_admin'))
    
    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin and admin.check_password(form.password.data):
            login_user(admin)
            return redirect(url_for('dashboard_admin'))
        else:
            flash('Usuário ou senha inválidos.', 'error')
            
    return render_template('admin/login.html', form=form)

@app.route('/admin/logout')
@login_required
def logout_admin():
    logout_user()
    return redirect(url_for('login_admin'))

@app.route('/admin/dashboard')
@login_required
def dashboard_admin():
    return render_template('admin/dashboard.html')

# --- CRUD de Produtos ---

@app.route('/admin/produtos')
@login_required
def gerenciar_produtos():
    produtos = Produto.query.order_by(Produto.id.desc()).all()
    categorias = Categoria.query.all()
    return render_template('admin/gerenciar_produtos.html', produtos=produtos, categorias=categorias)


@app.route('/admin/categorias', methods=['GET', 'POST'])
@login_required
def gerenciar_categorias():
    """Página para Listar e Adicionar novas categorias."""
    form = CategoriaForm()
    
    # Lógica para ADICIONAR nova categoria
    if form.validate_on_submit():
        # Verifica se a categoria já existe (para evitar duplicatas)
        nome_categoria = form.nome.data
        existente = Categoria.query.filter(db.func.lower(Categoria.nome) == db.func.lower(nome_categoria)).first()
        
        if existente:
            flash('Uma categoria com este nome já existe.', 'error')
        else:
            nova_categoria = Categoria(nome=nome_categoria)
            db.session.add(nova_categoria)
            db.session.commit()
            flash('Categoria adicionada com sucesso!', 'success')
        
        # Redireciona para a mesma página (limpando o formulário)
        return redirect(url_for('gerenciar_categorias'))

    # Lógica para LER (GET)
    categorias = Categoria.query.order_by(Categoria.nome).all()
    return render_template('admin/gerenciar_categorias.html', form=form, categorias=categorias)


@app.route('/admin/categoria/editar/<int:categoria_id>', methods=['GET', 'POST'])
@login_required
def edit_categoria(categoria_id):
    """Página para EDITAR uma categoria."""
    categoria = db.session.get(Categoria, categoria_id) or abort(404)
    form = CategoriaForm(obj=categoria) # Preenche o form com dados existentes

    if form.validate_on_submit():
        nome_categoria = form.nome.data
        # Verifica se o novo nome já existe em OUTRA categoria
        existente = Categoria.query.filter(
            db.func.lower(Categoria.nome) == db.func.lower(nome_categoria),
            Categoria.id != categoria_id
        ).first()
        
        if existente:
            flash('Já existe outra categoria com este nome.', 'error')
        else:
            categoria.nome = nome_categoria
            db.session.commit()
            flash('Categoria atualizada com sucesso!', 'success')
            return redirect(url_for('gerenciar_categorias'))

    return render_template('admin/form_categoria.html', form=form, categoria=categoria)


@app.route('/admin/categoria/excluir/<int:categoria_id>')
@login_required
def delete_categoria(categoria_id):
    """Rota para EXCLUIR uma categoria."""
    categoria = db.session.get(Categoria, categoria_id) or abort(404)
    
    # IMPORTANTE: Verificação de segurança
    # 'categoria.produtos' usa o backref que definimos no models.py
    if categoria.produtos:
        flash('Não é possível excluir esta categoria, pois ela está associada a produtos.', 'error')
    else:
        db.session.delete(categoria)
        db.session.commit()
        flash('Categoria excluída com sucesso!', 'success')
        
    return redirect(url_for('gerenciar_categorias'))

@app.route('/admin/produto/novo', methods=['GET', 'POST'])
@login_required
def add_produto():
    form = ProdutoForm()
    # Popula o 'SelectField' de categorias com dados do DB
    form.categorias.choices = [(c.id, c.nome) for c in Categoria.query.order_by(Categoria.nome).all()]
    
    if form.validate_on_submit():
        # 1. Cria o produto
        novo_produto = Produto(
            nome=form.nome.data,
            descricao=form.descricao.data,
            preco=form.preco.data,
            destaque=form.destaque.data
        )
        
        # 2. Associa a categoria
        categoria = db.session.get(Categoria, form.categorias.data)
        if categoria:
            novo_produto.categorias.append(categoria)
            
        db.session.add(novo_produto)
        db.session.commit() # Commit para ter o ID do produto
        
        # 3. Salva as imagens
        primeira_imagem_url = None
        for img_file in form.novas_imagens.data:
            filename = save_image(img_file)
            if filename:
                nova_imagem = ImagemProduto(url_imagem=filename, produto_id=novo_produto.id)
                db.session.add(nova_imagem)
                if not primeira_imagem_url:
                    primeira_imagem_url = filename
        
        # 4. Define a primeira imagem como destaque
        if primeira_imagem_url:
            novo_produto.imagem_destaque_url = primeira_imagem_url
            
        db.session.commit()
        flash('Produto adicionado com sucesso!', 'success')
        return redirect(url_for('gerenciar_produtos'))

    return render_template('admin/form_produto.html', form=form, produto=None)


@app.route('/admin/produto/editar/<int:produto_id>', methods=['GET', 'POST'])
@login_required
def edit_produto(produto_id):
    produto = db.session.get(Produto, produto_id) or abort(404)
    form = ProdutoForm(obj=produto) # Carrega dados do produto no form
    
    # Popula o 'SelectField' de categorias
    form.categorias.choices = [(c.id, c.nome) for c in Categoria.query.order_by(Categoria.nome).all()]
    
    if request.method == 'GET':
        # Pré-seleciona a categoria atual do produto
        if produto.categorias:
            form.categorias.data = produto.categorias[0].id
            
    if form.validate_on_submit():
        # 1. Atualiza dados básicos
        produto.nome = form.nome.data
        produto.descricao = form.descricao.data
        produto.preco = form.preco.data
        produto.destaque = form.destaque.data
        
        # 2. Atualiza categoria
        categoria = db.session.get(Categoria, form.categorias.data)
        produto.categorias = [categoria] # Simples, assume 1 categoria
        
        # 3. Exclui imagens marcadas
        ids_para_excluir = request.form.getlist('excluir_imagem')
        if ids_para_excluir:
            for img_id in ids_para_excluir:
                img = db.session.get(ImagemProduto, int(img_id))
                if img and img.produto_id == produto.id:
                    # Se a imagem a excluir era o destaque, limpa o destaque
                    if produto.imagem_destaque_url == img.url_imagem:
                        produto.imagem_destaque_url = None
                    delete_image(img.url_imagem) # Exclui arquivo
                    db.session.delete(img) # Exclui do DB
        
        # 4. Adiciona novas imagens
        novas_urls = []
        for img_file in form.novas_imagens.data:
            filename = save_image(img_file)
            if filename:
                nova_imagem = ImagemProduto(url_imagem=filename, produto_id=produto.id)
                db.session.add(nova_imagem)
                novas_urls.append(filename)
        
        # 5. Atualiza imagem de destaque
        destaque_selecionada = request.form.get('imagem_destaque')
        if destaque_selecionada:
            produto.imagem_destaque_url = destaque_selecionada
        elif not produto.imagem_destaque_url:
            # Se não tinha destaque (ou foi excluída), 
            # pega a primeira imagem nova ou a primeira que sobrou
            if novas_urls:
                produto.imagem_destaque_url = novas_urls[0]
            elif produto.imagens: # Cuidado, 'produto.imagens' pode conter imagens marcadas para exclusão
                img_restante = db.session.scalars(
                    db.select(ImagemProduto).filter_by(produto_id=produto.id).limit(1)
                ).first()
                if img_restante:
                    produto.imagem_destaque_url = img_restante.url_imagem

        db.session.commit()
        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('gerenciar_produtos'))

    return render_template('admin/form_produto.html', form=form, produto=produto)


@app.route('/admin/produto/excluir/<int:produto_id>', methods=['GET', 'POST']) # GET para link simples
@login_required
def delete_produto(produto_id):
    produto = db.session.get(Produto, produto_id) or abort(404)
    
    # Excluir todas as imagens associadas
    for img in produto.imagens:
        delete_image(img.url_imagem)
        # O DB excluirá via 'cascade'
        
    db.session.delete(produto)
    db.session.commit()
    
    flash('Produto excluído com sucesso!', 'success')
    return redirect(url_for('gerenciar_produtos'))


# --- CRUD de Site (Settings, Banners) e Categorias ---

@app.route('/admin/site', methods=['GET', 'POST'])
@login_required
def gerenciar_site():
    # Instancia os dois formulários
    settings_form = SiteSettingsForm()
    banner_form = BannerForm()
    
    # --- INÍCIO DA MUDANÇA ---
    # Precisamos carregar a lista de produtos para o dropdown do banner_form
    # Criamos uma lista de tuplas (id, nome)
    # O '0' é a opção "Nenhum"
    produto_choices = [(0, '--- Nenhum ---')] + \
                      [(p.id, f"ID {p.id} - {p.nome}") for p in Produto.query.order_by(Produto.nome).all()]
    banner_form.produto_selecionado.choices = produto_choices
    # --- FIM DA MUDANÇA ---

    # Lógica para o formulário de Configurações (sem alteração)
    if settings_form.validate_on_submit() and 'sobre_nos' in request.form:
        sobre = SiteSettings.query.filter_by(chave='sobre_nos').first() or SiteSettings(chave='sobre_nos')
        footer = SiteSettings.query.filter_by(chave='texto_footer').first() or SiteSettings(chave='texto_footer')
        
        # Atualiza os valores
        sobre.valor = settings_form.sobre_nos.data
        footer.valor = settings_form.texto_footer.data
        
        # Adiciona à sessão (necessário se forem novos)
        db.session.add_all([sobre, footer])
        db.session.commit()
        flash('Configurações do site salvas!', 'success')
        return redirect(url_for('gerenciar_site'))

    # Carrega os dados atuais nas configurações (sem alteração)
    if request.method == 'GET':
        context = get_site_context()
        settings_form.sobre_nos.data = context['settings'].get('sobre_nos')
        settings_form.texto_footer.data = context['settings'].get('texto_footer')

    # Carrega banners existentes (sem alteração)
    banners = Banner.query.order_by(Banner.ordem).all()

    return render_template('admin/gerenciar_site.html', 
                           settings_form=settings_form, 
                           banner_form=banner_form,
                           banners=banners)

@app.route('/admin/banner/novo', methods=['POST'])
@login_required
def add_banner():
    # Esta rota só aceita POST e é chamada pelo 'gerenciar_site'
    banner_form = BannerForm()
    
    # --- INÍCIO DA MUDANÇA ---
    # Precisamos popular as choices de novo, caso a validação falhe e 
    # a página 'gerenciar_site' precise ser re-renderizada com erros
    produto_choices = [(0, '--- Nenhum ---')] + \
                      [(p.id, f"ID {p.id} - {p.nome}") for p in Produto.query.order_by(Produto.nome).all()]
    banner_form.produto_selecionado.choices = produto_choices
    # --- FIM DA MUDANÇA ---
    
    if banner_form.validate_on_submit():
        filename = save_image(banner_form.imagem.data)
        if filename:
            
            # --- INÍCIO DA LÓGICA DO LINK ---
            produto_id_selecionado = banner_form.produto_selecionado.data
            link_manual = banner_form.link_url.data or None
            final_link = None
            
            if produto_id_selecionado and produto_id_selecionado > 0:
                # Se o admin escolheu um produto, criamos um "link especial"
                # que o nosso JavaScript vai entender.
                final_link = f"#product-modal-trigger-{produto_id_selecionado}"
            elif link_manual:
                # Senão, usamos o link manual (externo)
                final_link = link_manual
            # Se ambos estiverem vazios, final_link será None (sem link)
            # --- FIM DA LÓGICA DO LINK ---

            novo_banner = Banner(
                imagem_url=filename,
                link_url=final_link, # Usamos o link final decidido
                ordem=banner_form.ordem.data
            )
            db.session.add(novo_banner)
            db.session.commit()
            flash('Banner adicionado!', 'success')
        else:
            flash('Erro ao salvar imagem do banner. Verifique se enviou um arquivo.', 'error')
            
    # Redireciona de volta para a página de gerenciamento
    # (Se a validação falhar, o Flask-WTF vai lidar com isso 
    #  e re-renderizar 'gerenciar_site' com os erros)
    return redirect(url_for('gerenciar_site'))

@app.route('/admin/banner/excluir/<int:banner_id>')
@login_required
def delete_banner(banner_id):
    banner = db.session.get(Banner, banner_id) or abort(404)
    
    delete_image(banner.imagem_url)
    db.session.delete(banner)
    db.session.commit()
    
    flash('Banner excluído!', 'success')
    return redirect(url_for('gerenciar_site'))

# (Você pode adicionar o CRUD de Categorias seguindo o mesmo padrão)


# --- Execução ---
if __name__ == '__main__':
    app.run(debug=True)