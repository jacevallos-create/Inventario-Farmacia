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

    def test_allauth_does_not_expect_a_username_field(self):
        from allauth.account import app_settings

        self.assertIsNone(app_settings.USER_MODEL_USERNAME_FIELD)
        self.assertEqual(app_settings.USERNAME_VALIDATORS, [])

    def test_admin_can_persist_and_read_system_state(self):
        self.user.is_staff = True
        self.user.save(update_fields=["is_staff"])
        self.client.force_login(self.user)
        payload = {
            "branches": [{"id": "central", "name": "Farmacia Central", "address": "Centro", "active": True}],
            "inventories": {"central": [{
                "id": 1, "name": "Paracetamol 500 mg", "sku": "MED-API-1", "barcode": "",
                "category": "Analgésicos", "lab": "Laboratorio Test", "presentation": "Tabletas",
                "stock": 25, "min": 5, "sellPrice": 3.5,
            }]},
            "suppliers": [], "sales": [], "users": [],
        }
        response = self.client.put("/api/v1/state/", payload, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["inventories"]["central"][0]["stock"], 25)
        medicine_id = response.json()["inventories"]["central"][0]["id"]
        delete_response = self.client.delete(f"/api/v1/state/inventory/{medicine_id}/?branch=central")
        self.assertEqual(delete_response.status_code, 204)
        self.assertEqual(self.client.get("/api/v1/state/").json()["inventories"]["central"], [])
        self.assertEqual(self.client.get("/api/v1/state/").status_code, 200)

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
