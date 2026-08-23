from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.farmacias.models import Farmacia, UsuarioFarmacia


class SmokeTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(email="test@example.com", password="TestPassword2026!")
        self.farmacia = Farmacia.objects.create(codigo="TEST", nombre="Farmacia Test")
        UsuarioFarmacia.objects.create(usuario=self.user, farmacia=self.farmacia, rol=UsuarioFarmacia.Rol.ADMIN)

    def test_home_loads(self):
        self.assertEqual(self.client.get("/").status_code, 200)

    def test_login_loads(self):
        self.assertEqual(self.client.get("/accounts/login/").status_code, 200)

    def test_health_api(self):
        response = self.client.get("/api/v1/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_session_api_reports_authentication(self):
        self.assertFalse(self.client.get("/api/v1/auth/session/").json()["authenticated"])
        self.client.force_login(self.user)
        response = self.client.get("/api/v1/auth/session/")
        self.assertTrue(response.json()["authenticated"])
        self.assertEqual(response.json()["user"]["email"], self.user.email)

    def test_logout_api_closes_session(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.post("/api/v1/auth/logout/").status_code, 200)
        self.assertFalse(self.client.get("/api/v1/auth/session/").json()["authenticated"])

    def test_login_api_uses_django_credentials(self):
        self.client.get("/api/v1/auth/session/")
        response = self.client.post(
            "/api/v1/auth/login/",
            {"email": "test@example.com", "password": "TestPassword2026!"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user"]["email"], "test@example.com")

    def test_admin_redirects_anonymous_user(self):
        self.assertEqual(self.client.get("/admin/").status_code, 302)

    def test_private_pages_require_login(self):
        for url in ("/app/dashboard/", "/app/medicamentos/", "/app/inventario/", "/app/lotes/"):
            self.assertEqual(self.client.get(url).status_code, 302)

    def test_authenticated_application_pages_load(self):
        self.client.force_login(self.user)
        for url in ("/", "/app/dashboard/", "/app/medicamentos/", "/app/inventario/", "/app/lotes/"):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)
