

from datetime import datetime
from enum import Enum

from sqlalchemy import (Column, String, Integer, Float, Boolean, JSON, Text, DateTime,ForeignKey, UniqueConstraint)
from sqlalchemy.orm import relationship

from app.db.session import Base


class ChecklistItemsInspected(Base):
    __tablename__ = "checklists_items_inspected"
    id = Column(Integer, primary_key=True, index=True)

    fk_checklist = Column(Integer, ForeignKey("checklists.id", ondelete="CASCADE"), nullable=False, index=True)
    checklist = relationship("Checklist", backref="itens")

    fk_item = Column(Integer, ForeignKey("inspection_items.id", ondelete="RESTRICT"), nullable=False, index=True)
    item = relationship("InspectionItem", back_populates="checklists")

    status = Column(String, nullable=False)
    fk_foto = Column(Integer, ForeignKey("upload_files.id", ondelete="SET NULL"), nullable=True, index=True)
    foto = relationship("UploadFile")

    created_in = Column(DateTime(timezone=True), default=datetime.now, nullable=False)

    __table_args__ = (
        UniqueConstraint("fk_checklist", "fk_item", name="uq_checklist_item"),
    )


# OK DTO
class Client(Base):

    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    mail = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    status = Column(Boolean, default=True)

    frequency_order = Column(Integer, default=0)
    created_in = Column(DateTime(timezone=True), default=datetime.now, nullable=False)


# OK DTO
class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)    
    name = Column(String, nullable=True)

    phone = Column(String, nullable=True)
    mail = Column(String, unique=True, nullable=True)   

    num_cnh = Column(String, unique=True, index=True) 

    hashed_password = Column(String) # senha criptografada

    is_admin  = Column(Boolean, default=False)
    
    status = Column(Boolean, default=True)
    created_in = Column(DateTime(timezone=True), default=datetime.now, nullable=False)


# OK DTO
class Checklist(Base):
    
    __tablename__ = "checklists"
    
    id = Column(Integer, primary_key=True, index=True)

    fk_cliente = Column(Integer, ForeignKey("clients.id"), nullable=False)
    cliente = relationship("Client", backref="checklists")

    version_bus = Column(String, nullable=True)  
    
    km_start = Column(Integer, nullable=True)
    fuel_start = Column(String, nullable=True)
    date_start = Column(DateTime(timezone=True), default=datetime.now, nullable=False)
    
    km_end = Column(Integer, nullable=True)
    fuel_end = Column(String, nullable=True)
    date_end = Column(DateTime(timezone=True), default=datetime.now, nullable=False)

    fk_user = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User")

    status = Column(String, nullable=True)

    obs = Column(Text, nullable=True)   
    created_in = Column(DateTime(timezone=True), default=datetime.now, nullable=False)

# OK DTO
# --- UploadFolder (1) ---
class UploadFolder(Base):
    __tablename__ = "upload_folders"

    id = Column(Integer, primary_key=True, index=True)
    folder_hash = Column(String, unique=True, index=True)

    fk_user = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    fk_checklist = Column(Integer, ForeignKey("checklists.id"), nullable=True, index=True)

    # Uma pasta -> muitos arquivos
    files = relationship(
        "UploadFile",
        back_populates="folder",
        cascade="all, delete-orphan",   # opcional (bom pra limpeza)
        passive_deletes=True,           # se a FK tiver ondelete=CASCADE
    )

    created_in = Column(DateTime(timezone=True), default=datetime.now, nullable=False)

# OK DTO
# --- UploadFile (N) ---
class UploadFile(Base):
    __tablename__ = "upload_files"

    id = Column(Integer, primary_key=True, index=True)

    file_name = Column(String, nullable=False)
    file_url = Column(String, nullable=False)

    fk_folder = Column(
        Integer,
        ForeignKey("upload_folders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # volta para a pasta (nome deve bater com o lado de lá)
    folder = relationship("UploadFolder", back_populates="files")

    created_in = Column(DateTime(timezone=True), default=datetime.now, nullable=False)



# OK DTO
class InspectionItem(Base):
    __tablename__ = "inspection_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    mandatory = Column(Boolean, default=False)  # False = não, True = sim
    need_for_photo = Column(Boolean, default=False)         # Novo campo: requer foto?
    status = Column(Boolean, default=True)  # False = inativo, True = ativo

    checklists = relationship(
        "ChecklistItemsInspected",
        back_populates="item",
        cascade="all, delete-orphan",
    )
    created_in = Column(DateTime(timezone=True), default=datetime.now, nullable=False)


# OK DTO
class EmergencyRequests(Base):
    __tablename__ = "emergency_requests"

    id = Column(Integer, primary_key=True, index=True)

    fk_user = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", backref="emergency_requests")

    date_requested = Column(DateTime(timezone=True), default=datetime.now, nullable=False)
    lat = Column(Float, nullable=True)
    long = Column(Float, nullable=True)
    checked = Column(Boolean, default=False, nullable=False)

    created_in = Column(DateTime(timezone=True), default=datetime.now, nullable=False)



class ActionLog(Base):
    __tablename__ = "action_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String, nullable=False)
    previous_data = Column(JSON, nullable=True)
    current_data = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.now, nullable=False)
