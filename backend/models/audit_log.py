from datetime import datetime


class AuditLogEntry:
    def __init__(self, actor_id, action, target_type, target_id=None, details=None):
        self.actor_id = actor_id
        self.action = action
        self.target_type = target_type
        self.target_id = target_id
        self.details = details or {}
        self.created_at = datetime.now()

    def to_dict(self):
        return {
            "actor_id": self.actor_id,
            "action": self.action,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "details": self.details,
            "created_at": self.created_at.isoformat()
        }


class AuditLog:
    def __init__(self):
        self.entries = []

    def add_entry(self, entry):
        if not isinstance(entry, AuditLogEntry):
            raise TypeError("Es können nur AuditLogEntry-Objekte hinzugefügt werden.")
        self.entries.append(entry)

    def record(self, actor_id, action, target_type, target_id=None, details=None):
        entry = AuditLogEntry(
            actor_id=actor_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details
        )
        self.add_entry(entry)
        return entry

    def get_entries(self):
        return self.entries

    def find_by_actor(self, actor_id):
        return [entry for entry in self.entries if entry.actor_id == actor_id]

    def find_by_action(self, action):
        return [entry for entry in self.entries if entry.action == action]
