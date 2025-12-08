# PassportApp - Quick Start Guide

## 🚀 Quick Start

### First Time Setup
```bash
# Windows
setup.bat

# Linux/Mac
chmod +x setup.sh && ./setup.sh
```

### Starting the App
```bash
# Windows
start.bat

# Linux/Mac
./start.sh
```

### Manual Start
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Run the app
python run.py
```

## 📍 URLs

- **Login**: http://localhost:5000/auth/login
- **Register**: http://localhost:5000/auth/register
- **Dashboard**: http://localhost:5000/ (requires login)
- **Profile**: http://localhost:5000/profile (requires login)
- **Settings**: http://localhost:5000/settings (requires login)

## 🔐 Test Account

Create your own account by registering at:
http://localhost:5000/auth/register

## 📁 Project Structure

```
PassportAPP/
├── app.py          # Flask app configuration
├── models.py       # Database models
├── routes.py       # All routes
├── run.py          # Start point
├── templates/      # HTML files
├── static/         # CSS, JS, images
└── instance/       # Database (auto-created)
```

## 🛠️ Common Commands

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Reset Database
```bash
rm instance/passportapp.db
python run.py
```

### Update Dependencies
```bash
pip freeze > requirements.txt
```

### Deactivate Virtual Environment
```bash
deactivate
```

## 🎨 Features

- ✅ User Registration
- ✅ User Login/Logout
- ✅ Password Hashing
- ✅ Profile Management
- ✅ Settings Page
- ✅ Beautiful UI
- ✅ Responsive Design

## 🐛 Troubleshooting

### Port 5000 in use?
Edit `run.py` and change:
```python
app.run(debug=True, host='0.0.0.0', port=8000)
```

### Database errors?
```bash
rm instance/passportapp.db
python run.py
```

### Import errors?
```bash
# Make sure venv is activated
pip install -r requirements.txt
```

## 📝 Configuration

Edit `.env` file:
```env
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///passportapp.db
FLASK_ENV=development
FLASK_DEBUG=True
```

## 🚢 Deployment

### Heroku
```bash
heroku create your-app
heroku config:set SECRET_KEY=your-secret
git push heroku main
```

### Docker
```bash
docker build -t passportapp .
docker run -p 5000:5000 passportapp
```

## 📚 Resources

- GitHub: https://github.com/mediapower13/PassportAPP
- Flask Docs: https://flask.palletsprojects.com/
- Bootstrap: https://getbootstrap.com/

## 💡 Tips

1. Always activate venv before working
2. Keep SECRET_KEY secure in production
3. Use PostgreSQL for production
4. Enable HTTPS in production
5. Regular backups of database

---

**Happy Coding! 🎉**
