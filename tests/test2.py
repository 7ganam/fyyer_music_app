
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Sequence, Integer, String, MetaData, Table
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import ColumnClause
from sqlalchemy.sql import compiler
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ganam:1@localhost:5432/test1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class table_1(db.Model):
    __tablename__ = 'table_1'
    ID = Column(Integer)
    FIRST_NAME = Column(String(80), primary_key=True)
    LAST_NAME = Column(String(80))


class table_2(db.Model):
    __tablename__ = 'table_2'
    ID_1 = Column(Integer)
    FIRST_NAME_1 = Column(String(80), primary_key=True)
    LAST_NAME_1 = Column(String(80))


query = db.session.query(table_1).join(table_2, table_1.ID ==
                                       table_2.ID_1).filter(table_1.ID == 11)


print("My Join Query: ", str(query))

print("\n----> Print Output")

for _a in query.all():
    print(_a.ID, _a.FIRST_NAME, _a.LAST_NAME)


db.create_all()


@app.route('/')
def index():
    person = Person.query.first()
    return 'Hello ' + person.name


if __name__ == '__main__':
    app.run()
