from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import case
from datetime import datetime, date
import bleach

from app.models import db
from .models import User, Animal, Adoption

bp = Blueprint('users', __name__, url_prefix='/users')

status_labels = {
    'pending': 'ожидает рассмотрения',
    'accepted': 'принята',
    'rejected': 'отклонена',
    'rejected_adopted': 'отклонена по причине усыновления',
    'available': 'доступно',
    'adoption': 'в процессе усыновления',
    'adopted': 'усыновлено'
}

@bp.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 10

    status_order = case(
        (Animal.status == 'available', 0),
        else_=1
    )

    pagination = db.session.query(Animal).order_by(
        status_order.asc(),         
        Animal.arrival_date.desc()        
    ).paginate(page=page, per_page=per_page)

    animals = pagination.items

    return render_template("index.html", animals=animals, pagination=pagination, status_labels=status_labels)


@bp.route('/view_animal/<int:animal_id>', methods=['GET', 'POST'])
def view_animal(animal_id):
    user_adoption = None
    if current_user.is_authenticated and current_user.role.name == 'user':
        user_adoption = db.session.query(Adoption).filter_by(
            animal_id=animal_id,
            user_id=current_user.id
        ).first()
    animal = db.session.query(Animal).get(animal_id)
    adoptions = db.session.query(Adoption).filter_by(animal_id=animal_id).order_by(Adoption.date.desc()).all()

    return render_template('view_animal.html', animal=animal, adoptions=adoptions, user_adoption=user_adoption, status_labels=status_labels)

@bp.route('/submit_adoption/<int:animal_id>', methods=['POST'])
@login_required
def submit_adoption(animal_id):
    data = bleach.clean(request.form['contact_details'])
    new_adoption = Adoption(
        date = datetime.utcnow(),
        status = 'pending',
        contact_details = data,
        animal_id = animal_id,
        user_id = current_user.id
    )

    db.session.add(new_adoption)
    db.session.commit()

    return redirect(url_for('index'))