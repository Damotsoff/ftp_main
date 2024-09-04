from flask import Flask, request, render_template, send_from_directory, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_toastr import Toastr  # Импорт модуля для уведомлений

import os
import shutil

# Создаем объект приложения Flask
app = Flask(__name__)
app.secret_key = 'surprisemotherfukaaaaaaaaa'  # Секретный ключ для безопасности сессий
toastr = Toastr()
toastr.init_app(app=app)

# Конфигурируем Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'login'  # Маршрут для авторизации
login_manager.init_app(app)

# Конфигурируем папку для загрузки файлов
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Заглушка для данных пользователей (замените на настоящую базу данных)
users = { 'admin': {'password': 'abrakadabrahuyabra'}
         }

# Класс пользователя для управления сеансами Flask-Login
class User(UserMixin):
    pass

# Загрузка пользователя по идентификатору для Flask-Login
@login_manager.user_loader
def user_loader(username):
    if username not in users:
        return
    user = User()
    user.id = username
    return user

# Определение формы для входа пользователя с использованием Flask-WTF
class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

# Определение маршрута для основной страницы, доступной только авторизованным пользователям
@app.route('/')
@login_required  # Декоратор, требующий авторизацию для доступа к данному маршруту
def index():
    # Получение информации о диске
    disk_usage = shutil.disk_usage("/")
    total = f"Всего: {disk_usage.total / (2**30):.2f} GB"
    used = f"Использовано: {disk_usage.used / (2**30):.2f} GB"
    free = f"Свободно: {disk_usage.free / (2**30):.2f} GB"
    
    # Список файлов в папке загрузок
    filenames = os.listdir(app.config['UPLOAD_FOLDER'])
    
    # Отображение главной страницы с списком файлов и информацией о диске
    return render_template('index.html', filenames=filenames, current_user=current_user, total=total, used=used, free=free)

# Определение маршрута для входа пользователя, обрабатывающего GET и POST запросы
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if username in users and password == users[username]['password']:
            user = User()
            user.id = username
            login_user(user)  # Функция Flask-Login для входа пользователя
            return redirect(url_for('index'))
        else:
            flash('Введите корректные данные', 'error')  # Уведомление об ошибке

    return render_template('login.html', form=form)

# Определение маршрута для выхода пользователя, доступного только авторизованным пользователям
@app.route('/logout')
@login_required
def logout():
    logout_user()  # Функция Flask-Login для выхода пользователя
    return redirect(url_for('login'))

# Определение маршрута для загрузки файла, доступного только авторизованным пользователям
@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return "Не указана часть файла"
    file = request.files['file']
    if file.filename == '':
        return "Файл не выбран"
    if file:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        path = os.path.join(request.base_url, file.filename)           
        file.save(filename)
        flash('Файл успешно загружен', 'info')  # Уведомление о успешной загрузке файла
        return redirect('/')

# Определение маршрута для доступа к загруженным файлам, доступного только авторизованным пользователям
@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Определение маршрута для удаления файлов, доступного только авторизованным пользователям
@app.route('/delete/<filename>', methods=['POST', 'GET'])
@login_required
def delete_file(filename):
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('Файл успешно удален', 'info')  # Уведомление о успешном удалении файла
        return redirect(url_for('index'))
    except Exception as e:
        return str(e)

# Запуск приложения при выполнении этого сценария
# if __name__ == '__main__':
#     # Создание папки для загрузок, если ее нет
#     os.makedirs(UPLOAD_FOLDER, exist_ok=True)
#     # Запуск приложения Flask в режиме отладки на порту 4444
#     app.run(debug=True, port=4444)
