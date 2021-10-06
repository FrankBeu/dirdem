from dirdem import __version__, app
import re
import dirdem.application as dirdem

def test_version():
    assert __version__ == '0.0.0'

def test_homepage():
    tester = app.test_client()
    response = tester.get("/", content_type="html/text")

    assert response.status_code == 200
    assert re.search(dirdem.APP_TITLE, response.data.decode('UTF-8'))


