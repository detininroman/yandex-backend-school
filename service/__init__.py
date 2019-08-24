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
    keys = list(shelf.keys())

    for key in keys:
        if shelf[key]['import_id'] == import_id:
            return dict(data=shelf[key]['citizens']), 200

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
    # fields that will be updated
    fields_to_update = []

    # find import with citizens
    shelf = get_db()
    for key in list(shelf.keys()):
        if shelf[key]['import_id'] == import_id:
            citizens = shelf[key]['citizens']

    new_relatives, old_relatives = [], []

    # find citizen and its index
    citizen = [citizen for citizen in citizens if citizen['citizen_id'] == citizen_id][0]
    index = citizens.index(citizen)

    # forbid citizen_id changing
    if data.get('citizen_id'):
        return error('citizen_id cannot be changed'), 400

    for field in data.keys():
        # if relatives are changed
        if isinstance(data.get('relatives'), list):
            old_relatives = citizen['relatives']
            new_relatives = data['relatives']

        # change fields mentioned in data
        if data.get(field):
            fields_to_update.append(field)
            citizen[field] = data[field]

    # modify import with citizens

    # modify relatives
    # all_relatives = list(set(old_relatives + new_relatives))
    # debug(type(citizens))

    # for re
    # for relative in all_relatives:
    #     for citizen in citizens:
    #         if citizen['citizen_id'] in all_relatives:
    #             if citizen['citizen_id'] in new_relatives and citizen['citizen_id'] in old_relatives:
    #                 debug('relative was not changed')
    #             if citizen['citizen_id'] in new_relatives and citizen['citizen_id'] not in old_relatives:
    #                 debug(f'relative {citizen["citizen_id"]} was added')
    #             if citizen['citizen_id'] in old_relatives and citizen['citizen_id'] not in new_relatives:
    #                 debug(f'relative {citizen["citizen_id"]} was deleted')

    citizens[index] = citizen

    invalid_payload = validate_payload(citizens, fields_to_update)
    if invalid_payload:
        return invalid_payload

    shelf[str(import_id)] = dict(
        citizens=citizens,
        import_id=import_id
    )

    return dict(data=citizen), 200
