# AuthSystem 🔐

AuthSystem is an authentication and user management platform developed as a portfolio project to showcase backend development skills with Django and Django REST Framework. The system allows user registration, email activation, password recovery and change, JWT-protected views, and API documentation with Swagger.

## 🚀 Key Features

- ✅ User registration with email activation
- 🔐 Login using JWT (SimpleJWT)
- 📩 Password reset request and confirmation
- 🔁 Password change for authenticated users
- 🛡️ Protected views with authentication permissions
- 📄 Activity logging for password resets
- 📚 Complete API documentation with drf-spectacular (Swagger & Redoc)

## 🧩 Project Structure

```
accounts/              # Authentication and user management 
    serializers.py     # Serializers for registration, 
    views.py           # APIView-based views with validation
    models.py          # CustomUser model
    urls.py            # API endpoints
auth_system/           # Main project configuration
.env                   # Environment variables
password_reset.log     # Password reset log file
```

## ⚙️ Installation and Deployment

Follow these steps to deploy AuthSystem on a Linux server (Ubuntu/Debian):

### 🔧 System Requirements

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv libpq-dev postgresql postgresql-contrib nginx -y
```

### 📁 Clone the Repository

```bash
cd /srv/
sudo git clone https://github.com/jelenu/AuthSystem
cd AuthSystem/
```

### 🐍 Set Up the Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 🗄️ Configure PostgreSQL

```bash
sudo -u postgres psql
```

In the PostgreSQL shell:

```sql
CREATE DATABASE auth_db;
CREATE USER auth_user WITH PASSWORD 'your_secure_password';
ALTER ROLE auth_user SET client_encoding TO 'utf8';
ALTER ROLE auth_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE auth_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE auth_db TO auth_user;

\c auth_db
GRANT ALL ON SCHEMA public TO auth_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO auth_user;
GRANT CONNECT ON DATABASE auth_db TO auth_user;
GRANT CREATE ON DATABASE auth_db TO auth_user;
ALTER SCHEMA public OWNER TO auth_user;
\q
```

### ⚙️ Configure .env

Create a `.env` file with your configuration:

```env
SECRET_KEY=your_secret_key
DB_NAME=auth_db
DB_USER=auth_user
DB_PASSWORD=your_secure_password

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=your_email@gmail.com
```

### 🔧 Configure settings.py

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

EMAIL_BACKEND = config('EMAIL_BACKEND')
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')

STATIC_ROOT = BASE_DIR / 'staticfiles'
DEBUG = False
ALLOWED_HOSTS = ['auth.yourdomain.com', 'localhost', '127.0.0.1']
```

### 🛠️ Migrations and Static Files

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
```

### 🔥 Gunicorn + Nginx

#### Configure Gunicorn

File `/etc/systemd/system/auth_system.service`:

```ini
[Unit]
Description=Gunicorn instance to serve auth_system
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/srv/AuthSystem
ExecStart=/srv/AuthSystem/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/srv/AuthSystem/gunicorn.sock auth_system.wsgi:application
Environment="DJANGO_SETTINGS_MODULE=auth_system.settings"
EnvironmentFile=/srv/AuthSystem/.env

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl start auth_system
sudo systemctl enable auth_system
```

#### Configure Nginx

File `/etc/nginx/sites-available/auth_system`:

```nginx
server {
    listen 80;
    server_name auth.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /srv/AuthSystem/staticfiles;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/srv/AuthSystem/gunicorn.sock;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/auth_system /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

### 🔒 HTTPS with Certbot (Optional)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d auth.yourdomain.com
```

## 🧪 Testing

```bash
pytest
```

## 🔐 Authentication

This project uses JWT for authentication.

- Obtain token: `POST /api/accounts/token/`
- Refresh token: `POST /api/accounts/token/refresh/`

Use in headers:

```
Authorization: Bearer <token>
```

## 📘 API Documentation

- Swagger UI: [https://auth.jesusleon-portfolio.com/api/docs/](https://auth.jesusleon-portfolio.com/api/docs/)
- Redoc: [https://auth.jesusleon-portfolio.com/api/redoc/](https://auth.jesusleon-portfolio.com/api/redoc/)

## 📝 License

This project is licensed under the MIT License.

## 👨‍💻 About Me

Developed by Jesús León Núñez — Backend Web Developer.  
📧 [jesusleon2700@gmail.com] | 💼 [[LinkedIn](https://www.linkedin.com/in/jelenu/)] | 💻 [[GitHub](https://github.com/jelenu/)]