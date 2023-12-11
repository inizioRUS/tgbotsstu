import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Voice(SqlAlchemyBase):
    __tablename__ = 'voices'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    file_id = sqlalchemy.Column(sqlalchemy.String)
    user_name = sqlalchemy.Column(sqlalchemy.String)
    date = sqlalchemy.Column(sqlalchemy.DateTime)
    rates = orm.relationship("Rate", back_populates='voice', lazy='subquery')
