import requests

base_url = 'http://0.0.0.0:80'


def test_valid_create():
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


def test_invalid_create():
    citizens = list()
    for i in range(1, 4):
        citizens.append(
            dict(citizen_id="WRONG_CITIZEN_ID",
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
