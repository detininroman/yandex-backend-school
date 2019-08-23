import shelve

from flask import Flask, g, request
from flask_restful import Resource, Api
from datetime import datetime

app = Flask(__name__)
api = Api(app)


def debug(arg):
    return print(arg, flush=True)


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
        print(shelf, flush=True)
        keys = list(shelf.keys())

        imports = []

        for key in keys:
            print(shelf[key])
            imports.append(shelf[key])

        return {'imports': imports}, 200

    def post(self):
        data = request.get_json()

        citizens = data['citizens']

        identifiers = list()

        for citizen in citizens:
            identifiers.append(citizen['citizen_id'])
            try:
                birth_date = datetime.strptime(citizen['birth_date'], '%d.%m.%Y')
                if birth_date >= datetime.now():
                    return {'Error': f'Birth date `{birth_date}` is not valid'}, 400
            except ValueError:
                return {'Error': 'Date is not valid'}, 400

        if not len(set(identifiers)) == len(identifiers):
            return {'Error': 'Identifiers are not unique'}, 400

        shelf = get_db()

        # FIXME:
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

        return {'data': {'import_id': import_id}, 'tmp': data}, 201


api.add_resource(ImportList, '/imports')
