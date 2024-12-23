"""run.py"""
from app import create_app, db
from app.models import add_user_roles


app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        add_user_roles()
    app.run(debug=True)