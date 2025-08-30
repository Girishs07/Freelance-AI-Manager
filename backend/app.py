from __init__ import create_app, db

app = create_app()

# Create tables
with app.app_context():
    db.create_all()
    print("Database tables created successfully!")

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')