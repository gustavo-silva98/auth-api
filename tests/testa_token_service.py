from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

import pytest
from freezegun import freeze_time
from jwt import PyJWTError

from application_service.token_service import JWTLibHandler, JWTTokenService
from domain_entity.exceptions import BadRequest, UnauthorizedException
from settings import Settings


@pytest.fixture
def mock_jwt_handler():
    handler = MagicMock(spec=JWTLibHandler)
    handler.encode.return_value = b'mocked_token'
    handler.decode.return_value = {
        'sub': 'username',
        'perms': 'perm1,perm2',
        'token_type': 'access',
    }
    return handler


@pytest.fixture
def get_settings():
    settings = MagicMock(spec=Settings)
    settings.SECRET_KEY = 'test_secret'
    settings.ALGORITHM = 'HS256'
    return settings


@pytest.fixture
def get_jwt_token_service(mock_jwt_handler, get_settings):
    return JWTTokenService(jwt_handler=mock_jwt_handler, settings=get_settings)


def testa_create_access_token_invalid(get_jwt_token_service):
    mock_username = 'username'
    mock_perms = ['perm1', 'perm2']
    expires_delta_mock = None

    token_service = get_jwt_token_service
    with pytest.raises(BadRequest):
        token_service.create_access_token(
            username=mock_username,
            permissions=mock_perms,
            expires_delta=expires_delta_mock,
        )


def testa_create_access_token(
    get_jwt_token_service, mock_jwt_handler, get_settings
):

    token_service = get_jwt_token_service
    token = token_service.create_access_token(
        username='username',
        permissions=['perm1', 'perm2'],
        expires_delta=timedelta(minutes=30),
    )

    assert token == b'mocked_token'
    called_payload = mock_jwt_handler.encode.call_args[0][0]
    assert called_payload['sub'] == 'username'
    assert called_payload['perms'] == 'perm1,perm2'
    assert called_payload['token_type'] == 'access'

    assert mock_jwt_handler.encode.call_args[0][1] == get_settings.SECRET_KEY
    assert mock_jwt_handler.encode.call_args[0][2] == get_settings.ALGORITHM


def testa_decode_token_valid(
    get_settings, mock_jwt_handler, get_jwt_token_service
):
    token_service = get_jwt_token_service
    payload = token_service.decode_token('valid_token')

    assert payload['sub'] == 'username'

    mock_jwt_handler.decode.assert_called_with(
        'valid_token', get_settings.SECRET_KEY, get_settings.ALGORITHM
    )


def testa_decode_token_invalid(mock_jwt_handler, get_jwt_token_service):
    mock_jwt_handler.decode.side_effect = PyJWTError()

    with pytest.raises(UnauthorizedException):
        get_jwt_token_service.decode_token('invalid_token')


def testa_access_token_expiration(mock_jwt_handler, get_settings):
    service = JWTTokenService(mock_jwt_handler, get_settings)
    now = datetime.now(UTC)

    with freeze_time(now):
        service.create_access_token('user1', [], timedelta(minutes=30))
        payload = mock_jwt_handler.encode.call_args[0][0]
        assert payload['exp'] == str(
            int((now + timedelta(minutes=30)).timestamp())
        )


def testa_refresh_token_expiration(mock_jwt_handler, get_settings):
    service = JWTTokenService(mock_jwt_handler, get_settings)
    now = datetime.now(UTC)

    with freeze_time(now):
        service.create_refresh_token('user1', timedelta(minutes=30))
        payload = mock_jwt_handler.encode.call_args[0][0]
        assert payload['exp'] == str(
            int((now + timedelta(minutes=30)).timestamp())
        )


def testa_create_refresh_token_invalid(get_jwt_token_service):
    mock_username = 'username'
    expires_delta_mock = None

    token_service = get_jwt_token_service
    with pytest.raises(BadRequest):
        token_service.create_refresh_token(
            username=mock_username,
            expires_delta=expires_delta_mock,
        )
