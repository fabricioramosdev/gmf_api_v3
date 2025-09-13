from app.db.session import get_db
from app.db.crud import create_user

def create_admin():
    from sqlalchemy.orm import Session
    db: Session = next(get_db())
    
    name =  "Fabricio Rogerio Lopes Ramos"
    mail = "fabricio.ramos.dev@gmail.com"
    password = "admin123" 
    num_cnh = '123456789'
    
    create_user(db, mail = mail, password = password, name = name, num_cnh=num_cnh)
    print(f"✅ Usuário inicial criado: email={mail} / senha={password}")

if __name__ == "__main__":
    create_admin()
