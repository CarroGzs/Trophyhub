from flask import Blueprint, redirect, url_for, session, render_template, request, make_response
from app.models.achievementmodel import Achievement
from app.middlewares.authmiddlewares import login_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('auth.home'))
    return redirect(url_for('auth.login'))

@main_bp.route('/gamesList', methods=['GET'])
@login_required
def gamesList():
    meus_jogos = Achievement.get_by_user_grouped(session['user_id'])
    return render_template('gamesList.html', username=session.get('username'), meus_jogos=meus_jogos)

@main_bp.route('/toggle-theme', methods=['GET'])
def toggle_theme():
    current_theme = request.cookies.get('theme', 'dark')
    new_theme = 'light' if current_theme == 'dark' else 'dark'
    
    target_url = request.referrer or url_for('main.index')
    response = make_response(redirect(target_url))
    response.set_cookie('theme', new_theme, max_age=60*60*24*30)
    return response