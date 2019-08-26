import random
from datetime import datetime

import numpy as np
import requests

from service import base_url
from service import tools
from service.tools import create_default_citizen


def test_create_valid():
    citizens = []
    for i in range(1, 100):
        birth_year = 1950 + i % 50
        citizen = create_default_citizen(
            citizen_id=i,
            birth_date=f'03.02.{birth_year}'
        )
        citizens.append(citizen)
    payload = {'citizens': citizens}

    response = requests.post(url=f'{base_url}/imports', json=payload)
    assert response.status_code == 201
    import_id = response.json()['data']['import_id']

    response = requests.get(url=f'{base_url}/imports/{import_id}/citizens')
    assert response.status_code == 200
    assert response.json()['data'] == payload['citizens']


def test_create_invalid_id():
    citizens = [create_default_citizen(citizen_id=-1)]
    payload = {'citizens': citizens}

    response = requests.post(url=f'{base_url}/imports', json=payload)
    assert response.status_code == 400
    assert response.json()['error'] == 'citizen_id cannot be negative'


def test_create_invalid_street():
    citizens = [create_default_citizen(citizen_id=1, street='---')]
    payload = {'citizens': citizens}

    response = requests.post(url=f'{base_url}/imports', json=payload)
    assert response.status_code == 400
    assert response.json()['error'] == 'street name should contain at least' \
                                       ' one letter or one digit'


def test_create_invalid_relatives():
    citizens = [create_default_citizen(
        citizen_id=i,
        relatives=[1]
    ) for i in range(1, 4)]
    payload = {'citizens': citizens}

    response = requests.post(url=f'{base_url}/imports', json=payload)
    assert response.status_code == 400
    assert response.json()['error'] == 'invalid relatives'


def test_update_valid(created_import):
    response = requests.get(
        url=f'{base_url}/imports/{created_import}/citizens')
    assert response.status_code == 200
    citizen_ids = [item['citizen_id'] for item in response.json()['data']]

    citizen_id = random.choice(citizen_ids)
    response = requests.patch(
        url=f'{base_url}/imports/{created_import}/citizens/{citizen_id}',
        json={'name': 'new_name'})
    assert response.status_code == 200
    assert response.json()['data']['name'] == 'new_name'


def test_update_invalid_birthdate(created_import):
    response = requests.get(
        url=f'{base_url}/imports/{created_import}/citizens')
    assert response.status_code == 200
    citizen_ids = [item['citizen_id'] for item in response.json()['data']]

    citizen_id = random.choice(citizen_ids)
    response = requests.patch(
        url=f'{base_url}/imports/{created_import}/citizens/{citizen_id}',
        json={'birth_date': '31.02.1998'})
    assert response.status_code == 400
    assert response.json()['error'] == 'birth_date is not valid'


def test_bitrhdays():
    may, september = 5, 9
    citizens = [create_default_citizen(
        citizen_id=i,
        birth_date=f'26.{may}.1988'
    ) for i in range(1, 6)]

    # input data
    actor = 1
    citizens[actor - 1]['relatives'] += [2, 3, 4]
    for relative in citizens[actor - 1]['relatives']:
        citizens[relative - 1]['relatives'] = [actor]
    # expected result
    may_info = [dict(citizen_id=i,
                     presents=len(citizens[i - 1]['relatives'])
                     ) for i in range(1, 5)]

    # input data
    actor = 5
    citizens[actor - 1]['relatives'] += [actor]
    citizens[actor - 1]['birth_date'] = f'26.{september}.1988'
    # expected result
    september_info = [dict(citizen_id=actor,
                           presents=len(citizens[actor - 1]['relatives']))]

    payload = {'citizens': citizens}

    response = requests.post(url=f'{base_url}/imports', json=payload)
    assert response.status_code == 201
    import_id = response.json()['data']['import_id']

    response = requests.get(
        url=f'{base_url}/imports/{import_id}/citizens/birthdays')
    assert response.status_code == 200

    assert response.json()['data'][str(may)] == may_info
    assert response.json()['data'][str(september)] == september_info
    for month, month_info in response.json()['data'].items():
        if int(month) not in [september, may]:
            assert month_info == []


def test_statistics():
    citizens, ages = [], {}
    towns = ['Moscow', 'London', 'Paris', 'New-York']
    for i in range(1, 2000):
        year = 1940 + random.randint(0, 60)
        birth_date = f'05.04.{year}'
        town = towns[i % len(towns)]

        citizen = create_default_citizen(
            citizen_id=i,
            birth_date=birth_date,
            town=town
        )
        citizens.append(citizen)

        birth_date = datetime.strptime(citizen['birth_date'], '%d.%m.%Y')
        age = tools.calculate_age(birth_date)
        ages[town] = ages[town] + [age] if town in ages.keys() else [age]

    payload = {'citizens': citizens}
    response = requests.post(url=f'{base_url}/imports', json=payload)
    assert response.status_code == 201
    import_id = response.json()['data']['import_id']

    response = requests.get(
        url=f'{base_url}/imports/{import_id}/towns/stat/percentile/age')
    assert response.status_code == 200

    expected_data = []
    for (key, value) in ages.items():
        ages_for_town = np.array(value)
        town_info = {'town': key}
        for percent in [50, 75, 99]:
            town_info[f'p{percent}'] = \
                round(np.percentile(ages_for_town, percent), 2)
        expected_data.append(town_info)

    statistics = response.json()['data']
    for town in towns:
        d1 = [d for d in statistics if d['town'] == town][0]
        d2 = [d for d in expected_data if d['town'] == town][0]
        assert d1 == d2
