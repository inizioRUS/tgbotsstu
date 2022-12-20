import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Rate(SqlAlchemyBase):
    __tablename__ = 'rates'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_name = sqlalchemy.Column(sqlalchemy.String)
    mark = sqlalchemy.Column(sqlalchemy.Integer)
    voice_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("voices.id"))
    voice = orm.relation('Voice')
