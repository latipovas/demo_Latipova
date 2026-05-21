from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# модели базы 
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    birth_date = db.Column(db.String(10), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    requests = db.relationship('Request', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)

class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transport_type = db.Column(db.String(50), nullable=False)  # автобус, электробус, трамвай
    preferred_date = db.Column(db.String(10), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default='Новая')  # Новая, Идет обучение, Обучение завершено
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    request_id = db.Column(db.Integer, db.ForeignKey('request.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    request = db.relationship('Request', backref='reviews')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def validate_login(login):
    if len(login) < 6:
        return False, "Логин должен содержать минимум 6 символов"
    if not re.match(r'^[a-zA-Z0-9]+$', login):
        return False, "Логин может содержать только латинские буквы и цифры"
    return True, ""


def validate_password(password):
    if len(password) < 8:
        return False, "Пароль должен содержать минимум 8 символов"
    return True, ""


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        full_name = request.form['full_name']
        birth_date = request.form['birth_date']
        phone = request.form['phone']
        email = request.form['email']
        

        login_valid, login_msg = validate_login(login)
        password_valid, password_msg = validate_password(password)
        
        if not login_valid:
            flash(login_msg, 'danger')
        elif not password_valid:
            flash(password_msg, 'danger')
        elif User.query.filter_by(login=login).first():
            flash('Логин уже существует', 'danger')
        else:
            hashed_password = generate_password_hash(password)
            new_user = User(
                login=login,
                password_hash=hashed_password,
                full_name=full_name,
                birth_date=birth_date,
                phone=phone,
                email=email,
                is_admin=False
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Регистрация успешна! Теперь войдите в систему.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        user = User.query.filter_by(login=login).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            if user.is_admin:
                return redirect(url_for('admin'))
            return redirect(url_for('dashboard'))
        else:
            flash('Неверный логин или пароль', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin'))
    user_requests = Request.query.filter_by(user_id=current_user.id).order_by(Request.created_at.desc()).all()

    user_reviews = Review.query.filter_by(user_id=current_user.id).all()
    review_dict = {r.request_id: r.text for r in user_reviews}
    return render_template('dashboard.html', requests=user_requests, reviews=review_dict)

@app.route('/new_request', methods=['GET', 'POST'])
@login_required
def new_request():
    if current_user.is_admin:
        return redirect(url_for('admin'))
    if request.method == 'POST':
        transport_type = request.form['transport_type']
        preferred_date = request.form['preferred_date']
        payment_method = request.form['payment_method']
        

        try:
            datetime.strptime(preferred_date, '%d.%m.%Y')
        except ValueError:
            flash('Неверный формат даты. Используйте ДД.ММ.ГГГГ', 'danger')
            return render_template('new_request.html')
        
        new_req = Request(
            user_id=current_user.id,
            transport_type=transport_type,
            preferred_date=preferred_date,
            payment_method=payment_method,
            status='Новая'
        )
        db.session.add(new_req)
        db.session.commit()
        flash('Заявка успешно создана и отправлена администратору', 'success')
        return redirect(url_for('dashboard'))
    return render_template('new_request.html')

@app.route('/submit_review/<int:request_id>', methods=['POST'])
@login_required
def submit_review(request_id):
    req = Request.query.get_or_404(request_id)
    if req.user_id != current_user.id:
        flash('Доступ запрещён', 'danger')
        return redirect(url_for('dashboard'))
    

    if req.status != 'Обучение завершено':
        flash('Отзыв можно оставить только после завершения обучения', 'warning')
        return redirect(url_for('dashboard'))
    
    existing_review = Review.query.filter_by(request_id=request_id, user_id=current_user.id).first()
    if existing_review:
        flash('Вы уже оставили отзыв на эту заявку', 'warning')
        return redirect(url_for('dashboard'))
    
    review_text = request.form['review_text']
    if review_text.strip():
        new_review = Review(user_id=current_user.id, request_id=request_id, text=review_text.strip())
        db.session.add(new_review)
        db.session.commit()
        flash('Спасибо за ваш отзыв!', 'success')
    else:
        flash('Текст отзыва не может быть пустым', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        return redirect(url_for('dashboard'))
    

    status_filter = request.args.get('status', '')
    transport_filter = request.args.get('transport', '')
    page = request.args.get('page', 1, type=int)
    per_page = 5
    
    query = Request.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    if transport_filter:
        query = query.filter_by(transport_type=transport_filter)
    
    paginated = query.order_by(Request.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('admin.html', 
                         requests=paginated.items,
                         pagination=paginated,
                         status_filter=status_filter,
                         transport_filter=transport_filter)

@app.route('/admin/update_status/<int:request_id>', methods=['POST'])
@login_required
def update_status(request_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    req = Request.query.get_or_404(request_id)
    new_status = request.form['status']
    if new_status in ['Новая', 'Идет обучение', 'Обучение завершено']:
        req.status = new_status
        db.session.commit()
        flash(f'Статус заявки #{request_id} изменён на "{new_status}"', 'success')
    else:
        flash('Некорректный статус', 'danger')
    return redirect(url_for('admin'))


with app.app_context():
    db.create_all()
    admin = User.query.filter_by(login='Admin26').first()
    if not admin:
        admin_user = User(
            login='Admin26',
            password_hash=generate_password_hash('Demo20'),
            full_name='Администратор',
            birth_date='01.01.1990',
            phone='+70000000000',
            email='admin@passazhiram.ru',
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Администратор создан: Admin26 / Demo20")

if __name__ == '__main__':
    app.run(debug=True)
