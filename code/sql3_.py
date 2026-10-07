from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class Customer(Base):
    __tablename__ = "customers"
    customer_id = Column(String(20), primary_key=True)
    gender = Column(String(10))
    senior_citizen = Column(Integer)
    partner = Column(Integer)
    dependents = Column(Integer)

class Contract(Base):
    __tablename__ = "dim_contract"
    contract_id = Column(Integer, primary_key=True)
    contract_name = Column(String(30))

#query using sqlalchemy orm

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    "mysql+pymysql://root:root@localhost/telecom_db"
)

Session = sessionmaker(bind=engine)

session = Session()

customer = session.query(Customer).filter_by(
    customer_id="7590-VHVEG"
).first()

print(customer.customer_id)
print(customer.gender)
print(customer.partner)
