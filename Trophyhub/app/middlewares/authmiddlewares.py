from functools import wraps
from flask import session, redirect, url_for, flash, g
from app.models.usermodel import User

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        
        if not user_id:
            flash('Você precisa fazer login para acessar esta página.', 'warning')
            return redirect(url_for('auth.login'))
            
        user = User.get_by_id(user_id)
        if not user:
            session.clear()
            flash('Sessão inválida. Faça login novamente.', 'danger')
            return redirect(url_for('auth.login'))
            
        g.usuario = user
        return f(*args, **kwargs)
        
    return decorated_function