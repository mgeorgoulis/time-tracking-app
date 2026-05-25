import hashlib
import hmac
import os


class User:
    def __init__(
        self,
        user_id,
        name=None,
        pin_code=None,
        pin_hash=None,
        must_change_pin=False,
        is_active=True,
        first_name=None,
        last_name=None,
        email=None,
        phone=None,
        street=None,
        postal_code=None,
        city=None,
        country=None
    ):
        self.user_id = user_id

        if first_name is None and last_name is None and name:
            name_parts = name.split(" ", 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ""

        self.first_name = first_name or ""
        self.last_name = last_name or ""

        if name is None:
            name = self.full_name

        self.name = name or ""
        self.email = email
        self.phone = phone
        self.street = street
        self.postal_code = postal_code
        self.city = city
        self.country = country

        self.must_change_pin = must_change_pin
        self.is_active = is_active

        if pin_hash is not None:
            self._pin_hash = pin_hash
        elif pin_code is not None:
            self._validate_pin(pin_code)
            self._pin_hash = self._hash_pin(pin_code)
        else:
            raise ValueError("Es muss entweder ein PIN-Code oder ein PIN-Hash angegeben werden.")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

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

    def set_pin(self, new_pin):
        self._validate_pin(new_pin)
        self._pin_hash = self._hash_pin(new_pin)

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
        name=None,
        pin_code=None,
        department=None,
        pin_hash=None,
        must_change_pin=False,
        is_active=True,
        first_name=None,
        last_name=None,
        email=None,
        phone=None,
        street=None,
        postal_code=None,
        city=None,
        country=None
    ):
        super().__init__(
            user_id,
            name=name,
            pin_code=pin_code,
            pin_hash=pin_hash,
            must_change_pin=must_change_pin,
            is_active=is_active,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            street=street,
            postal_code=postal_code,
            city=city,
            country=country
        )
        self.department = department
        self.role = "employee"

class Apprentice(Employee):
    def __init__(
        self,
        user_id,
        name=None,
        pin_code=None,
        department=None,
        pin_hash=None,
        must_change_pin=False,
        is_active=True,
        first_name=None,
        last_name=None,
        email=None,
        phone=None,
        street=None,
        postal_code=None,
        city=None,
        country=None
    ):
        super().__init__(
            user_id,
            name=name,
            pin_code=pin_code,
            department=department,
            pin_hash=pin_hash,
            must_change_pin=must_change_pin,
            is_active=is_active,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            street=street,
            postal_code=postal_code,
            city=city,
            country=country
        )
        self.role = "apprentice"

class DepartmentManager(Employee):
    def __init__(
        self,
        user_id,
        name=None,
        pin_code=None,
        department=None,
        pin_hash=None,
        must_change_pin=False,
        is_active=True,
        first_name=None,
        last_name=None,
        email=None,
        phone=None,
        street=None,
        postal_code=None,
        city=None,
        country=None
    ):
        super().__init__(
            user_id,
            name=name,
            pin_code=pin_code,
            department=department,
            pin_hash=pin_hash,
            must_change_pin=must_change_pin,
            is_active=is_active,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            street=street,
            postal_code=postal_code,
            city=city,
            country=country
        )
        self.role = "department_manager"

    def can_create_reports(self):
        return True

class Executive(User):
    def __init__(
        self,
        user_id,
        name=None,
        pin_code=None,
        pin_hash=None,
        must_change_pin=False,
        is_active=True,
        first_name=None,
        last_name=None,
        email=None,
        phone=None,
        street=None,
        postal_code=None,
        city=None,
        country=None
    ):
        super().__init__(
            user_id,
            name=name,
            pin_code=pin_code,
            pin_hash=pin_hash,
            must_change_pin=must_change_pin,
            is_active=is_active,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            street=street,
            postal_code=postal_code,
            city=city,
            country=country
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
        name=None,
        pin_code=None,
        pin_hash=None,
        must_change_pin=False,
        is_active=True,
        first_name=None,
        last_name=None,
        email=None,
        phone=None,
        street=None,
        postal_code=None,
        city=None,
        country=None
    ):
        super().__init__(
            user_id,
            name=name,
            pin_code=pin_code,
            pin_hash=pin_hash,
            must_change_pin=must_change_pin,
            is_active=is_active,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            street=street,
            postal_code=postal_code,
            city=city,
            country=country
        )
        self.role = "admin"

    def can_manage_users(self):
        return True

    def can_create_reports(self):
        return True

    def can_view_all_times(self):
        return True
