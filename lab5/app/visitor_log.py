from flask import Blueprint, request,  render_template, abort, request, make_response, session, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required

import mysql.connector as connector

from .repositories.user_repository import UserRepository
from .repositories.role_repository import RoleRepository
from .repositories.visit_log_repository import VisitLogRepository
from .check_pass_and_login import check_password, check_login
from functools import wraps
from app import db
import csv
from io import StringIO


login_manager = LoginManager()
login_manager.login_message = 'Необходимо авторизоваться'
login_manager.login_message_category = 'warning'

bp = Blueprint('log', __name__, url_prefix='/log')
@bp.errorhandler(connector.errors.DatabaseError)
def handler():
    pass

@bp.route('/report')
def report():
    page = request.args.get('page', 1, type=int)

    repo = VisitLogRepository(db)
    logs = repo.get_paginated(page)
    total = repo.count_all()
    page_size = repo.page_size

    return render_template(
        'log/report.html',
        logs=logs,
        page=page,
        total=total,
        page_size=page_size
    )

@bp.route('/report/pages')
@login_required
def report_by_pages():
    repo = VisitLogRepository(db)
    stats = repo.count_by_pages()
    return render_template('log/report_by_pages.html', stats=stats)

@bp.route('/report/pages/export')
@login_required
def export_pages_csv():
    repo = VisitLogRepository(db)
    stats = repo.count_by_pages()

    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(["№", "Страница", "Количество посещений"])

    for idx, row in enumerate(stats, 1):
        writer.writerow([idx, row['path'], row['visit_count']])

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=report_by_pages.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@bp.route('/report/users')
@login_required
def report_by_users():
    repo = VisitLogRepository(db)
    stats = repo.count_by_users()
    return render_template('log/report_by_users.html', stats=stats)

@bp.route('/report/users/export')
@login_required
def export_users_csv():
    repo = VisitLogRepository(db)
    stats = repo.count_by_users()

    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(["№", "Пользователь", "Количество посещений"])

    for idx, row in enumerate(stats, 1):
        name = row['full_name'] if row['full_name'] else 'Неаутентифицированный пользователь'
        writer.writerow([idx, name, row['visit_count']])

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=report_by_users.csv"
    output.headers["Content-type"] = "text/csv"
    return output