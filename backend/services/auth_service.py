class AuthService:
    def __init__(self, users, audit_log):
        self.users = users
        self.audit_log = audit_log

    def login_with_pin(self, user_id, pin_code):
        user = self.find_user_by_id(user_id)

        if user is None:
            self.audit_log.record(
                actor_id=user_id,
                action="login_failed",
                target_type="User",
                target_id=user_id,
                details={"reason": "user_not_found"}
            )
            raise ValueError("Benutzer wurde nicht gefunden.")

        if not user.check_pin(pin_code):
            self.audit_log.record(
                actor_id=user.user_id,
                action="login_failed",
                target_type="User",
                target_id=user.user_id,
                details={"reason": "invalid_pin", "employee_name": user.name}
            )
            raise ValueError("PIN-Code ist ungültig.")

        self.audit_log.record(
            actor_id=user.user_id,
            action="login_success",
            target_type="User",
            target_id=user.user_id,
            details={"employee_name": user.name}
        )

        return user

    def find_user_by_id(self, user_id):
        for user in self.users:
            if user.user_id == user_id:
                return user

        return None
