from sqlalchemy import Boolean, Column, ForeignKey, Integer, String,Float, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.orm import mapped_column,Mapped
from database.database import Base
from sqlalchemy import event
class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    height: Mapped[int] = mapped_column(Integer, nullable=True)
    weight: Mapped[int] = mapped_column(Integer, nullable=True)
    calves: Mapped[int] = mapped_column(Integer, nullable=True)
    tigth: Mapped[int] = mapped_column(Integer, nullable=True)
    chest: Mapped[int] = mapped_column(Integer, nullable=True)
    waist: Mapped[int] = mapped_column(Integer, nullable=True)
    forearm: Mapped[int] = mapped_column(Integer, nullable=True)
    arm: Mapped[int] = mapped_column(Integer, nullable=True)
    neck: Mapped[int] = mapped_column(Integer, nullable=True)
    shoulders: Mapped[int] = mapped_column(Integer, nullable=True)
    age: Mapped[int] = mapped_column(Integer, nullable=True)
    gender: Mapped[str] = mapped_column(String, nullable=True)
    exercise_pr: Mapped[int] = mapped_column(Integer, nullable=True)
    icm: Mapped[float] = mapped_column(Float, nullable=True)
    bodyFat: Mapped[float] = mapped_column(Float, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", back_populates="profile", uselist=False)
    __table_args__ = (UniqueConstraint("user_id"),)

    def calculate_icm_and_bodyfat(mapper,connection,self):
    
  
        self.icm = self.weight / (self.height / 100) ** 2
        self.bodyFat = 1.2 * self.icm + 0.23 * self.age - 10.8 * int(self.gender == 'male') - 5.4

    def set_icm_and_bodyfat_to_null(mapper,connection,self):
        self.icm = None
        self.bodyFat = None

event.listen(Profile, 'before_update', Profile.calculate_icm_and_bodyfat)
event.listen(Profile, 'before_insert', Profile.set_icm_and_bodyfat_to_null)

    # def __init__(self, **kwargs):       
    #     super().__init__(**kwargs)
    #     if (self.weight== None  or self.height== None)== True:
    #         self.icm = 3
    #         self.bodyFat = 4
    #         icm = 3
    #         bodyFat =5
    #     else:
    #         self.icm = self.weight / (self.height ** 2)
    #         self.bodyFat = 1

    