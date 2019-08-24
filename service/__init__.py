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
    keys = list(shelf.keys())

    imports = []
    for key in keys:
        imports.append(shelf[key])

    return {'imports': imports}, 200


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

    return {'data': {'import_id': import_id}}, 201


@app.route('/import/<int:import_id>/citizens', methods=['GET'])
def get_import_citizens(import_id: int) -> (dict, int):
    """Gets list of citizens for particular import.

    :param import_id: the ID of import.
    :return: list of citizens and status code.
    """
    shelf = get_db()
    keys = list(shelf.keys())

    for key in keys:
        if shelf[key]['import_id'] == import_id:
            return {'data': shelf[key]['citizens']}, 200

    return error('not found'), 404


@app.route('/imports/<int:import_id>/citizens/<int:citizen_id>', methods=['PATCH'])
def update_citizen(import_id: int, citizen_id: int) -> (dict, int):
    """Updates citizen information.

    :param import_id: the ID of import.
    :param citizen_id: the ID of citizen.
    :return: updated information and status code.
    """
    data = request.get_json()

    # outdated information about all import
    citizens = {}
    # outdated information about citizen
    citizen_info = {}
    # fields that will be updated
    fields_to_update = []

    # find import with citizens
    shelf = get_db()
    for key in list(shelf.keys()):
        if shelf[key]['import_id'] == import_id:
            citizens = shelf[key]['citizens']

    # modify import with citizens
    for citizen in citizens:
        if citizen['citizen_id'] == citizen_id:
            if data.get('citizen_id'):
                return error('citizen_id cannot be changed'), 400

            for field in data.keys():
                if data.get(field):
                    fields_to_update.append(field)
                    citizen[field] = data[field]

            citizen_info = citizen

    invalid_payload = validate_payload(citizens, fields_to_update)
    if invalid_payload:
        return invalid_payload

    payload = {'citizens': citizens,
               'import_id': import_id}

    shelf[str(import_id)] = payload

    return {'data': citizen_info}, 200
