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


def error(arg):
    return {'error': arg}


def contains_digit(string):
    return any(char.isdigit() for char in string)


def contains_letter(string):
    return any(char.isalpha() for char in string)


def is_payload_invalid(citizens):
    identifiers = list()
    for citizen in citizens:

        # check if all fields are present
        if len(citizen.keys()) != 9:
            return error('all fields must be filled'), 400

        # check if all fields are not empty
        for (key, value) in citizen.items():
            if value is None:
                return error(f'{key} must be specified'), 400

        # validating citizen_id
        identifiers.append(citizen['citizen_id'])
        if citizen['citizen_id'] < 0:
            return error('Citizen ID cannot be negative'), 400

        # validating town
        town = citizen['town']
        if len(town) >= 256:
            return error('Town name should not exceed 256 characters'), 400
        if not (contains_digit(town) or contains_letter(town)):
            return error('Town name should contain at least one letter or one digit'), 400

        # validating street
        street = citizen['street']
        if len(street) >= 256:
            return error('Street name should not exceed 256 characters'), 400
        if not (contains_digit(street) or contains_letter(street)):
            return error('Street name should contain at least one letter or one digit'), 400

        # validating building
        building = citizen['building']
        if len(building) >= 256:
            return error('Building name should not exceed 256 characters'), 400
        if not (contains_digit(street) or contains_letter(street)):
            return error('Building name should contain at least one letter or one digit'), 400

        # validating apartment
        if citizen['apartment'] < 0:
            return error('Apartment number cannot be negative'), 400

        # validating name
        name = citizen['name']
        if not len(name) or len(name) >= 256:
            return error('Name should not be empty and exceed 256 characters'), 400

        # validating birth_date
        try:
            birth_date = datetime.strptime(citizen['birth_date'], '%d.%m.%Y')
            if birth_date >= datetime.now():
                return error(f'Birth date `{birth_date}` is not valid'), 400
        except ValueError:
            return error('Birth date is not valid'), 400

        # validating gender
        if citizen['gender'] not in ['male', 'female']:
            return error('Invalid gender'), 400

        # validating relatives
        if not isinstance(citizen['relatives'], list):
            return error('Relatives field must be list'), 400

        for relative in citizen['relatives']:
            if not isinstance(relative, int):
                return error('Relative must be int'), 400

    # validate uniqueness
    if not len(set(identifiers)) == len(identifiers):
        return error('Identifiers are not unique'), 400

    return


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


api.add_resource(ImportList, '/imports')
