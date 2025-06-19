from flask import Blueprint, request,  render_template, abort, request, make_response, session, redirect, url_for, flash, current_app
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
import os
import uuid
from werkzeug.utils import secure_filename
from datetime import datetime, date
from functools import wraps
import bleach

from app.models import db
from .models import User, Animal, Photo, Adoption

bp = Blueprint('admin', __name__, url_prefix='/admin')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.role.name == "administrator":
            flash('У вас нет доступа к этой странице', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def moderator_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.role.name in ["administrator", "moderator"]:
            flash('У вас нет доступа к этой странице', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/delete_animal/<int:animal_id>', methods=['POST'])
@admin_required
def delete_animal(animal_id):
    animal = db.session.query(Animal).get(animal_id)

    for photo in animal.photos:
        photo_path = os.path.join(current_app.root_path, 'static/uploads', photo.name)
        if os.path.exists(photo_path):
            os.remove(photo_path)

    db.session.delete(animal)
    db.session.commit()
    flash('Животное успешно удалено', 'success')
    return redirect(url_for('index'))

@bp.route('/edit_animal/<int:animal_id>', methods=['GET', 'POST'])
@moderator_required
def edit_animal(animal_id):
    animal = db.session.query(Animal).get(animal_id)
    print("животное", animal)
    if request.method == 'POST':
            try:
                animal.name=bleach.clean(request.form['name'])
                animal.description=bleach.clean(request.form['description'])
                animal.age=bleach.clean(int(request.form['age']))
                animal.breed=bleach.clean(request.form['breed'])
                animal.gender=request.form['gender']
                animal.status=request.form['status']

                db.session.commit()
                flash('Животное успешно изменено', 'success')
                return redirect(url_for('index'))
            
            except:
                db.session.rollback()
                current_app.logger.error(f"Ошибка при добавлении животного: {str(e)}", exc_info=True)
                flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных', 'danger')
                return redirect(request.url)
    
    return render_template('edit_animal.html', animal=animal)


@bp.route('/add_animal', methods=['GET', 'POST'])
@admin_required
def add_animal():
    if request.method == 'POST':
        try:
            if not all(field in request.form for field in ['name', 'description', 'age', 'breed', 'gender', 'status']):
                flash('Заполните все обязательные поля', 'danger')
                return redirect(request.url)
            
            new_animal = Animal(
                name=bleach.clean(request.form['name']),
                description=bleach.clean(request.form['description']),
                age=bleach.clean(int(request.form['age'])),
                breed=bleach.clean(request.form['breed']),
                gender=request.form['gender'],
                status=request.form['status'],
                arrival_date=datetime.utcnow()
            )
            
            db.session.add(new_animal)
            db.session.flush()
            
            if 'photos' not in request.files:
                flash('Не выбраны фотографии', 'warning')
            
            photos = request.files.getlist('photos')
            print("FILES:", request.files)
            print("PHOTOS:", request.files.getlist("photos"))
            
            for photo in photos:
                if photo.filename == '':
                    continue
                
                if photo and allowed_file(photo.filename):
                    filename = secure_filename(photo.filename)
                    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    photo.save(upload_path)
                    print("Сохраняю файл в:", upload_path)
                    new_photo = Photo(
                        name=filename,
                        mime=photo.mimetype,
                        animal_id=new_animal.id
                    )
                    db.session.add(new_photo)

            db.session.commit()
            flash('Животное успешно добавлено', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Ошибка при добавлении животного: {str(e)}", exc_info=True)
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных', 'danger')
            return redirect(request.url)
    
    return render_template('add_animal.html', action='add_animal')


@bp.route('/accept_adoption/<int:adoption_id>', methods=['POST'])
@moderator_required
def accept_adoption(adoption_id):
    adoption = db.session.query(Adoption).get(adoption_id)
    adoption.status = "accepted"
    other_adoptions = db.session.query(Adoption).filter(Adoption.id != adoption_id).all()
    for app in other_adoptions:
        app.status = "rejected_adopted"

    animal = db.session.query(Animal).get(adoption.animal_id)
    animal.status = 'adopted'

    db.session.commit()

    return redirect(url_for('users.view_animal', animal_id=adoption.animal_id))


@bp.route('/accept_reject_adoption/<int:adoption_id>', methods=['POST'])
@moderator_required
def reject_adoption(adoption_id):
    adoption = db.session.query(Adoption).get(adoption_id)
    adoption.status = "rejected"

    db.session.commit()

    return redirect(url_for('users.view_animal', animal_id=adoption.animal_id))