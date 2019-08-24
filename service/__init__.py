import shelve

from flask import Flask, g, request
from flask_restful import Resource, Api

from service.tools import error, contains_digit, contains_letter, \
    validate_payload as is_payload_invalid, debug

app = Flask(__name__)
api = Api(app)


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


class ImportList(Resource):
    def get(self):
        shelf = get_db()
        keys = list(shelf.keys())

        imports = []
        for key in keys:
            imports.append(shelf[key])

        return {'imports': imports}, 200

    def post(self):
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


class Import(Resource):
    def get(self, import_id):
        shelf = get_db()
        keys = list(shelf.keys())

        for key in keys:
            if shelf[key]['import_id'] == import_id:
                return {'data': shelf[key]['citizens']}, 200

        return error('not found'), 404


api.add_resource(ImportList, '/imports')
api.add_resource(Import, '/import/<int:import_id>/citizens')
