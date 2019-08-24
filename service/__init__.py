import shelve

from flask import Flask, g, request

from service.tools import error, contains_digit, contains_letter, \
    validate_payload, debug

app = Flask(__name__)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = shelve.open("devices.db")
    return db


@app.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/imports', methods=['GET'])
def get_all_imports() -> (dict, int):
    """Gets all imports.

    :return: imports and status code.
    """
    shelf = get_db()

    imports = [shelf[key] for key in list(shelf.keys())]
    return dict(imports=imports), 200


@app.route('/imports', methods=['POST'])
def post_import() -> (dict, int):
    """Creates a new import.

    :return: import identifier and status code
    """
    data = request.get_json()

    invalid_payload = validate_payload(data['citizens'])
    if invalid_payload:
        return invalid_payload

    shelf = get_db()

    # TODO: refactor it
    keys = list(shelf.keys())
    keysint = [int(i) for i in keys]
    keysint.sort()
    keys = [str(i) for i in keysint]

    try:
        import_id = dict(shelf[keys[-1]])['import_id'] + 1
    except IndexError:
        import_id = 1

    data['import_id'] = import_id
    shelf[str(import_id)] = data

    return dict(data=dict(import_id=import_id)), 201


@app.route('/import/<int:import_id>/citizens', methods=['GET'])
def get_import_citizens(import_id: int) -> (dict, int):
    """Gets list of citizens for particular import.

    :param import_id: the ID of import.
    :return: list of citizens and status code.
    """
    shelf = get_db()

    try:
        citizens = [shelf[key]['citizens'] for key in list(shelf.keys())
                    if shelf[key]['import_id'] == import_id][0]
        return dict(data=citizens)
    except IndexError:
        return error('not found'), 404


@app.route(
    '/imports/<int:import_id>/citizens/<int:citizen_id>', methods=['PATCH'])
def update_citizen(import_id: int, citizen_id: int) -> (dict, int):
    """Updates citizen information.

    :param import_id: the ID of import.
    :param citizen_id: the ID of citizen.
    :return: updated information and status code.
    """
    data = request.get_json()

    shelf = get_db()

    # information about all citizens in  import to update
    citizens = [shelf[key]['citizens'] for key in list(shelf.keys())
                if shelf[key]['import_id'] == import_id][0]

    # find particular citizen and its index
    citizen = [citizen for citizen in citizens
               if citizen['citizen_id'] == citizen_id][0]
    index = citizens.index(citizen)

    # forbid citizen_id changing
    if data.get('citizen_id'):
        return error('citizen_id cannot be changed'), 400

    # fields that will be updated
    fields_to_update = list()
    new_relatives, old_relatives = list(), list()

    for field in data.keys():
        # if relatives are changed
        if data.get('relatives') is not None and \
                isinstance(data.get('relatives'), list):
            old_relatives = citizen['relatives']
            new_relatives = data['relatives']

        # if other fields are changed
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
            rel = [item for item in citizens
                   if item['citizen_id'] == relative][0]
            index = citizens.index(rel)
            rel['relatives'].append(citizen_id)
            citizens[index] = rel
        elif relative in old_relatives and relative not in new_relatives:
            rel = [item for item in citizens
                   if item['citizen_id'] == relative][0]
            index = citizens.index(rel)
            rel['relatives'].remove(citizen_id)
            citizens[index] = rel

    invalid_payload = validate_payload(citizens, fields_to_update)
    if invalid_payload:
        return invalid_payload

    shelf[str(import_id)] = dict(
        citizens=citizens,
        import_id=import_id
    )

    return dict(data=citizen), 200


@app.route('/imports/<int:import_id>/citizens/birthdays', methods=['GET'])
def get_birthdays(import_id):
    shelf = get_db()

    citizens = None

    try:
        citizens = [shelf[key]['citizens'] for key in list(shelf.keys())
                    if shelf[key]['import_id'] == import_id][0]
    except IndexError:
        return error('not found'), 404

    months = dict()
    for i in range(1, 12 + 1):
        months[i] = {}

    ret_data = dict(data=months)
    return ret_data, 200
