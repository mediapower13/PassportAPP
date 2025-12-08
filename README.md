# PassportApp - Python Flask Authentication System

A modern, secure, and beautiful authentication system built with Python Flask, featuring user registration, login, profile management, and a stunning UI.

## 🚀 Features

- ✅ **User Authentication**: Secure login and registration system
- ✅ **Password Hashing**: Werkzeug security for password protection
- ✅ **Session Management**: Flask-Login for user session handling
- ✅ **Beautiful UI**: Modern gradient design with animations
- ✅ **Responsive Design**: Works perfectly on all devices
- ✅ **User Dashboard**: Personalized dashboard with statistics
- ✅ **Profile Management**: Edit user profile and bio
- ✅ **Settings Page**: Account settings and security options
- ✅ **SQLite Database**: Easy-to-use database with SQLAlchemy ORM
- ✅ **Environment Variables**: Secure configuration management
- ✅ **Easy Setup**: Automated setup and start scripts

## 🛠️ Tech Stack

- **Backend**: Python 3.8+, Flask 3.0
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login, Werkzeug Security
- **Frontend**: Bootstrap 5, Custom CSS3, JavaScript
- **Icons**: Font Awesome 6
- **Fonts**: Google Fonts (Poppins)

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

## 🔧 Installation

### Quick Setup (Recommended)

**Windows:**
```bash
# Clone the repository
git clone https://github.com/mediapower13/PassportAPP.git
cd PassportAPP

# Run setup script
setup.bat

# Start the application
start.bat
```

**macOS/Linux:**
```bash
# Clone the repository
git clone https://github.com/mediapower13/PassportAPP.git
cd PassportAPP

# Make scripts executable
chmod +x setup.sh start.sh

# Run setup script
./setup.sh

# Start the application
./start.sh
```

### Manual Setup

#### 1. Clone the repository

```bash
git clone https://github.com/mediapower13/PassportAPP.git
cd PassportAPP
```

#### 2. Create a virtual environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install dependencies

```bash
pip install -r requirements.txt
```

#### 4. Configure environment variables

The `.env` file is already created with default settings. For production, update:

```env
SECRET_KEY=your-secret-key-here-change-in-production
DATABASE_URL=sqlite:///passportapp.db
FLASK_ENV=production
FLASK_DEBUG=False
```

**Important**: Generate a secure `SECRET_KEY` for production!

#### 5. Run the application

```bash
python run.py
```

The application will be available at: `http://localhost:5000`

## 📱 Application Structure

```
PassportAPP/
│
├── app.py                 # Main Flask application & configuration
├── models.py              # Database models (User model)
├── routes.py              # Application routes (auth & main blueprints)
├── run.py                 # Application entry point
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in git)
├── .gitignore            # Git ignore file
├── README.md             # Documentation
│
├── setup.bat             # Windows setup script
├── setup.sh              # Linux/Mac setup script
├── start.bat             # Windows start script
├── start.sh              # Linux/Mac start script
│
├── templates/            # Jinja2 HTML templates
│   ├── base.html         # Base template with CSS/JS
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── dashboard.html    # User dashboard (protected)
│   ├── profile.html      # User profile (protected)
│   └── settings.html     # Settings page (protected)
│
├── static/               # Static files
│   ├── css/
│   │   └── style.css     # Custom styles with animations
│   ├── js/
│   │   └── main.js       # JavaScript functions
│   └── images/           # Image assets
│
├── instance/             # Instance folder (auto-generated)
│   └── passportapp.db   # SQLite database (auto-generated)
│
└── venv/                 # Virtual environment (auto-generated)
```

## 🎨 Features Breakdown

### Authentication System
- **Registration**: Secure user registration with validation
- **Login**: Username/password authentication with "Remember Me"
- **Logout**: Secure session termination
- **Password Security**: Hashed passwords using Werkzeug
- **Session Management**: Flask-Login for persistent sessions
- **Route Protection**: Login required decorators

### User Dashboard
- Welcome message with personalized greeting
- Statistics cards (Member since, Status, Security, Last login)
- Quick actions (Edit Profile, Settings, Logout)
- Account information display
- Activity timeline
- Beautiful gradient design

### Profile Management
- View user information
- Edit name and bio
- Profile statistics
- Beautiful profile card design
- Avatar icon display

### Settings
- Security settings (Password change, 2FA toggle)
- Notification preferences
- Account deletion option
- Toggle switches for settings
- Danger zone for critical actions

## 🔒 Security Features

- Password hashing with Werkzeug (bcrypt-based)
- CSRF protection (Flask default)
- Session management with secure cookies
- Secret key configuration
- Environment variable protection
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection (Jinja2 auto-escaping)

## 🎨 UI/UX Features

- Modern gradient backgrounds
- Smooth animations and transitions
- Floating shapes animation on auth pages
- Responsive design (mobile-first approach)
- Beautiful card designs with shadows
- Font Awesome 6 icons throughout
- Custom color scheme with CSS variables
- Password visibility toggle
- Auto-dismissing alerts (5 seconds)
- Loading animations on form submission
- Hover effects and transitions

## 📝 API Routes

### Authentication Routes (`/auth`)
- `GET/POST /auth/register` - User registration
- `GET/POST /auth/login` - User login
- `GET /auth/logout` - User logout

### Main Routes (`/`)
- `GET /` - Dashboard (requires login)
- `GET /profile` - User profile (requires login)
- `POST /update_profile` - Update profile (requires login)
- `GET /settings` - Settings page (requires login)

## 🚀 Deployment

### Using Heroku

1. Install Heroku CLI
2. Create a Heroku app:
```bash
heroku create your-app-name
```

3. Add PostgreSQL addon:
```bash
heroku addons:create heroku-postgresql:hobby-dev
```

4. Set environment variables:
```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set FLASK_ENV=production
```

5. Create Procfile:
```
web: python run.py
```

6. Deploy:
```bash
git push heroku main
```

### Using PythonAnywhere

1. Upload files to PythonAnywhere
2. Create a virtual environment in Bash:
```bash
mkvirtualenv --python=/usr/bin/python3.8 passportapp
pip install -r requirements.txt
```

3. Configure WSGI file:
```python
import sys
path = '/home/yourusername/PassportAPP'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```

4. Reload the web app

### Using Docker

Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "run.py"]
```

Build and run:
```bash
docker build -t passportapp .
docker run -p 5000:5000 passportapp
```

## 📦 Dependencies

```
Flask==3.0.0              # Web framework
Flask-SQLAlchemy==3.1.1   # ORM for database
Flask-Login==0.6.3        # User session management
python-dotenv==1.0.0      # Environment variables
email-validator==2.1.0    # Email validation
Werkzeug==3.0.1          # Security utilities
```

## 🐛 Troubleshooting

### Database Issues
If you encounter database errors:
```bash
# Delete the database and recreate
rm instance/passportapp.db
python run.py
```

### Port Already in Use
If port 5000 is already in use:
```python
# Edit run.py and change the port
app.run(debug=True, host='0.0.0.0', port=8000)
```

### Module Import Errors
Make sure virtual environment is activated:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

## 🧪 Testing

Create test accounts:
1. Start the application
2. Navigate to http://localhost:5000/auth/register
3. Fill in the registration form
4. Login with your credentials

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**mediapower13**
- GitHub: [@mediapower13](https://github.com/mediapower13)
- Repository: [PassportAPP](https://github.com/mediapower13/PassportAPP)

## 🙏 Acknowledgments

- Flask documentation and community
- Bootstrap team for the amazing CSS framework
- Font Awesome for beautiful icons
- Google Fonts for Poppins typeface
- SQLAlchemy for the powerful ORM

## 📧 Support

For support, create an issue in the repository or contact via GitHub.

## 🔮 Future Enhancements

- [ ] Email verification on registration
- [ ] Password reset functionality
- [ ] Two-factor authentication (2FA)
- [ ] OAuth integration (Google, GitHub)
- [ ] Profile image upload
- [ ] Password strength meter
- [ ] Email notifications
- [ ] Activity log
- [ ] Admin panel
- [ ] API endpoints (REST)
- [ ] Unit tests
- [ ] Integration tests

## 📝 Changelog

### Version 1.0.0 (December 2025)
- Initial release
- User authentication (register, login, logout)
- User profile management
- Settings page
- Beautiful responsive UI
- SQLite database
- Complete documentation

---

**Built with ❤️ using Python & Flask**

**⭐ Star this repository if you find it useful!**
