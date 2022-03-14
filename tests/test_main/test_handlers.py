from flask import url_for

from tests.test_main import MainTestCase


class MainIndexTestCase(MainTestCase):
    """Test GET on main index route."""
    def test_get_index(self):
        response = self.client.get(url_for("main.index"))
        self.assert_200(response)


# class MainAboutTestCase(MainTestCase):
#     """Test GET on main about route."""
#     def test_get_about(self):
#         response = self.client.get(url_for("main.about"))
#         self.assert_200(response)
#         self.assertIn(b"Each recommendation round has three phases", response.data)
