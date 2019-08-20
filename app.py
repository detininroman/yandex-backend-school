from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import request
from flask import jsonify

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
    birth_date = db.Column(db.String(256), unique=False)
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


@app.route('/imports', methods=['POST'])
def insert_citizens():
    for citizen_info in request.json['citizens']:
        for (key, value) in citizen_info.items():
            if not value:
                error_message = {'Error': f'"{key}" field of citizen'
                                          f' {citizen_info["citizen_id"]}'
                                          f' is not specified'}
                return jsonify(error_message), 400

        citizen_id = citizen_info['citizen_id']
        town = citizen_info['town']
        street = citizen_info['street']
        building = citizen_info['building']
        apartment = citizen_info['apartment']
        name = citizen_info['name']
        birth_date = citizen_info['birth_date']
        gender = citizen_info['gender']
        relatives = citizen_info['relatives']

        citizen = Citizen(citizen_id, town, street, building, apartment,
                          name, birth_date, gender, relatives)
        db.session.add(citizen)
        db.session.commit()

    data = {'data': {'import_id': 1}}
    return jsonify(data), 201
