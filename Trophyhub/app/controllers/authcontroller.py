import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from app.models.usermodel import User
from app.models.gamemodel import Game
from app.models.achievementmodel import Achievement
from app.middlewares.authmiddlewares import login_required

auth_bp = Blueprint('auth', __name__, template_folder='../views')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('auth.home'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not username or not email or not password:
            flash('Preencha todos os campos para se cadastrar.', 'warning')
            return render_template('register.html')

        if len(username) < 3 or len(username) > 30:
            flash('O nome de usuário deve ter entre 3 e 30 caracteres.', 'warning')
            return render_template('register.html')

        if len(password) < 3 or len(password) > 50:
            flash('A senha deve ter entre 3 e 50 caracteres.', 'warning')
            return render_template('register.html')

        if password != confirm_password:
            flash('As senhas digitadas não coincidem.', 'danger')
            return render_template('register.html')

        if User.get_by_username(username):
            flash('Este nome de usuário já está cadastrado.', 'danger')
            return render_template('register.html')

        if User.get_by_email(email):
            flash('Este e-mail já está associado a outra conta.', 'danger')
            return render_template('register.html')

        try:
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            new_user.save()

            current_app.logger.info(f"Novo usuário cadastrado: '{username}'.")
            flash('Conta criada com sucesso! Faça seu login.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            current_app.logger.error(f"Erro ao cadastrar usuário '{username}': {e}")
            flash('Ocorreu um erro interno ao criar a conta. Tente novamente.', 'danger')

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('auth.home'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.get_by_username(username)

        if user and user.verify_password(password):
            session.clear()
            session['user_id'] = user.id
            session['username'] = user.username
            
            current_app.logger.info(f"Usuário '{user.username}' realizou login com sucesso.")
            flash(f'Bem-vindo de volta, {user.username}!', 'success')
            return redirect(url_for('auth.home'))
        else:
            current_app.logger.warning(f"Tentativa de login inválida para o usuário '{username}'.")
            flash('Usuário ou senha incorretos.', 'danger')
            return render_template('login.html')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    username = session.get('username')
    session.clear()
    current_app.logger.info(f"Usuário '{username}' encerrou a sessão (logout).")
    flash('Você encerrou sua sessão com sucesso.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/newgame', methods=['GET', 'POST'])
@login_required
def newgame():
    if session.get('username') != 'admin':
        current_app.logger.warning(f"Acesso negado à criação de jogo para o usuário '{session.get('username')}'.")
        flash('Acesso restrito apenas ao administrador.', 'danger')
        return redirect(url_for('auth.home'))

    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        genero = request.form.get('genero', '').strip()
        conquistas_raw = request.form.get('conquistas', '').strip()

        if not nome or not genero or not conquistas_raw:
            flash('Preencha todos os campos para cadastrar o jogo.', 'warning')
            return render_template('newgame.html')

        if len(nome) > 80 or len(genero) > 40:
            flash('O nome do jogo (máx. 80) ou gênero (máx. 40) ultrapassou o limite de caracteres.', 'warning')
            return render_template('newgame.html')

        conquistas = [c.strip() for c in conquistas_raw.split(',') if c.strip()]
        try:
            Game.create(nome, genero, conquistas, session['user_id'])
            current_app.logger.info(f"Admin cadastrou o jogo '{nome}' ({genero}).")
        except sqlite3.IntegrityError:
            flash('Já existe um jogo com esse nome.', 'warning')
            return render_template('newgame.html')

        flash('Jogo cadastrado com sucesso pelo Admin!', 'success')
        return redirect(url_for('auth.home'))

    return render_template('newgame.html')

@auth_bp.route('/game/<int:game_id>/delete', methods=['POST'])
@login_required
def delete_game(game_id):
    if session.get('username') != 'admin':
        current_app.logger.warning(f"Tentativa não autorizada de excluir jogo ID {game_id} por '{session.get('username')}'.")
        flash('Acesso restrito apenas ao administrador.', 'danger')
        return redirect(url_for('auth.home'))

    Game.delete(game_id, session['user_id'])
    current_app.logger.info(f"Admin excluiu o jogo ID {game_id}.")
    flash('Jogo removido com sucesso!', 'info')
    return redirect(url_for('auth.home'))

@auth_bp.route('/game/<int:game_id>/achievement', methods=['GET', 'POST'])
@login_required
def new_achievement(game_id):
    if session.get('username') != 'admin':
        flash('Acesso restrito apenas ao administrador.', 'danger')
        return redirect(url_for('auth.home'))

    game = Game.get_by_id(game_id, session['user_id'])
    if not game:
        flash('Jogo não encontrado.', 'danger')
        return redirect(url_for('auth.home'))

    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        descricao = request.form.get('descricao', '').strip()

        if not nome:
            flash('Informe o nome da conquista.', 'warning')
            return render_template('new_achievement.html', game=game)

        if len(nome) > 80 or len(descricao) > 200:
            flash('O nome (máx. 80) ou descrição (máx. 200) da conquista é muito longo.', 'warning')
            return render_template('new_achievement.html', game=game)

        Achievement.create(nome, descricao, game_id, session['user_id'])
        Game.add_conquista_nome(game_id, nome, session['user_id'])

        current_app.logger.info(f"Admin adicionou a conquista '{nome}' ao jogo '{game.nome}'.")
        flash(f'Conquista "{nome}" adicionada ao jogo {game.nome} pelo Admin!', 'success')
        return redirect(url_for('auth.home'))

    return render_template('new_achievement.html', game=game)

@auth_bp.route('/game/<int:game_id>/claim_achievement', methods=['POST'])
@login_required
def claim_achievement(game_id):

    game = Game.get_by_id_global(game_id)
    if not game:
        current_app.logger.warning(f"Tentativa de resgate em jogo inexistente (ID {game_id}) por '{session.get('username')}'.")
        flash('Jogo não encontrado no catálogo.', 'danger')
        return redirect(url_for('auth.home'))

    nome_conquista = request.form.get('nome_conquista', '').strip()
    if not nome_conquista or nome_conquista not in game.conquistas:
        flash('Conquista inválida para este jogo.', 'warning')
        return redirect(url_for('auth.home'))


    if Achievement.user_has_achievement(session['user_id'], game_id, nome_conquista):
        flash(f'Você já possui a conquista "{nome_conquista}" na sua conta!', 'warning')
        return redirect(url_for('main.gamesList'))

    descricao = Achievement.get_descricao_by_game_and_nome(game_id, nome_conquista)
    Achievement.create(nome_conquista, descricao, game_id, session['user_id'])
    current_app.logger.info(f"Jogador '{session.get('username')}' resgatou a conquista '{nome_conquista}' (Jogo ID {game_id}).")
    flash(f'Conquista "{nome_conquista}" adicionada ao seu perfil!', 'success')
        
    return redirect(url_for('main.gamesList'))

@auth_bp.route('/achievement/<int:achievement_id>/delete', methods=['POST'])
@login_required
def delete_achievement(achievement_id):
    Achievement.delete(achievement_id, session['user_id'])
    current_app.logger.info(f"Usuário '{session.get('username')}' removeu a conquista ID {achievement_id}.")
    flash('Conquista removida com sucesso!', 'info')
    return redirect(url_for('main.gamesList'))

@auth_bp.route('/home')
@login_required
def home():
    busca = request.args.get('q', '').strip()
    if busca:
        listaGames = Game.search_games(busca)
    else:
        listaGames = Game.get_all_games()
        
    return render_template('home.html', username=session.get('username'), listaGames=listaGames, busca=busca)

@auth_bp.route('/game/<int:game_id>/remove_achievement', methods=['POST'])
@login_required
def admin_remove_achievement(game_id):
    if session.get('username') != 'admin':
        flash('Acesso restrito apenas ao administrador.', 'danger')
        return redirect(url_for('auth.home'))

    nome_conquista = request.form.get('nome_conquista', '').strip()
    if nome_conquista:
        Game.remove_conquista_nome(game_id, nome_conquista)
        current_app.logger.info(f"Admin removeu a conquista '{nome_conquista}' do jogo ID {game_id}.")
        flash(f'Conquista "{nome_conquista}" removida do jogo!', 'info')

    return redirect(url_for('auth.home'))