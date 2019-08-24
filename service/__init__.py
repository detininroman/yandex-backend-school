import shelve

from flask import Flask, g, request

from service.tools import error, contains_digit, contains_letter, \
    validate_payload as is_payload_invalid, debug

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
def get_all_imports():
    shelf = get_db()
    keys = list(shelf.keys())

    imports = []
    for key in keys:
        imports.append(shelf[key])

    return {'imports': imports}, 200


@app.route('/imports', methods=['POST'])
def post_import():
    data = request.get_json()

    invalid_payload = is_payload_invalid(data['citizens'])

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
def get_import_citizens(import_id):
    shelf = get_db()
    keys = list(shelf.keys())

    for key in keys:
        if shelf[key]['import_id'] == import_id:
            return {'data': shelf[key]['citizens']}, 200

    return error('not found'), 404


@app.route('/imports/<int:import_id>/citizens/<int:citizen_id>', methods=['PATCH'])
def update_citizen(import_id, citizen_id):
    data = request.get_json()

    # outdated information about import
    import_info = {}
    # outdated information about citizen
    citizen_info = {}

    shelf = get_db()
    for key in list(shelf.keys()):
        if shelf[key]['import_id'] == import_id:
            import_info = shelf[key]['citizens']
            for citizen in import_info:
                if citizen['citizen_id'] == citizen_id:
                    citizen_info = citizen

    citizen_info['town'] = data['town']
    for citizen in import_info:
        if citizen['citizen_id'] == citizen_id:
            citizen['town'] = citizen_info['town']

    payload = {'citizens': import_info,
               'import_id': import_id}

    shelf[str(import_id)] = payload

    return {'data': citizen_info}, 200
