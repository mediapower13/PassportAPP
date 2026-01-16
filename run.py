
from app import app, db

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✓ Database initialized successfully")
        print("✓ Starting Flask development server...")
        print("✓ Open http://localhost:5000 in your browser")
        print("-" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
