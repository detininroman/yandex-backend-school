from flask import Flask, Response
from flask_sqlalchemy import SQLAlchemy
from flask import request

app = Flask("__name__")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://roman:123456@localhost:9000/database01'
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
    citizen_id = request.form['citizen_id']
    town = request.form['town']
    street = request.form['street']
    building = request.form['building']
    apartment = request.form['apartment']
    name = request.form['name']
    birth_date = request.form['birth_date']
    gender = request.form['gender']
    relatives = request.form['relatives']

    citizen = Citizen(citizen_id, town, street, building, apartment, name, birth_date, gender, relatives)
    db.session.add(citizen)
    db.session.commit()
    return Response("{'a':'b'}", status=201)


if __name__ == '__main__':
    app.run()
