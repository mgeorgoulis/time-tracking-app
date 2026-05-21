import unittest

from backend.models.user import Employee


class TestPinChange(unittest.TestCase):

    def test_user_can_change_pin_with_correct_current_pin(self):
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")

        result = employee.change_pin("1234", "5678")

        self.assertTrue(result)
        self.assertTrue(employee.check_pin("5678"))
        self.assertFalse(employee.check_pin("1234"))

    def test_user_cannot_change_pin_with_wrong_current_pin(self):
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")

        with self.assertRaises(ValueError):
            employee.change_pin("9999", "5678")

    def test_change_pin_resets_must_change_pin(self):
        employee = Employee(
            1,
            "Max Mitarbeiter",
            "1234",
            "Verkauf",
            must_change_pin=True
        )

        employee.change_pin("1234", "5678")

        self.assertFalse(employee.must_change_pin)

    def test_force_change_pin_does_not_require_current_pin(self):
        employee = Employee(
            1,
            "Max Mitarbeiter",
            "1234",
            "Verkauf",
            must_change_pin=True
        )

        employee.force_change_pin("5678")

        self.assertTrue(employee.check_pin("5678"))
        self.assertFalse(employee.must_change_pin)

    def test_pin_must_have_four_digits(self):
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")

        with self.assertRaises(ValueError):
            employee.change_pin("1234", "12345")

        with self.assertRaises(ValueError):
            employee.change_pin("1234", "abcd")

        with self.assertRaises(ValueError):
            employee.change_pin("1234", "12")


if __name__ == "__main__":
    unittest.main()
