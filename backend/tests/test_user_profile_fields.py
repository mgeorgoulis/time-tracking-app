import unittest

from backend.models.user import Employee


class TestUserProfileFields(unittest.TestCase):

    def test_user_splits_existing_name_into_first_and_last_name(self):
        employee = Employee(1, "Max Mustermann", "1234", "Verkauf")

        self.assertEqual(employee.first_name, "Max")
        self.assertEqual(employee.last_name, "Mustermann")
        self.assertEqual(employee.full_name, "Max Mustermann")

    def test_user_can_be_created_with_separate_profile_fields(self):
        employee = Employee(
            user_id=1,
            first_name="Max",
            last_name="Mustermann",
            pin_code="1234",
            department="Verkauf",
            email="max.mustermann@example.com",
            phone="0123456789",
            street="Musterstraße 1",
            postal_code="12345",
            city="Musterstadt",
            country="Deutschland"
        )

        self.assertEqual(employee.full_name, "Max Mustermann")
        self.assertEqual(employee.name, "Max Mustermann")
        self.assertEqual(employee.email, "max.mustermann@example.com")
        self.assertEqual(employee.phone, "0123456789")
        self.assertEqual(employee.street, "Musterstraße 1")
        self.assertEqual(employee.postal_code, "12345")
        self.assertEqual(employee.city, "Musterstadt")
        self.assertEqual(employee.country, "Deutschland")

    def test_user_without_last_name_still_has_full_name(self):
        employee = Employee(1, "Max", "1234", "Verkauf")

        self.assertEqual(employee.first_name, "Max")
        self.assertEqual(employee.last_name, "")
        self.assertEqual(employee.full_name, "Max")


if __name__ == "__main__":
    unittest.main()
