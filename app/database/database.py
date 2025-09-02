from sqlalchemy.orm import declarative_base,DeclarativeBase
from sqlalchemy import create_engine, event,Column,Boolean
from sqlalchemy.orm import ORMExecuteState, Session, sessionmaker, with_loader_criteria
import os
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



Base = declarative_base()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db= Session()
# db.query(Human).execution_options(skip_visibility_filter=True).all()
# # engine = create_engine(DATABASE_URL)
# # SessionLocal = sessionmaker(bind=engine)

# class VisibilityMixin:
#     is_deleted = Column(Boolean, server_default="0")

# class Human(DeclarativeBase, VisibilityMixin):
#     __tablename__ = "humans"

# class Alien(DeclarativeBase, VisibilityMixin):
#     __tablename__ = "aliens"

# @event.listens_for(SessionLocal, "do_orm_execute")
# def _add_filtering_criteria(execute_state: ORMExecuteState):
#     if execute_state.is_select:
#         execute_state.statement = execute_state.statement.options(
#             with_loader_criteria(
#                 VisibilityMixin,
#                 lambda cls: cls.is_deleted.is_(False),
#                 include_aliases=True,
#             )
#         )
