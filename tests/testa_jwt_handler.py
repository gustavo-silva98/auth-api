import jwt
import pytest
from jwt import PyJWTError

from application_service.token_service import JWTLibHandler


@pytest.fixture
def get_jwt_handler():
    return JWTLibHandler()


def testa_jwt_handler_encode(get_jwt_handler):
    payload = {'sub': 'test_user'}
    encoded = get_jwt_handler.encode(payload, 'secret', 'HS256')

    assert isinstance(encoded, str)


def testa_jwt_handler_decode_valid(get_jwt_handler):
    token = jwt.encode({'sub': 'test_user'}, 'secret', algorithm='HS256')

    decoded = get_jwt_handler.decode(token, 'secret', 'HS256')

    assert decoded['sub'] == 'test_user'


def testa_jwt_handler_decode_invalid_token(get_jwt_handler):
    invalid_token = 'invalid.token.here'

    with pytest.raises(PyJWTError):
        get_jwt_handler.decode(invalid_token, 'secret', 'HS256')


def testa_jwt_handler_decode_wrong_secret(get_jwt_handler):
    token = jwt.encode({'sub': 'test_user'}, 'right_secret', algorithm='HS256')

    with pytest.raises(PyJWTError):
        get_jwt_handler.decode(token, 'wrong_secret', 'HS256')
