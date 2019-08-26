import pytest
import requests

from service import base_url
from service.tools import create_default_citizen


@pytest.fixture
def created_import():
    citizens = [create_default_citizen(citizen_id=i) for i in range(1, 6)]
    payload = {'citizens': citizens}

    response = requests.post(url=f'{base_url}/imports', json=payload)
    assert response.status_code == 201
    yield response.json()['data']['import_id']
