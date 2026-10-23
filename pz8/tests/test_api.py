import unittest

from fastapi.testclient import TestClient

from planner.main import app
from planner.models.events import Event
from planner.models.users import NewUser, User
from planner.routes.events import events
from planner.routes.users import users


class PlannerTests(unittest.TestCase):
    def setUp(self):
        users.clear()
        events.clear()
        self.client = TestClient(app)
        self.addCleanup(self.client.close)
        self.user = {"email": "fastapi@packt.com", "password": "Stro0ng!"}
        self.event = {
            "id": 1,
            "title": "FastAPI Book Launch",
            "image": "https://linktomyimage.com/image.png",
            "description": "Обсуждение книги FastAPI",
            "tags": ["python", "fastapi"],
            "location": "Google Meet",
        }

    def test_registration_and_signin(self):
        response = self.client.post("/user/signup", json=self.user)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("password", response.json())
        self.assertEqual(self.client.post("/user/signin", json=self.user).status_code, 200)
        self.assertEqual(self.client.post("/user/signup", json=self.user).status_code, 409)
        wrong_password = dict(self.user, password="incorrect")
        self.assertEqual(self.client.post("/user/signin", json=wrong_password).status_code, 403)

    def test_unknown_user_and_validation(self):
        self.assertEqual(self.client.post("/user/signin", json=self.user).status_code, 404)
        for payload in ({"email": "invalid", "password": "x"}, {"email": self.user["email"]}):
            with self.subTest(payload=payload):
                self.assertEqual(self.client.post("/user/signup", json=payload).status_code, 422)

    def test_event_lifecycle(self):
        self.assertEqual(self.client.get("/event/").json(), [])
        self.assertEqual(self.client.post("/event/new", json=self.event).status_code, 200)
        self.assertEqual(self.client.get("/event/1").json(), self.event)
        self.assertEqual(self.client.get("/event/").json(), [self.event])
        self.assertEqual(self.client.post("/event/new", json=self.event).status_code, 409)
        self.assertEqual(self.client.delete("/event/1").status_code, 200)
        self.assertEqual(self.client.get("/event/1").status_code, 404)
        self.assertEqual(self.client.delete("/event/1").status_code, 404)

    def test_clear_multiple_events(self):
        for event_id in (1, 2):
            self.assertEqual(
                self.client.post("/event/new", json=dict(self.event, id=event_id)).status_code,
                200,
            )
        self.assertEqual(self.client.delete("/event/").status_code, 200)
        self.assertEqual(self.client.get("/event/").json(), [])
        self.assertEqual(self.client.delete("/event/").status_code, 200)

    def test_invalid_events(self):
        for payload in ({}, dict(self.event, id=0), dict(self.event, tags="python")):
            with self.subTest(payload=payload):
                self.assertEqual(self.client.post("/event/new", json=payload).status_code, 422)
        self.assertEqual(self.client.get("/event/not-an-id").status_code, 422)
        self.assertEqual(self.client.get("/event/").json(), [])

    def test_user_model_defaults_and_public_fields(self):
        first = NewUser(**self.user)
        second = NewUser(email="second@packt.com", password="secret")
        first.events.append(Event(**self.event))
        self.assertEqual(second.events, [])
        public = User.model_validate(first.model_dump()).model_dump()
        self.assertNotIn("password", public)

    def test_docs(self):
        self.assertEqual(self.client.get("/docs").status_code, 200)
        schema = self.client.get("/openapi.json").json()
        self.assertIn("/user/signup", schema["paths"])
        self.assertIn("/event/{id}", schema["paths"])
        self.assertEqual(self.client.get("/", follow_redirects=False).headers["location"], "/docs")


if __name__ == "__main__":
    unittest.main()
