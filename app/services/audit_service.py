from sqlalchemy.orm import Session
from app.db.models import ActionLog, User

def log_action(
    action: str,
    previous_data: dict,
    current_data: dict,
    db: Session,
    current_user: User
):
    """
    Registra uma ação no banco de dados. current_user e db são obrigatórios.
    """
    log_entry = ActionLog(
        user_id=current_user.id,
        action=action,
        previous_data=previous_data,
        current_data=current_data
    )
    try:
        db.add(log_entry)
        db.commit()
    except Exception as e:
        print(f"[LOG ERROR] {e}")
