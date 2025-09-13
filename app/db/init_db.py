from app.db.session import engine
from app.db.models import Base

def init():
    print("⏳ Criando as tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")

if __name__ == "__main__":
    init()
