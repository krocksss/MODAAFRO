"# MODAAFRO" 
E-commerce Flask com Checkout via WhatsApp
Este é um projeto de e-commerce full-stack, construído em Python com o micro-framework Flask. Ele foi projetado para ser uma loja de roupas leve, com um painel de administração completo e um fluxo de checkout de cliente que finaliza o pedido diretamente em uma conversa do WhatsApp.

O frontend foi "upgradado" do CSS padrão para o Bootstrap 5, tornando-o totalmente responsivo e moderno, e utiliza o Swiper.js para um carrossel de banners dinâmico.

Recursos Principais
O projeto é dividido em duas áreas principais: a Loja do Cliente e o Painel de Administração.

1. Loja do Cliente (Frontend)
Design Responsivo: Utiliza Bootstrap 5 para se adaptar a desktops, tablets e dispositivos móveis.

Homepage Dinâmica: Apresenta um carrossel de banners (Swiper.js) e uma grade de "Produtos em Destaque" gerenciados pelo admin.

Página da Loja Completa (/loja):

Grid de todos os produtos cadastrados.

Sistema de Filtro por categorias.

Sistema de Pesquisa por nome ou descrição.

Página "Sobre Nós": Exibe informações institucionais cadastradas no painel de admin.

Modal de Produto: Ao clicar em um produto, um modal (pop-up) do Bootstrap é aberto com detalhes, múltiplas imagens e um botão "Adicionar ao Carrinho".

Carrinho de Compras Persistente: O carrinho é salvo no localStorage do navegador, permitindo que o cliente navegue pelo site sem perder seus itens.

Checkout via WhatsApp: Ao finalizar o pedido, o site gera uma mensagem de WhatsApp pré-formatada com todos os itens do pedido, subtotal e total, e a envia para o número de telefone do lojista.

2. Painel de Administração (Backend)
Autenticação Segura: Painel protegido em /admin com login e senha (usando Flask-Login).

Dashboard Central.

CRUD de Produtos:

Administradores podem Criar, Ler, Atualizar e Excluir produtos.

Upload de múltiplas imagens por produto.

Seleção de uma imagem de destaque.

Atribuição de uma categoria.

Marcação de "Produto em Destaque" para a homepage.

CRUD de Categorias:

Gerenciamento completo de categorias (Adicionar, Editar, Excluir).

O sistema impede a exclusão de categorias que já possuem produtos associados.

Customização do Site:

Atualização do texto da página "Sobre Nós".

Atualização do texto do rodapé.

Gerenciamento de Banners:

Upload de imagens para o carrossel da homepage.

Definição de ordem de exibição.

Link dinâmico: O admin pode lincar um banner a uma URL externa (ex: https://google.com) ou selecionar um produto cadastrado em um menu dropdown, fazendo o banner abrir o modal daquele produto.

Stack de Tecnologias
Backend
Python 3

Flask: Framework web.

Flask-SQLAlchemy: ORM para interação com o banco de dados.

Flask-Login: Gerenciamento de sessão de usuário (admin).

Flask-WTF: Criação e validação de formulários do painel admin.

Pillow: Processamento de uploads de imagem.

Banco de Dados
SQLite: Banco de dados simples baseado em arquivo, ideal para desenvolvimento e pequenos projetos.

Frontend
HTML5 / Jinja2: Motor de templates do Flask.

Bootstrap 5: Framework de CSS para design responsivo e componentes (modais, navbar, cards, grid).

JavaScript (ES6+): Lógica do cliente para o carrinho, API de produtos e interação com modais do Bootstrap.

Swiper.js: Biblioteca para o carrossel de banners.

localStorage: Armazenamento no navegador para o carrinho.

Estrutura do Projeto
/MODAAFRO/
|
|-- app.py             # App principal Flask (rotas, lógica de view)
|-- models.py          # Modelos do banco de dados (SQLAlchemy)
|-- forms.py           # Formulários do admin (Flask-WTF)
|-- config.py          # Configurações (Chave Secreta, DB URI, Nº WhatsApp)
|
|-- instance/
|   |-- site.db        # Arquivo do banco de dados SQLite
|
|-- static/
|   |-- css/
|   |   |-- style.css  # CSS customizado (ajustes do Bootstrap, Swiper)
|   |-- js/
|   |   |-- main.js    # Lógica do carrinho, modais e checkout (adaptado para Bootstrap)
|   |-- uploads/       # Pasta onde as imagens de produtos e banners são salvas
|
|-- templates/
    |-- layout_cliente.html  # Layout base do cliente (com Bootstrap e Navbar)
    |-- layout_admin.html    # Layout base do admin (CSS simples)
    |-- index.html           # Homepage (com Swiper.js)
    |-- loja.html            # Página da loja (com filtros e grid Bootstrap)
    |-- sobre.html           # Página "Sobre Nós"
    |
    |-- admin/
        |-- login.html
        |-- dashboard.html
        |-- gerenciar_categorias.html
        |-- gerenciar_produtos.html
        |-- gerenciar_site.html
        |-- form_categoria.html
        |-- form_produto.html
Como Executar o Projeto
1. Pré-requisitos
Python 3 instalado.

pip (gerenciador de pacotes do Python).

2. Instalação
Clone o repositório (ou certifique-se de ter todos os arquivos acima na pasta).

Crie um Ambiente Virtual (Recomendado):

Bash

python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
Instale as dependências:

Bash

pip install Flask Flask-SQLAlchemy Flask-Login Flask-WTF Pillow
Configure o WhatsApp:

Abra o arquivo config.py.

Altere o WHATSAPP_NUMBER para o número de telefone (com código do país) que deve receber os pedidos.

3. Inicialização
Crie o Banco de Dados:

No terminal, execute o comando Flask para criar as tabelas:

Bash

flask init-db
Crie o Usuário Administrador:

Execute o comando para criar o primeiro usuário admin:

Bash

flask create-admin
(O login padrão definido no código é usuario: admin, senha: admin123)

4. Execute a Aplicação
Inicie o servidor Flask:

Bash

flask run --debug
Acesse o site:

Loja: http://127.0.0.1:5000/

Painel Admin: http://127.0.0.1:5000/admin
