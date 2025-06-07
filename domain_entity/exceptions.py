class AppException(Exception):
    def __init__(
        self, message: str, code: str = 'APP_ERROR', status_code: int = 500
    ):
        self.message = message
        self.code = code
        self.status_code = status_code


class DuplicateUserError(AppException):
    def __init__(self, message: str = 'Usuário Duplicado'):
        super().__init__(message, code='AUTH_USER_DUPLICATE', status_code=409)


class PasswordNotMatch(AppException):
    def __init__(
        self,
        message: str = ('As senhas não são iguais. Por gentileza validar'),
    ):
        super().__init__(message, code='AUTH_USER_DONT_MATCH', status_code=409)


class WrongPassword(AppException):
    def __init__(self, message: str = 'Senha inválida.'):
        super().__init__(
            message, code='AUTH_USER_WRONG_PASSWORD', status_code=401
        )


class UserNotCreated(AppException):
    def __init__(self, message: str = 'Usuário não encontrado'):
        super().__init__(
            message, code='AUTH_USER_NOT_CREATED', status_code=404
        )
