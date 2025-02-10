from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import relationship,mapped_column,Mapped
from ..database.database import Base
from ..models.rol import Rol
from ..models.user_rol import User_rol
from ..models.invitacion import Invitacion

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True,autoincrement=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    profile = relationship("Profile", uselist=False, back_populates="user",lazy="joined")
    teams_created = relationship("Team", back_populates="creator",lazy="joined")
    teams = relationship("Team", secondary="team_members",back_populates="members",lazy="joined")
    tournaments_created= relationship("Tournament",back_populates="creator")
    rol=relationship("Rol",secondary="user_roles",back_populates="useRol",lazy="joined")
    # User_T:Mapped["User_team"]=relationship("User_team",back_populates="user")
    # team: Mapped["Team"] = relationship("Team",  back_populates="creator")

# Para lograr esto, puedes utilizar la opción cascade en las relaciones de SQLAlchemy. Esto te permite especificar que ciertas operaciones se “propaguen” desde un objeto padre a sus objetos relacionados. Aquí te muestro cómo podrías hacerlo:

# Python

# from sqlalchemy import Column, Integer, String, ForeignKey
# from sqlalchemy.orm import relationship

# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True)

#     # otros campos...

#     equipos = relationship("Equipo", backref="usuario", cascade="all, delete")

# class Equipo(Base):
#     __tablename__ = "equipos"

#     id = Column(Integer, primary_key=True)
#     # otros campos...

#     usuario_id = Column(Integer, ForeignKey("users.id"))
# Código generado por IA. Revisar y usar cuidadosamente. Más información sobre preguntas frecuentes.
# En este código, he añadido cascade="all, delete" a la relación equipos en la clase User. Esto significa que cuando un objeto User sea eliminado, todos los objetos Equipo relacionados también serán eliminados.

# De manera similar, puedes hacer lo mismo para la relación entre equipos y torneos.

# Por favor, ten en cuenta que el uso de cascade="all, delete" puede tener efectos significativos en tu base de datos, ya que eliminará permanentemente los registros relacionados. Asegúrate de entender completamente cómo funciona antes de usarlo.

# Espero que esto te ayude a resolver el problema. 😊