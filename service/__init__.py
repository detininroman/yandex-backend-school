import shelve

from flask import Flask, g, request
from flask_restful import Resource, Api

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
        print(shelf, flush=True)
        keys = list(shelf.keys())

        imports = []

        for key in keys:
            imports.append(shelf[key])

        return {'imports': imports}, 200

    def post(self):
        data = request.get_json()

        print(data, flush=True)

        shelf = get_db()
        shelf[str(data['citizen_id'])] = data

        import_id = 1

        return {'data': {'import_id': import_id}}, 201


api.add_resource(ImportList, '/imports')
