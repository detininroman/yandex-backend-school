from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask('__name__')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://roman:123456@localhost:9000/database01'
db = SQLAlchemy(app)


class Citizen(db.Model):
    citizen_id = db.Column(db.Integer, primary_key=True)
    town = db.Column(db.String(256), unique=False)
    street = db.Column(db.String(256), unique=False)
    building = db.Column(db.String(256), unique=False)
    apartment = db.Column(db.Integer, unique=False)
    name = db.Column(db.String(256), unique=False)
    birth_date = db.Column(db.Date, unique=False)
    gender = db.Column(db.String(256), unique=False)
    relatives = db.Column(db.PickleType, unique=False)

    def __init__(self, citizen_id, town, street, building, apartment, name, birth_date, gender, relatives):
        self.citizen_id = citizen_id
        self.town = town
        self.street = street
        self.building = building
        self.apartment = apartment
        self.name = name
        self.birth_date = birth_date
        self.gender = gender
        self.relatives = relatives


def validate_data(data):
    for (key, value) in data.items():
        if value is None:
            return {'Error': f'`{key}` field is not specified'}
    return None


def validate_birth_date(birth_date):
    if birth_date >= datetime.now():
        return dict(error=f'Birth date `{birth_date}`  is not valid')
    return None


@app.route('/imports', methods=['POST'])
def insert_citizens():
    for citizen_info in request.json['citizens']:

        error_message = validate_data(citizen_info)
        if error_message:
            return jsonify(error_message), 400

        citizen_id = citizen_info['citizen_id']
        town = citizen_info['town']
        street = citizen_info['street']
        building = citizen_info['building']
        apartment = citizen_info['apartment']
        name = citizen_info['name']

        birth_date = datetime.strptime(citizen_info['birth_date'], '%d.%m.%Y')
        error_message = validate_birth_date(birth_date)
        if error_message:
            return jsonify(error_message), 400

        gender = citizen_info['gender']
        relatives = citizen_info['relatives']

        citizen = Citizen(citizen_id, town, street, building, apartment,
                          name, birth_date, gender, relatives)
        db.session.add(citizen)
        db.session.commit()

    data = {'data': {'import_id': 1}}
    return jsonify(data), 201
