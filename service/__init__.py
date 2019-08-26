from datetime import datetime

from flask import Flask
from flask import g
from flask import request
from sqlitedict import SqliteDict

from service import tools

app = Flask(__name__)

host = '0.0.0.0'
port = 80
base_url = f'http://{host}:{port}'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = SqliteDict('./my_db.sqlite', autocommit=True)
    return db


@app.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# Task 0 (not required)
@app.route('/imports', methods=['GET'])
def get_all_imports() -> (dict, int):
    """Gets all imports.

    :return: imports and status code.
    """
    database = get_db()
    return {'imports': list(database.values())}, 200


# Task 1
@app.route('/imports', methods=['POST'])
def create_import() -> (dict, int):
    """Creates a new import.

    :return: import identifier and status code
    """
    data = request.get_json()
    if not data:
        return tools.error('invalid json'), 400

    invalid_payload = tools.validate_payload(data['citizens'])
    if invalid_payload:
        return invalid_payload

    database = get_db()

    try:
        import_id = int(list(database.keys())[-1]) + 1
    except IndexError:
        import_id = 1
    data['import_id'] = import_id
    database[import_id] = data
    return {'data': {'import_id': import_id}}, 201


# Task 2
@app.route(
    '/imports/<int:import_id>/citizens/<int:citizen_id>', methods=['PATCH'])
def update_citizen(import_id: int, citizen_id: int) -> (dict, int):
    """Updates citizen information.

    :param import_id: the ID of import.
    :param citizen_id: the ID of citizen.
    :return: updated information and status code.
    """
    data = request.get_json()
    if not data:
        return tools.error('invalid json'), 400

    database = get_db()

    # find import to update
    try:
        citizens = database[import_id]['citizens']
    except KeyError:
        return tools.error(f'import {import_id} not found'), 400

    # find particular citizen and its index
    try:
        citizen = [citizen for citizen in citizens
                   if citizen['citizen_id'] == citizen_id][0]
        index = citizens.index(citizen)
    except IndexError:
        return tools.error(f'invalid citizen_id: {citizen_id}'), 400

    # forbid citizen_id changing
    if data.get('citizen_id'):
        return tools.error('citizen_id cannot be changed'), 400

    fields_to_update = []
    new_relatives, old_relatives = [], []

    for field in data.keys():
        # if relatives are changed
        if data.get('relatives') is not None and \
                isinstance(data.get('relatives'), list):
            old_relatives = citizen['relatives']
            new_relatives = data['relatives']
            if not len(new_relatives) == len(set(new_relatives)):
                return tools.error('invalid relatives'), 400

        if data.get(field) is not None:
            fields_to_update.append(field)
            citizen[field] = data[field]

    # apply changes to citizen
    citizens[index] = citizen

    # modify relatives
    for relative in list(set(old_relatives + new_relatives)):
        if relative in new_relatives and relative in old_relatives:
            pass
        elif relative in new_relatives and relative not in old_relatives:
            new_relative = [item for item in citizens
                            if item['citizen_id'] == relative][0]
            index = citizens.index(new_relative)
            if citizen_id not in new_relative['relatives']:
                new_relative['relatives'].append(citizen_id)
            debug(new_relative['relatives'])
            citizens[index] = new_relative
        elif relative in old_relatives and relative not in new_relatives:
            old_relative = [item for item in citizens
                            if item['citizen_id'] == relative][0]
            index = citizens.index(old_relative)
            if citizen_id in old_relative['relatives']:
                old_relative['relatives'].remove(citizen_id)
            citizens[index] = old_relative

    invalid_payload = tools.validate_payload(citizens, fields_to_update)
    if invalid_payload:
        return invalid_payload

    database[import_id] = {
        'citizens': citizens,
        'import_id': import_id
    }

    return {'data': citizen}, 200


# Task 3
@app.route('/imports/<int:import_id>/citizens', methods=['GET'])
def get_citizens(import_id: int) -> (dict, int):
    """Gets list of citizens for particular import.

    :param import_id: the ID of import.
    :return: list of citizens and status code.
    """
    database = get_db()

    try:
        return {'data': database[import_id]['citizens']}, 200
    except KeyError:
        return tools.error(f'import {import_id} not found'), 400


# Task 4
@app.route('/imports/<int:import_id>/citizens/birthdays', methods=['GET'])
def get_birthdays(import_id):
    database = get_db()

    # get list of citizens for particular import
    try:
        citizens = database[import_id]['citizens']
    except KeyError:
        return tools.error(f'import {import_id} not found'), 400

    # create dictionary for output
    months = {key: [] for key in range(1, 12 + 1)}

    for citizen in citizens:
        for relative in citizen['relatives']:
            # recipient is person who receives the gift
            recipient = [item for item in citizens if
                         item['citizen_id'] == relative][0]
            birthday = datetime.strptime(recipient['birth_date'], '%d.%m.%Y')
            # giver is person who gives a gift
            try:
                # if dict for a particular giver already exists
                giver = [item for item in months[birthday.month] if
                         item['citizen_id'] == citizen['citizen_id']][0]
                giver['presents'] += 1
            except IndexError:
                # create dict for a particular giver
                giver = {
                    'citizen_id': citizen['citizen_id'],
                    'presents': 1
                }
                months[birthday.month].append(giver)

    return {'data': months}, 200


# Task 5
@app.route(
    '/imports/<int:import_id>/towns/stat/percentile/age', methods=['GET'])
def get_statistics(import_id):
    database = get_db()

    # get list of citizens for particular import
    try:
        citizens = database[import_id]['citizens']
    except KeyError:
        return tools.error(f'import {import_id} not found'), 400

    # create list of all towns from import
    towns = list(set([citizen['town'] for citizen in citizens]))
    # create dict for every town
    data = [
        {
            'town': town,
            'ages': []
        } for town in towns
    ]

    for citizen in citizens:
        # calculate age
        try:
            birth_date = datetime.strptime(citizen['birth_date'], '%d.%m.%Y')
            age = tools.calculate_age(birth_date)
        except ValueError:
            return tools.error('birth_date is not valid'), 400

        # get dict for particular town
        town_statistics = [item for item in data if
                           item['town'] == citizen['town']][0]
        index = data.index(town_statistics)
        # add age
        town_statistics['ages'].append(age)
        # apply changes
        data[index] = town_statistics

    # count percentiles
    for town_statistics in data:
        ages = town_statistics.pop('ages')
        for percent in [50, 75, 99]:
            town_statistics[f'p{percent}'] = tools.percentile(ages, percent)

    return {'data': data}, 200
