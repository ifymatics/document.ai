from app.core.config import settings
from app.db.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def init_db():
    db = SessionLocal()
    
    # Create initial superuser if configured
    if settings.FIRST_SUPERUSER and settings.FIRST_SUPERUSER_PASSWORD:
        user = db.query(User).filter(User.email == settings.FIRST_SUPERUSER).first()
        if not user:
            superuser = User(
                email=settings.FIRST_SUPERUSER,
                hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                is_superuser=True,
                full_name="Initial Superuser"
            )
            db.add(superuser)
            db.commit()
    
    db.close()

if __name__ == "__main__":
    init_db()