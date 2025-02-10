from sqlalchemy import  ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.orm import mapped_column,Mapped
from ..database.database import Base

class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nickname: Mapped[str] = mapped_column(String,nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id",ondelete="cascade"))
    user: Mapped["User"] = relationship("User", back_populates="profile", uselist=False)
    


# event.listen(Profile, 'before_update', Profile.calculate_icm_and_bodyfat)
# event.listen(Profile, 'before_insert', Profile.set_icm_and_bodyfat_to_null)

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

    