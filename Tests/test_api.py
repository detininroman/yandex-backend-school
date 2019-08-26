import random

import requests

base_url = 'http://0.0.0.0:80'


def test_create_valid():
    citizens = list()
    for i in range(1, 100):
        birth_year = 1950 + i % 50
        citizens.append(
            dict(citizen_id=i,
                 town='Moscow',
                 street='street_name',
                 building='building_name',
                 apartment=10,
                 name='test_name',
                 birth_date=f'03.02.{birth_year}',
                 gender='male',
                 relatives=[]
                 )
        )
    payload = dict(citizens=citizens)

    response = requests.post(url=f'{base_url}/imports', json=payload)
    assert response.status_code == 201
    import_id = response.json()['data']['import_id']

    response = requests.get(url=f'{base_url}/import/{import_id}/citizens')
    assert response.status_code == 200
    assert response.json()['data'] == payload['citizens']


def test_create_invalid_id():
    citizens = list()
    for i in range(1, 4):
        citizens.append(
            dict(citizen_id='WRONG_CITIZEN_ID',  # invalid
                 town='Moscow',
                 street='street_name',
                 building='building_name',
                 apartment=10,
                 name='test_name',
                 birth_date='03.02.1998',
                 gender='male',
                 relatives=[]
                 )
        )
    payload = dict(citizens=citizens)

    response = requests.post(url=f'{base_url}/imports', json=payload)
    assert response.status_code == 400
    assert response.json()['error'] == 'citizen_id name must be int'


def test_create_invalid_name():
    citizens = list()
    for i in range(1, 4):
        citizens.append(
            dict(citizen_id=i,
                 town='Moscow',
                 street='---',  # invalid
                 building='building_name',
                 apartment=10,
                 name='test_name',
                 birth_date='03.02.1998',
                 gender='male',
                 relatives=[]
                 )
        )
    payload = dict(citizens=citizens)

    response = requests.post(url=f'{base_url}/imports', json=payload)
    assert response.status_code == 400
    assert response.json()['error'] == 'street name should contain at least' \
                                       ' one letter or one digit'


def test_create_invalid_relatives():
    citizens = list()
    for i in range(1, 4):
        citizens.append(
            dict(citizen_id=i,
                 town='Moscow',
                 street='street_name',
                 building='building_name',
                 apartment=10,
                 name='test_name',
                 birth_date='03.02.1998',
                 gender='male',
                 relatives=[1]  # invalid
                 )
        )
    payload = dict(citizens=citizens)

    response = requests.post(url=f'{base_url}/imports', json=payload)
    assert response.status_code == 400
    assert response.json()['error'] == 'invalid relatives'


def test_update_valid(created_import):
    response = requests.get(url=f'{base_url}/import/{created_import}/citizens')
    assert response.status_code == 200
    citizen_ids = [item['citizen_id'] for item in response.json()['data']]

    citizen_id = random.choice(citizen_ids)
    response = requests.patch(url=f'{base_url}/imports/'
                                  f'{created_import}/citizens/{citizen_id}',
                              json=dict(name='new_name'))
    assert response.status_code == 200
    assert response.json()['data']['name'] == 'new_name'


def test_update_invalid_birthdate(created_import):
    response = requests.get(url=f'{base_url}/import/{created_import}/citizens')
    assert response.status_code == 200
    citizen_ids = [item['citizen_id'] for item in response.json()['data']]

    citizen_id = random.choice(citizen_ids)
    response = requests.patch(url=f'{base_url}/imports/'
                                  f'{created_import}/citizens/{citizen_id}',
                              json=dict(birth_date='31.02.1998'))
    assert response.status_code == 400
    assert response.json()['error'] == 'birth_date is not valid'


def test_bitrhdays():
    citizens = list()

    may, september = 5, 9

    for i in range(1, 6):
        citizens.append(
            {
                "citizen_id": i,
                "town": "Moscow",
                "street": "123",
                "building": "empty",
                "apartment": 7,
                "name": "name",
                "birth_date": f'26.{may}.1988',
                "gender": "male",
                "relatives": []
            })

    # input data
    citizens[0]['relatives'] = [2, 3, 4]
    citizens[1]['relatives'] = [1]
    citizens[2]['relatives'] = [1]
    citizens[3]['relatives'] = [1]
    # expectable result
    may_info = [
        {'citizen_id': 1, 'presents': len(citizens[0]['relatives'])},
        {'citizen_id': 2, 'presents': len(citizens[1]['relatives'])},
        {'citizen_id': 3, 'presents': len(citizens[2]['relatives'])},
        {'citizen_id': 4, 'presents': len(citizens[3]['relatives'])}]

    # input data
    citizens[4]['relatives'] = [5]
    citizens[4]['birth_date'] = f'26.{september}.1988'
    # expectable result
    september_info = [{'citizen_id': 5, 'presents': 1}]

    payload = dict(citizens=citizens)

    response = requests.post(url=f'{base_url}/imports', json=payload)
    assert response.status_code == 201
    import_id = response.json()['data']['import_id']

    response = requests.get(url=f'{base_url}/imports/{import_id}/citizens/birthdays')
    assert response.status_code == 200

    assert response.json()['data'][str(may)] == may_info
    assert response.json()['data'][str(september)] == september_info
    for month, month_info in response.json()['data'].items():
        if int(month) not in [september, may]:
            assert month_info == []
