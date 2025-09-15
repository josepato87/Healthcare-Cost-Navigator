from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Provider(Base):
    __tablename__ = "providers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    provider_id = Column(String, unique=True, index=True)
    name = Column(String)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String, index=True)
    star_rating = Column(Float)  # Mock rating 1-10
    procedures = relationship("Procedure", back_populates="provider")

class Procedure(Base):
    __tablename__ = "procedures"
    id = Column(Integer, primary_key=True, autoincrement=True)
    provider_id = Column(Integer, ForeignKey("providers.id"))
    ms_drg_definition = Column(String, index=True)
    total_discharges = Column(Integer)
    average_covered_charges = Column(Float)
    average_total_payments = Column(Float)
    average_medicare_payments = Column(Float)
    provider = relationship("Provider", back_populates="procedures")

