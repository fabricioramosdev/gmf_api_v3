

from datetime import datetime

from sqlalchemy import (Column, String, Integer, Float, Boolean, JSON, Text, DateTime,ForeignKey)
from sqlalchemy.orm import relationship

from app.db.session import Base




class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, nullable=True)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)    
    nome = Column(String, nullable=True)
    cpf = Column(String, unique=True, nullable=True)
    celular = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=True)    
    cnh = Column(String, unique=True, index=True) # primeiro acesso será a CNH
    hashed_password = Column(String) # senha criptografada
    criado_em = Column(DateTime,  default=datetime.now, nullable=False)


class InspectionItem(Base):
    __tablename__ = "inspection_items"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False, unique=True)
    obrigatorio = Column(Boolean, default=False)  # False = não, True = sim
    foto = Column(Boolean, default=False)         # Novo campo: requer foto?
    status = Column(Boolean, default=False)  # False = inativo, True = ativo
    checklists = relationship("ChecklistInspected", back_populates="item")


class Checklist(Base):
    __tablename__ = "checklists"

    id = Column(Integer, primary_key=True, index=True)

    cliente_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    cliente = relationship("Client", backref="checklists")
    
    versao_onibus = Column(String, nullable=True)  # exemplo: URBANO-CONVENCIONAL-4X2
     
    km_saida = Column(String, nullable=True)
    combustivel_saida = Column(String, nullable=True)
    foto_painel_saida =  Column(String, nullable=True)

    km_chegada = Column(String, nullable=True)
    combustivel_chegada = Column(String, nullable=True)    
    foto_painel_chegada =  Column(String, nullable=True)
    
    observacoes = Column(Text, nullable=True)    
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User")
    
    iniciado_em = Column(DateTime(timezone=True), default=datetime.now, nullable=False)
    finalizado_em = Column(DateTime(timezone=True), nullable=True)

  
class ChecklistInspected(Base):
    __tablename__ = "checklist_inspected"
    id = Column(Integer, primary_key=True, index=True)

    # ID DO CHECKLIST
    checklist_id = Column(Integer, ForeignKey("checklists.id"), nullable=False)
    checklist = relationship("Checklist", backref="itens")

    # ID DO ITEM CHECKED
    inspection_item_id = Column(Integer, ForeignKey("inspection_items.id"))
    item = relationship("InspectionItem", back_populates="checklists")
    
    status = Column(String, nullable=False) # Ex: ok, rejeitado, na
    
    # mantém FK e aceita NULL; se o UploadFile sumir, seta NULL automaticamente
    foto_id = Column(
        Integer,
        ForeignKey("upload_files.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    foto = relationship("UploadFile", lazy="joined")



class UploadFolder(Base):
    __tablename__ = "upload_folders"

    id = Column(Integer, primary_key=True, index=True)
    folder_hash = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    checklist_id = Column(Integer, ForeignKey("checklists.id"))
    files = relationship("UploadFile", back_populates="folder")


class UploadFile(Base):
    __tablename__ = "upload_files"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String)
    file_url = Column(String)
    folder_id = Column(Integer, ForeignKey("upload_folders.id"))
    folder = relationship("UploadFolder", back_populates="files")


class EmergencyRequest(Base):
    __tablename__ = "emergency_requests"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", backref="emergency_requests")
    timestamp = Column(DateTime(timezone=True), default=datetime.now, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    verificado = Column(Boolean, default=False, nullable=False)


class ActionLog(Base):
    __tablename__ = "action_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String, nullable=False)
    previous_data = Column(JSON, nullable=True)
    current_data = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.now, nullable=False)   


class AppVersion(Base):
    __tablename__ = "app_versions"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(String, nullable=False)
    platform = Column(String, nullable=False)  # Ex: "android" ou "ios"
    created_at = Column(DateTime(timezone=True),default=datetime.now, nullable=False)

class BusVersion(Base):
    __tablename__ = "bus_versions"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False, unique=True)
