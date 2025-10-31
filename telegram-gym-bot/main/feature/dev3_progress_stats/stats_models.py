#stats_models
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase  , Mapped, mapped_column,relationship

class Base(DeclarativeBase):
    pass

class User_Stats(Base):
    __tablename__="stats"
    

    
    id:Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    exercise:Mapped[String]=mapped_column(String,nullable=False)
    orm:Mapped[int]=mapped_column(primary_key=False)



