import uuid
from datetime import datetime


class Session:
    def __init__(self, token, user, created_at=None):
        self.token = token
        self.user = user
        self.created_at = created_at or datetime.now()
        self.active = True

    def deactivate(self):
        self.active = False


class SessionService:
    def __init__(self, audit_log):
        self.audit_log = audit_log
        self.sessions = {}

    def create_session(self, user):
        token = str(uuid.uuid4())
        session = Session(token, user)

        self.sessions[token] = session

        self.audit_log.record(
            actor_id=user.user_id,
            action="session_created",
            target_type="Session",
            target_id=None,
            details={"employee_name": user.name}
        )

        return session

    def get_user_by_token(self, token):
        session = self.sessions.get(token)

        if session is None:
            return None

        if not session.active:
            return None

        return session.user

    def logout(self, token):
        session = self.sessions.get(token)

        if session is None:
            raise ValueError("Session wurde nicht gefunden.")

        session.deactivate()

        self.audit_log.record(
            actor_id=session.user.user_id,
            action="session_closed",
            target_type="Session",
            target_id=None,
            details={"employee_name": session.user.name}
        )

        return True

    def is_valid_token(self, token):
        return self.get_user_by_token(token) is not None
