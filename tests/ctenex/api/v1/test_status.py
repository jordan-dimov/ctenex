from fastapi.testclient import TestClient

from tests.fixtures import client  # noqa F401


class TestStatusController:
    def setup_method(self):
        self.url = "/status"

    # GET /status

    def test_get_status(
        self,
        client: TestClient,  # noqa F811
    ):
        # test
        response = client.get(
            url=self.url,
        )

        # validation
        payload = response.json()

        assert response.status_code == 200

        assert payload["status"] == "OK"
