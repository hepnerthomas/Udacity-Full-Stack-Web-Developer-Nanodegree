from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, AssetClass, FinancialAsset

engine = create_engine('sqlite:///financialAssetswithusers.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Create dummy user
User1 = User(name="Marco Rubio", email="mrubio@gmail.com")
session.add(User1)
# session.commit()

# Financial Assets for Crypto-Asset Class
assetClass1 = AssetClass(user_id=1, name="Crypto-Assets")

session.add(assetClass1)
# session.commit()

financialAsset1 = FinancialAsset(user_id=1, name="Bitcoin", description="Bitcoin is the original cryptocurrency that started it all. It is viewed by an increasing subset of the global populace as 'digital gold'.",
                     price="$3600", asset_class=assetClass1)

session.add(financialAsset1)
# session.commit()

financialAsset2 = FinancialAsset(user_id=1, name="Ethereum", description="Ethereum is the second largest cryptocurrency by current market capitalization. It has been the a platform for initial coin offerings (ICOs) and seeks to build commercial use cases for the blockchain beyond electronic cash.",
                     price="$120", asset_class=assetClass1)

session.add(financialAsset2)
# session.commit()

financialAsset3 = FinancialAsset(user_id=1, name="Ripple", description="Not even a cryptocurrency.",
                     price="$0.30", asset_class=assetClass1)

session.add(financialAsset3)
# session.commit()

# Financial Assets for Precious Metals Class
assetClass2 = AssetClass(user_id=1, name="Precious Metals")

session.add(assetClass2)
# session.commit()

financialAsset1 = FinancialAsset(user_id=1, name="Gold", description="Gold is the most valuable monetary metal, and served as the premier store of value for over 5,000 years.",
                     price="$1300", asset_class=assetClass2)

session.add(financialAsset1)
# session.commit()

financialAsset2 = FinancialAsset(user_id=1, name="Silver", description="Silver was once the second most valuable monetary metal and within striking distance of gold. As precious metals no longer provide backing for most fiat currencies, the value of silver has fallen dramatically over the last century.",
                     price="$15", asset_class=assetClass2)

session.add(financialAsset2)

# Financial Assets for US Equities 
assetClass3 = AssetClass(user_id=1, name = "US Equity Indices")
financialAsset1 = FinancialAsset(user_id=1, name="S&P 500", description="Created by Standard & Poors, the S&P 500 is an index of a basket of the 500 largest U.S. companies by market capitalization.",
                     price="$2600", asset_class=assetClass3)

session.add(financialAsset1)

# Financial Assets for Chinese Equities
assetClass4 = AssetClass(user_id=1, name = "Chinese Equity Indices")
financialAsset1 = FinancialAsset(user_id=1, name="Shanghai Composite Index", description="Index of Largest Chinese companies.",
                     price="$???", asset_class=assetClass4)
session.add(financialAsset1)

# Financial Assets for Fixed Income


session.commit()
print("added financial assets to the database!")