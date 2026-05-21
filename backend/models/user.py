import hashlib
import hmac
import os


class User:
    def __init__(
        self,
        user_id,
        name,
        pin_code=None,
        pin_hash=None,
        must_change_pin=False,
        is_active=True
    ):

        self.user_id = user_id
        self.name = name
        self.must_change_pin = must_change_pin
        self.is_active = is_active

        if pin_hash is not None:
            self._pin_hash = pin_hash
        elif pin_code is not None:
            self._validate_pin(pin_code)
            self._pin_hash = self._hash_pin(pin_code)
        else:
            raise ValueError("Es muss entweder ein PIN-Code oder ein PIN-Hash angegeben werden.")

    def check_pin(self, pin_code):
        salt, stored_hash = self._pin_hash.split(":")
        new_hash = hashlib.pbkdf2_hmac(
            "sha256",
            pin_code.encode("utf-8"),
            bytes.fromhex(salt),
            100_000
        ).hex()

        return hmac.compare_digest(stored_hash, new_hash)

    def change_pin(self, current_pin, new_pin):
        if not self.check_pin(current_pin):
            raise ValueError("Aktueller PIN ist ungültig.")

        self._validate_pin(new_pin)
        self._pin_hash = self._hash_pin(new_pin)
        self.must_change_pin = False

        return True

    def force_change_pin(self, new_pin):
        self._validate_pin(new_pin)
        self._pin_hash = self._hash_pin(new_pin)
        self.must_change_pin = False

        return True

    def get_pin_hash(self):
        return self._pin_hash

    def _hash_pin(self, pin_code):
        salt = os.urandom(16)

        pin_hash = hashlib.pbkdf2_hmac(
            "sha256",
            pin_code.encode("utf-8"),
            salt,
            100_000
        ).hex()

        return f"{salt.hex()}:{pin_hash}"

    def _validate_pin(self, pin_code):
        if not isinstance(pin_code, str):
            raise ValueError("PIN muss als Text übergeben werden.")

        if len(pin_code) != 4 or not pin_code.isdigit():
            raise ValueError("PIN muss genau 4 Ziffern enthalten.")

    def can_clock_in(self):
        return True

    def can_manage_users(self):
        return False

    def can_create_reports(self):
        return False

    def can_view_all_times(self):
        return False


class Employee(User):
    def __init__(
        self,
        user_id,
        name,
        pin_code=None,
        department=None,
        pin_hash=None,
        must_change_pin=False,
        is_active=True
    ):
        super().__init__(
            user_id,
            name,
            pin_code=pin_code,
            pin_hash=pin_hash,
            must_change_pin=must_change_pin,
            is_active=is_active
        )
        self.department = department
        self.role = "employee"

class Apprentice(Employee):
    def __init__(
        self,
        user_id,
        name,
        pin_code=None,
        department=None,
        pin_hash=None,
        must_change_pin=False,
        is_active=True
    ):
        super().__init__(
            user_id,
            name,
            pin_code=pin_code,
            department=department,
            pin_hash=pin_hash,
            must_change_pin=must_change_pin,
            is_active=is_active
        )
        self.role = "apprentice"

class DepartmentManager(Employee):
    def __init__(
        self,
        user_id,
        name,
        pin_code=None,
        department=None,
        pin_hash=None,
        must_change_pin=False,
        is_active=True
    ):
        super().__init__(
            user_id,
            name,
            pin_code=pin_code,
            department=department,
            pin_hash=pin_hash,
            must_change_pin=must_change_pin,
            is_active=is_active
        )
        self.role = "department_manager"

    def can_create_reports(self):
        return True


class Executive(User):
    def __init__(
        self,
        user_id,
        name,
        pin_code=None,
        pin_hash=None,
        must_change_pin=False,
        is_active=True
    ):
        super().__init__(
            user_id,
            name,
            pin_code=pin_code,
            pin_hash=pin_hash,
            must_change_pin=must_change_pin,
            is_active=is_active
        )
        self.role = "executive"

    def can_create_reports(self):
        return True

    def can_view_all_times(self):
        return True


class Admin(User):
    def __init__(
        self,
        user_id,
        name,
        pin_code=None,
        pin_hash=None,
        must_change_pin=False,
        is_active=True
    ):
        super().__init__(
            user_id,
            name,
            pin_code=pin_code,
            pin_hash=pin_hash,
            must_change_pin=must_change_pin,
            is_active=is_active
        )
        self.role = "admin"

    def can_manage_users(self):
        return True

    def can_create_reports(self):
        return True

    def can_view_all_times(self):
        return True
