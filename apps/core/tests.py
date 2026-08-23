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
