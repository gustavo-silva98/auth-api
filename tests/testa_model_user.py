from sqlalchemy import String, inspect

from domain_entity.models import User


def testa_columns():
    inspector = inspect(User)

    columns_name = {col.name for col in inspector.columns}
    assert columns_name == {'id', 'username', 'email', 'fullname', 'password'}

    username_column = inspector.columns.username

    assert isinstance(username_column.type, String)
    assert username_column.type.length == 20

    pks = [column.name for column in inspector.primary_key]
    assert pks == ['id']


def testa_repr():
    user = User(
        username='teste',
        email='teste@teste.com',
        fullname='teste da silva',
        password='teste',
    )

    user.id = 13

    user_expected = (
        'User (id=13, username=teste,'
        'email=teste@teste.com, fullname=teste da silva)'
    )

    assert repr(user) == user_expected
