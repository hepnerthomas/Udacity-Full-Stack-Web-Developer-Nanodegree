# import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)

class AssetClass(Base):

    __tablename__ = 'asset_class'

    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)    

    # financial_asset = relationship('FinancialAsset', cascade='all, delete-orphan')

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'user_id': self.user_id
        }    

class FinancialAsset(Base):

    __tablename__ = 'financial_asset'

    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    description = Column(String(250))
    price = Column(String(30))

    asset_class_id = Column(Integer, ForeignKey('asset_class.id'))
    asset_class = relationship("AssetClass", backref=backref("financial_assets", cascade="all, delete"))
    # asset_class = relationship("AssetClass")

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)    

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'price': self.price
        }    

engine = create_engine('sqlite:///financialAssetswithusers.db')
Base.metadata.create_all(engine)
