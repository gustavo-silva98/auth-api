class AppException(Exception):
    def __init__(self, message: str, code: str = 'APP_ERROR'):
        self.message = message
        self.code = code


class DuplicateUserError(AppException):
    def __init__(self, message: str = 'Usuário Duplicado'):
        super().__init__(message, code='AUTH_USER_DUPLICATE')


class PasswordNotMatch(AppException):
    def __init__(
        self,
        message: str = ('As senhas não são iguais. Por gentileza, ' 'validar'),
    ):
        super().__init__(message, code='AUTH_USER_DONT_MATCH')


class WrongPassword(AppException):
    def __init__(self, message: str = 'Senha inválida.'):
        super().__init__(message, code='AUTH_USER_WRONG_PASSWORD')


class UserNotCreated(AppException):
    def __init__(self, message: str = 'Usuário não encontrado'):
        super().__init__(message, code='AUTH_USER_NOT_CREATED')
