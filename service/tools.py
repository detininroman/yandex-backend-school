from datetime import datetime


def error(arg):
    return {'error': arg}


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
            return error(f'{field_name} name must be string')

    elif field_name in ['citizen_id', 'apartment']:
        if not isinstance(data[field_name], int):
            return error(f'{field_name} name must be int')

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


def validate_payload(citizens, fields_to_check=None):
    all_fields = ['citizen_id', 'building', 'street', 'town',
                  'gender', 'birth_date', 'name', 'apartment', 'relatives']
    # validate only needed fields while updating citizen's info
    fields_to_check = fields_to_check or all_fields

    # validate ID uniqueness
    identifiers = [item['citizen_id'] for item in citizens]
    if not len(set(identifiers)) == len(identifiers):
        return error('Identifiers are not unique'), 400

    for citizen in citizens:
        # while citizen creating (not updating)
        # check if all fields exist in payload
        if 'citizen_id' in fields_to_check:
            if len(fields_to_check) != len(all_fields):
                return error(f'all fields must be filled'), 400

        for field_name in fields_to_check:
            # check if field name is correct
            if field_name not in citizen.keys():
                return error(f'{field_name} is unknown field'), 400
            # check if values are not empty
            if not citizen.get(field_name) and field_name != 'relatives':
                return error(f'{field_name} must be specified'), 400

        # check if all fields meet specific conditions
        for field_name in fields_to_check:
            is_field_invalid = validate_field(citizen, field_name)
            if is_field_invalid:
                return is_field_invalid
    return


def debug(arg):
    return print(arg, flush=True)
