import pytest

from application_service.token_service import JWTLibHandler, JWTTokenService
from domain_entity.exceptions import BadRequest
from settings import Settings


@pytest.fixture
def get_settings():
    return Settings()


@pytest.fixture
def get_jwt_token_service(get_settings):
    settings = get_settings
    jwt_handler = JWTLibHandler()
    return JWTTokenService(jwt_handler=jwt_handler, settings=settings)


def testa_create_acces_token(get_jwt_token_service):
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
