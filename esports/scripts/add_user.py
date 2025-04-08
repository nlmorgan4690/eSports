from esports import create_app, db
from esports.models import User, Role
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    admin_role = Role.query.filter_by(role='Admin').first()

    user = User(
        username='nlmorgan',
        email='nlmorgan@dcsdk12.org',
        password=generate_password_hash('pass'),
        image_file='default.jpg',
        role=admin_role
    )

    db.session.add(user)
    db.session.commit()
    print("✅ User added.")
