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

### 1. Clone the repository

```bash
git clone https://github.com/mediapower13/PassportAPP.git
cd PassportAPP
```

### 2. Create a virtual environment

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

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the root directory (already created):

```env
SECRET_KEY=your-secret-key-here-change-in-production
DATABASE_URL=sqlite:///passportapp.db
FLASK_ENV=development
FLASK_DEBUG=True
```

**Important**: Change the `SECRET_KEY` to a random secure string in production!

### 5. Run the application

```bash
python app.py
```

The application will be available at: `http://localhost:5000`

## 📱 Application Structure

```
PassportAPP/
│
├── app.py                 # Main Flask application
├── models.py              # Database models (User model)
├── routes.py              # Application routes (auth & main)
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── .gitignore            # Git ignore file
│
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── dashboard.html    # User dashboard
│   ├── profile.html      # User profile
│   └── settings.html     # Settings page
│
└── static/               # Static files
    ├── css/
    │   └── style.css     # Custom styles
    ├── js/
    │   └── main.js       # JavaScript functions
    └── images/           # Image assets
```

## 🎨 Features Breakdown

### Authentication System
- **Registration**: Secure user registration with validation
- **Login**: Username/password authentication
- **Logout**: Secure session termination
- **Password Security**: Hashed passwords using Werkzeug
- **Session Management**: Flask-Login for user sessions

### User Dashboard
- Welcome message with user name
- Statistics cards (Member since, Status, Security, Last login)
- Quick actions (Edit Profile, Settings, Logout)
- Account information display
- Activity timeline

### Profile Management
- View user information
- Edit name and bio
- Profile statistics
- Beautiful profile card design

### Settings
- Security settings (Password change, 2FA)
- Notification preferences
- Account deletion option
- Toggle switches for settings

## 🔒 Security Features

- Password hashing with Werkzeug
- CSRF protection (Flask default)
- Session management
- Secure secret key configuration
- Environment variable protection

## 🎨 UI/UX Features

- Modern gradient backgrounds
- Smooth animations and transitions
- Floating shapes animation
- Responsive design (mobile-first)
- Beautiful card designs
- Font Awesome icons
- Custom color scheme
- Password visibility toggle
- Auto-dismissing alerts
- Loading animations

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
```

5. Deploy:
```bash
git push heroku main
```

### Using PythonAnywhere

1. Upload files to PythonAnywhere
2. Create a virtual environment
3. Install dependencies
4. Configure WSGI file
5. Reload the web app

## 📦 Dependencies

- Flask==3.0.0
- Flask-SQLAlchemy==3.1.1
- Flask-Login==0.6.3
- python-dotenv==1.0.0
- email-validator==2.1.0
- Werkzeug==3.0.1

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

**mediapower13**
- GitHub: [@mediapower13](https://github.com/mediapower13)

## 🙏 Acknowledgments

- Flask documentation
- Bootstrap team
- Font Awesome
- Google Fonts

## 📧 Support

For support, email your-email@example.com or create an issue in the repository.

---

**Made with ❤️ and Python**
