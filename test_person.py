import unittest
from io import StringIO
from unittest.mock import patch

from Person import Person, Manager, Employee


def capture(obj):
    with patch("sys.stdout", new=StringIO()) as out:
        obj.printInfo()
    return out.getvalue()


class TestPerson(unittest.TestCase):
    def test_person_attributes(self):
        p = Person(1, "Kim")
        self.assertEqual((p.id, p.name), (1, "Kim"))

    def test_person_print_info(self):
        self.assertEqual(capture(Person(1, "Kim")), "ID: 1, Name: Kim\n")

    def test_manager_is_person(self):
        self.assertIsInstance(Manager(2, "Lee", "CEO"), Person)

    def test_manager_attributes(self):
        m = Manager(2, "Lee", "CEO")
        self.assertEqual((m.id, m.name, m.title), (2, "Lee", "CEO"))

    def test_manager_print_info(self):
        self.assertEqual(capture(Manager(2, "Lee", "CEO")),
                         "ID: 2, Name: Lee\nTitle: CEO\n")

    def test_employee_is_person(self):
        self.assertIsInstance(Employee(3, "Park", "Python"), Person)

    def test_employee_attributes(self):
        e = Employee(3, "Park", "Python")
        self.assertEqual((e.id, e.name, e.skill), (3, "Park", "Python"))

    def test_employee_print_info(self):
        self.assertEqual(capture(Employee(3, "Park", "Python")),
                         "ID: 3, Name: Park\nSkill: Python\n")

    def test_employee_has_no_title(self):
        self.assertFalse(hasattr(Employee(3, "Park", "Python"), "title"))

    def test_manager_has_no_skill(self):
        self.assertFalse(hasattr(Manager(2, "Lee", "CEO"), "skill"))


if __name__ == "__main__":
    unittest.main()
