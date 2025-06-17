class AppException(Exception):
    def __init__(
        self,
        message: str,
        code: str = 'APP_ERROR',
        status_code: int = 500,
        headers: dict[str, str] | None = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.headers = headers or {}


class DuplicateUserError(AppException):
    def __init__(self, message: str = 'Usuário Duplicado'):
        super().__init__(message, code='AUTH_USER_DUPLICATE', status_code=409)


class PasswordNotMatch(AppException):
    def __init__(
        self,
        message: str = ('As senhas não são iguais. Por gentileza validar'),
    ):
        super().__init__(message, code='AUTH_USER_DONT_MATCH', status_code=409)


class UnauthorizedException(AppException):
    def __init__(
        self,
        message: str = 'Could not validate credentials',
        bearer: str = 'Bearer',
    ):
        super().__init__(
            message,
            code='AUTH_INVALID_CREDENTIALS',
            status_code=401,
            headers={'WWW-Authenticate': f'{bearer}'},
        )


class UserNotFound(AppException):
    def __init__(self, message: str = 'Usuário não encontrado'):
        super().__init__(
            message, code='AUTH_USER_NOT_CREATED', status_code=404
        )


class BadRequest(AppException):
    def __init__(
        self, message: str = 'Bad Request, avalie a request novamente.'
    ):
        super().__init__(message, code='AUTH_BAD_REQUEST', status_code=400)
