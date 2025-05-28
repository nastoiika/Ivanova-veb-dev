from flask import Blueprint, request,  render_template, abort, request, make_response, session, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required

import mysql.connector as connector

from .repositories.user_repository import UserRepository
from .repositories.role_repository import RoleRepository
from .check_pass_and_login import check_password, check_login
from functools import wraps
from app import db

login_manager = LoginManager()
login_manager.login_view = 'users.index'
login_manager.login_message = 'Необходимо авторизоваться'
login_manager.login_message_category = 'warning'


user_repository = UserRepository(db)
role_repository = RoleRepository(db)

bp = Blueprint('users', __name__, url_prefix='/users')
@bp.errorhandler(connector.errors.DatabaseError)
def handler():
    pass

def check_rights(allow_self=False, user_id_param=None, admin_only=False):
    def decorator(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Вы не авторизованы", "danger")
                return redirect(url_for("auth.login"))

            if current_user.is_admin():
                return view(*args, **kwargs)

            if admin_only:
                flash("У вас недостаточно прав для доступа к данной странице.", "danger")
                return redirect(url_for("index"))

            if allow_self and user_id_param:
                target_user_id = kwargs.get(user_id_param)
                if int(current_user.id) == int(target_user_id):
                    return view(*args, **kwargs)

            flash("У вас недостаточно прав для доступа к данной странице.", "danger")
            return redirect(url_for("index"))
        return wrapped_view
    return decorator

@bp.route('/')
def index():
    return render_template('users/index.html', users=user_repository.all())

@bp.route('/<int:user_id>')
@check_rights(allow_self=True, user_id_param='user_id')
def show(user_id):
    user = user_repository.get_by_id(user_id)
    if user is None:
        flash('Пользователя нет в базе даных', 'danger')
        return redirect(url_for('users.index'))
    user_role = role_repository.get_by_id(user['role_id'])
    return render_template('users/show.html', user_data=user, user_role=user_role['name'] if user_role else '')


@bp.route('/new', methods = ['POST', 'GET'])
@login_required
@check_rights(admin_only=True)
def new():
    user_data = {}
    if request.method == 'POST':
        fields = ('username', 'password', 'first_name', 'middle_name', 'last_name', 'role_id')
        user_data = {field: request.form.get(field) or None for field in fields}
        if check_password(user_data['password']) and check_login(user_data['username']):
            try:
                user_repository.create(**user_data)
                flash("Учетная запись создана", 'success')
                return redirect(url_for('users.index'))
            except connector.errors.DatabaseError:
                flash('Произошла ошибка при созданиии записи', 'error')
                db.connect().rollback()
        else:
            flash('Введен недопустимый логин или пароль', 'error')
            user_data['username'] = ''
            user_data['password'] = ''

    return render_template('users/new.html', user_data=user_data, roles=role_repository.all())
    
@bp.route('/<int:user_id>/delete', methods = ['POST'])
@login_required
@check_rights(admin_only=True)
def delete(user_id):
    user_repository.delete(user_id)
    flash('Учетная запись удалена', 'success')
    return redirect(url_for('users.index'))

@bp.route('/<int:user_id>/edit', methods = ['POST', 'GET'])
@login_required
@check_rights(allow_self=True, user_id_param='user_id')
def edit(user_id):
    user = user_repository.get_by_id(user_id)
    if user is None:
        flash('Пользователя нет в базе даных', 'danger')
        return redirect(url_for('users.index'))

    if request.method == 'POST':
        fields = ('first_name', 'middle_name', 'last_name', 'role_id')
        user_data = {field: request.form.get(field) or None for field in fields}
        user_data["user_id"] = user_id
        try:
            user_repository.update(**user_data)
            flash("Учетная запись изменена", 'success')
            return redirect(url_for('users.index'))
        except connector.errors.DatabaseError:
            flash('Произошла ошибка при изменении записи', 'danger') 
            db.connect().rollback()
            user = user_data

    return render_template('users/edit.html', user_data=user, roles=role_repository.all())
    

@bp.route('/<int:user_id>/change', methods=['GET', 'POST'])
@login_required
def change(user_id):
    user = user_repository.get_by_id(user_id)
    if user is None:
        flash('Пользователя нет в базе данных', 'danger')
        return redirect(url_for('users.index'))

    error_fields = []

    if request.method == 'POST':
        old_password = request.form.get('old_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('copy_password', '')

        if not user_repository.check_password(user['username'], old_password):
            flash('Старый пароль введён неверно', 'danger')
            error_fields.append('old')

        elif not check_password(new_password):
            flash('Новый пароль не соответствует требованиям', 'danger')
            error_fields.append('new')

        elif new_password != confirm_password:
            flash('Пароли не совпадают', 'danger')
            error_fields.append('confirm')

        else:
            try:
                user_repository.update_password(user_id, new_password)
                flash('Пароль успешно обновлён', 'success')
                return redirect(url_for('users.index'))
            except connector.errors.DatabaseError:
                flash('Ошибка при сохранении нового пароля', 'danger')

    return render_template('users/change.html', user_data=user, error_fields=error_fields)