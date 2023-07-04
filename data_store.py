# импорты
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import Session
from config import db_url_object

# схема БД
metadata = MetaData()       # metadata содержит всю информацию о базе данных и таблицах, используется для создания/удаления таблиц в БД
Base = declarative_base()   # нужно для класса SQLAlchemy(обычно называемый Base), чтобы не было ошибки

# создаем класс на основе Base и присваиваем ему нужный __tablename__ и создаем profile_id и user_id
class Viewed(Base):     # class 'sqlalchemy.orm.decl_api.DeclarativeMeta'
    __tablename__ = 'viewed'
    profile_id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, primary_key=True)

class DBTools():
    # инициализация класса self
    def __init__(self):
        # создание движка соединения
        self.engine = create_engine(db_url_object)
        # создадим в БД таблицу(если не создана), хранящуюся в экземпляре MetaData
        Base.metadata.create_all(self.engine)
        
    # добавление записи в бд
    def add_user(self, profile_id, user_id):
        with Session(self.engine) as session:
            to_bd = Viewed(profile_id=profile_id, user_id=user_id)
            session.add(to_bd)
            session.commit()

    # извлечение записей из БД
    def check_user(self, profile_id, user_id):
        with Session(self.engine) as session:
            from_bd = session.query(Viewed).filter(Viewed.profile_id==profile_id, Viewed.user_id==user_id).all()
            # если from_bd существует то true
            return True if from_bd else False

#if __name__ == '__main__':
    #db = DBTools()
    #add_user(engine, 20230629, 456)
    #res = db.check_user(20230629, 456)
    #print(res)