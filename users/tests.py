from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from main.email import CustomActivationEmail, CustomPasswordResetEmail


class EmailLoginFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_inactive_user_login_returns_inactive_error(self):
        user = User.objects.create_user(
            username="inactive_case_user",
            email="inactive_case@example.com",
            password="Pass123456!@",
            is_active=False,
        )
        self.assertFalse(user.is_active)

        response = self.client.post(
            "/api/auth/token/login/",
            {"email": user.email, "password": "Pass123456!@"},
            format="json",
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, 400)
        payload = response.json()
        self.assertIn("non_field_errors", payload)
        self.assertIn("未激活", " ".join(payload.get("non_field_errors", [])))
        self.assertIn("inactive_account", "".join(payload.get("code", [])))

    def test_active_user_can_login_with_email(self):
        user = User.objects.create_user(
            username="active_case_user",
            email="active_case@example.com",
            password="Pass123456!@",
            is_active=True,
        )

        response = self.client.post(
            "/api/auth/token/login/",
            {"email": user.email, "password": "Pass123456!@"},
            format="json",
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("auth_token", response.json())

    def test_duplicate_email_login_uses_matching_active_account(self):
        duplicate_email = "duplicate_login@example.com"
        User.objects.create_user(
            username="duplicate_inactive_user",
            email=duplicate_email,
            password="InactivePass123!@",
            is_active=False,
        )
        User.objects.create_user(
            username="duplicate_active_user",
            email=duplicate_email,
            password="ActivePass123!@",
            is_active=True,
        )

        response = self.client.post(
            "/api/auth/token/login/",
            {"email": duplicate_email, "password": "ActivePass123!@"},
            format="json",
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("auth_token", response.json())

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.dummy.EmailBackend")
    def test_duplicate_email_reset_password_is_accepted(self):
        duplicate_email = "duplicate_reset@example.com"
        User.objects.create_user(
            username="duplicate_reset_inactive",
            email=duplicate_email,
            password="InactivePass123!@",
            is_active=False,
        )
        User.objects.create_user(
            username="duplicate_reset_active",
            email=duplicate_email,
            password="ActivePass123!@",
            is_active=True,
        )

        response = self.client.post(
            "/api/auth/users/reset_password/",
            {"email": duplicate_email},
            format="json",
            HTTP_HOST="localhost",
        )

        self.assertEqual(response.status_code, 204)


class ActivationEmailContextTests(TestCase):
    @override_settings(
        FRONTEND_PROTOCOL="https",
        FRONTEND_DOMAIN="www.cyphergamebuy.com",
    )
    def test_activation_email_uses_frontend_domain_and_protocol(self):
        user = User.objects.create_user(
            username="activation_mail_user",
            email="activation_mail@example.com",
            password="Pass123456!@",
        )
        email = CustomActivationEmail(context={"user": user})

        context = email.get_context_data()

        self.assertEqual(context.get("protocol"), "https")
        self.assertEqual(context.get("domain"), "www.cyphergamebuy.com")

    @override_settings(
        FRONTEND_PROTOCOL="https",
        FRONTEND_DOMAIN="www.cyphergamebuy.com",
    )
    def test_password_reset_email_uses_frontend_domain_and_protocol(self):
        user = User.objects.create_user(
            username="password_reset_mail_user",
            email="password_reset_mail@example.com",
            password="Pass123456!@",
        )
        email = CustomPasswordResetEmail(context={"user": user})

        context = email.get_context_data()

        self.assertEqual(context.get("protocol"), "https")
        self.assertEqual(context.get("domain"), "www.cyphergamebuy.com")
