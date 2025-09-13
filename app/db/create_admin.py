from app.db.session import get_db
from app.db.crud import create_user
from app.core.security import get_password_hash

def create_admin():
    from sqlalchemy.orm import Session
    db: Session = next(get_db())
    
    nome =  "Fabricio Rogerio Lopes Ramos"
    email = "fabricio.ramos.dev@gmail.com"
    password = "admin123"  # Senha inicial
    
    create_user(db, email = email, password = password, nome = nome)
    print(f"✅ Usuário inicial criado: email={email} / senha={password}")

if __name__ == "__main__":
    create_admin()
