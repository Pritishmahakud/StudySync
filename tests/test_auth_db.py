"""
Unit tests for Database and Authentication Security.
"""

import sys
from pathlib import Path
root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

import unittest
from shared.auth import authenticate_user, register_user
from shared.database import get_db_connection, hash_password, verify_password


class TestAuthAndDatabase(unittest.TestCase):
    def test_password_hashing_and_verification(self):
        pw = "SecurePass@2026"
        pw_hash, salt = hash_password(pw)
        self.assertNotEqual(pw, pw_hash)
        self.assertEqual(len(pw_hash), 64)
        self.assertTrue(verify_password(pw, pw_hash, salt))
        self.assertFalse(verify_password("WrongPassword", pw_hash, salt))

    def test_default_asha_user_seeded(self):
        ok, msg, user = authenticate_user("asha@studysync.edu", "Password@123")
        self.assertTrue(ok)
        self.assertIsNotNone(user)
        self.assertEqual(user["email"], "asha@studysync.edu")
        self.assertEqual(user["name"], "Asha Sharma")

    def test_invalid_login(self):
        ok, msg, user = authenticate_user("asha@studysync.edu", "IncorrectPw")
        self.assertFalse(ok)
        self.assertIn("Incorrect password", msg)

    def test_register_and_login_new_user(self):
        import uuid
        test_email = f"user_{uuid.uuid4().hex[:6]}@college.edu"
        ok, msg, user = register_user(test_email, "TestPassword123", "Test Student")
        self.assertTrue(ok)
        self.assertEqual(user["email"], test_email)

        # Now authenticate
        ok_login, _, login_user = authenticate_user(test_email, "TestPassword123")
        self.assertTrue(ok_login)
        self.assertEqual(login_user["name"], "Test Student")

    def test_reject_short_password(self):
        ok, msg, _ = register_user("short@test.com", "123", "Short User")
        self.assertFalse(ok)
        self.assertIn("at least 6 characters", msg)

    def test_reject_invalid_email(self):
        ok, msg, _ = register_user("notanemail", "ValidPassword123", "Bad Email User")
        self.assertFalse(ok)
        self.assertIn("valid email", msg)


if __name__ == "__main__":
    unittest.main()
