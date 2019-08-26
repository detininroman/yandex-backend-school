import math
from datetime import datetime


def error(arg: str) -> dict:
    return {'error': arg}


def calculate_age(born):
    today = datetime.today()
    return today.year - born.year - \
           ((today.month, today.day) < (born.month, born.day))


def percentile(values: list, percent: int) -> float or None:
    """Finds the percentile of a list of values.

    :param values: sorted list of values
    :param percent: percent (from 0 to 100)
    :return: the percentile of the values
    """
    if values is None:
        return None

    values.sort()

    k = (len(values) - 1) * (percent / 100)
    f, c = math.floor(k), math.ceil(k)
    result = values[int(k)] if f == c else \
        values[int(f)] * (c - k) + values[int(c)] * (k - f)
    return round(result, 2)


def contains_digit(string: str) -> bool:
    """Checks if string contains digits

    :param string: string to check
    :return: True if contains, False otherwise
    """
    return any(char.isdigit() for char in string)


def contains_letter(string: str) -> bool:
    """Checks if string contains letters

    :param string: string to check
    :return: True if contains, False otherwise
    """
    return any(char.isalpha() for char in string)


def validate_field(data: dict, field_name: str) -> (dict, int):
    # validate types
    if field_name in ['town', 'street', 'building',
                      'name', 'birth_date', 'gender']:
        if not isinstance(data[field_name], str):
            return error(f'{field_name} name must be string'), 400

    elif field_name in ['citizen_id', 'apartment']:
        if not isinstance(data[field_name], int):
            return error(f'{field_name} name must be int'), 400

    elif field_name in ['relatives']:
        if not isinstance(data[field_name], list):
            return error(f'{field_name} field must be list'), 400
        for relative in data[field_name]:
            if not isinstance(relative, int):
                return error(f'{field_name} must contain ints'), 400

    # validate values
    if field_name in ['town', 'street', 'building']:
        if len(data[field_name]) >= 256:
            return error(f'{field_name} name should not exceed'
                         f' 256 characters'), 400
        if not contains_digit(data[field_name]) and \
                not contains_letter(data[field_name]):
            return error(f'{field_name} name should contain at least'
                         f' one letter or one digit'), 400

    elif field_name in ['citizen_id', 'apartment']:
        if data[field_name] < 0:
            return error(f'{field_name} cannot be negative'), 400

    elif field_name in ['name']:
        if not len(data[field_name]) or len(data[field_name]) >= 256:
            return error(f'{field_name} should not be empty and exceed'
                         f' 256 characters'), 400

    elif field_name in ['gender']:
        if data[field_name] not in ['male', 'female']:
            return error('Invalid gender'), 400

    elif field_name in ['birth_date']:
        try:
            birth_date = datetime.strptime(data[field_name], '%d.%m.%Y')
            if birth_date >= datetime.now():
                return error(f'{field_name} `{birth_date}` is not valid'), 400
        except ValueError:
            return error(f'{field_name} is not valid'), 400

    return


def validate_payload(
        citizens: list, fields_to_check: list = None) -> (dict, int):
    all_fields = [
        'citizen_id', 'building', 'street',
        'town', 'gender', 'birth_date',
        'name', 'apartment', 'relatives'
    ]
    # validate only needed fields while updating citizen's info
    fields_to_check = fields_to_check or all_fields

    identifiers = []
    for citizen in citizens:
        identifiers.append(citizen['citizen_id'])
        # while citizen creating (not updating)
        # check if all fields exist in payload
        if 'citizen_id' in fields_to_check:
            if len(fields_to_check) != len(all_fields):
                return error(f'all fields must be filled'), 400

        for field_name in fields_to_check:
            # check if field name is correct
            if field_name not in all_fields:
                return error(f'{field_name} is unknown field'), 400
            # check if values are not empty
            if not citizen.get(field_name) and field_name != 'relatives':
                return error(f'{field_name} must be specified'), 400

        # check if all fields meet specific conditions
        for field_name in fields_to_check:
            is_field_invalid = validate_field(citizen, field_name)
            if is_field_invalid:
                return is_field_invalid

        # validate relatives
        relatives = []
        for relative_id in citizen['relatives']:
            relatives.append(relative_id)
            relative = [item for item in citizens if
                        item['citizen_id'] == relative_id][0]
            if citizen['citizen_id'] not in relative['relatives']:
                return error('invalid relatives'), 400

        # validate that relatives don't repeat
        if not len(relatives) == len(set(relatives)):
            return error('invalid relatives'), 400

    # validate ID uniqueness
    if not len(set(identifiers)) == len(identifiers):
        return error('identifiers are not unique'), 400

    return


def debug(arg):
    return print(arg, flush=True)


def create_default_citizen(
        citizen_id: int,
        town: str = 'Moscow',
        street: str = 'Tverskaya',
        building: str = '1/1',
        apartment: int = 10,
        name: str = 'Roman',
        birth_date: str = '03.02.1998',
        gender: str = 'male',
        relatives: list = None) -> dict:
    relatives = relatives or []
    return locals()
