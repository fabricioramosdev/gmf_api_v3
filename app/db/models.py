

from datetime import datetime
from enum import Enum

from sqlalchemy import (Column, String, Integer, Float, Boolean, JSON, Text, DateTime,ForeignKey)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app.db.session import Base


class ChecklistStatus(str, Enum):
    INICIADO = 1
    EM_TRANSPORTE = 2
    ENTREGUE = 3
    CONCLUIDO = 0

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

    status = Column(
        SAEnum(
            ChecklistStatus,
            name="checklist_status",
            native_enum=False,          # grava como VARCHAR + CHECK (portável)
            validate_strings=True,      # valida mesmo se vier string
        ),
        nullable=False,
        default=ChecklistStatus.INICIADO,
        index=True,
    )

    obs = Column(Text, nullable=True)   
    created_in = Column(DateTime(timezone=True), default=datetime.now, nullable=False)


# OK DTO
class ChecklistItemsInspected(Base):

    __tablename__ = "checklists_items_inspected"

    id = Column(Integer, primary_key=True, index=True)

    fk_checklist = Column(Integer, ForeignKey("checklists.id"), nullable=False)
    checklist = relationship("Checklist", backref="itens")


    fk_item = Column(Integer, ForeignKey("inspection_items.id"))
    item = relationship("InspectionItem", back_populates="checklists")
    
    status = Column(String, nullable=False) # Ex: ok, rejeitado, na
    
    fk_photo = Column(
        Integer,
        ForeignKey("upload_files.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    photo = relationship("UploadFile", lazy="joined")
    
    created_in = Column(DateTime(timezone=True), default=datetime.now, nullable=False)


# OK DTO
class UploadFolder(Base):
    __tablename__ = "upload_folders"

    id = Column(Integer, primary_key=True, index=True)
    
    folder_hash = Column(String, unique=True, index=True)
    
    fk_user = Column(Integer, ForeignKey("users.id"))
    fk_checklist = Column(Integer, ForeignKey("checklists.id"))
    fk_file = relationship(
        "UploadFile",
        back_populates="folder",
        cascade="all, delete-orphan",  # opcional, mas útil
    )

    created_in = Column(DateTime(timezone=True), default=datetime.now, nullable=False)


# OK DTO
class UploadFile(Base):
    __tablename__ = "upload_files"

    id = Column(Integer, primary_key=True, index=True)

    file_name = Column(String)
    file_url = Column(String)
    
    fk_folder = Column(Integer, ForeignKey("upload_folders.id"))
    folder = relationship("UploadFolder", back_populates="fk_file")

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
