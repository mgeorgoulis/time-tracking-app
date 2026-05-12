import unittest

from backend.models.user import Employee


class TestPinHashing(unittest.TestCase):

    def test_correct_pin_is_accepted(self):
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")

        self.assertTrue(employee.check_pin("1234"))

    def test_wrong_pin_is_rejected(self):
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")

        self.assertFalse(employee.check_pin("9999"))

    def test_pin_is_not_stored_as_plain_text(self):
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")

        self.assertNotEqual(employee.get_pin_hash(), "1234")

    def test_same_pin_creates_different_hashes(self):
        employee_one = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")
        employee_two = Employee(2, "Lena Mitarbeiterin", "1234", "Verkauf")

        self.assertNotEqual(
            employee_one.get_pin_hash(),
            employee_two.get_pin_hash()
        )

    def test_user_can_be_recreated_from_existing_pin_hash(self):
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")
        stored_hash = employee.get_pin_hash()

        loaded_employee = Employee(
            1,
            "Max Mitarbeiter",
            department="Verkauf",
            pin_hash=stored_hash
        )

        self.assertTrue(loaded_employee.check_pin("1234"))


if __name__ == "__main__":
    unittest.main()
