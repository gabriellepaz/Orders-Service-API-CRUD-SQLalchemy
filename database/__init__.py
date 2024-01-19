from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy import Table, event
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import subqueryload
from datetime import datetime

engine = create_engine('sqlite:///database/database.db')
Session = sessionmaker(bind=engine)
session = Session()

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    address_id = Column(Integer, ForeignKey('address.id'))
    address = relationship('Address', backref='address_user', cascade='all, delete')

    def __repr__(self):
        return f'<User (id={self.id}, name={self.name}, email={self.email}, address={self.address})>'
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
class Address(Base):
    __tablename__ = 'address'

    id = Column(Integer, primary_key=True)
    street = Column(String(255), nullable=False)
    number = Column(Integer)

    def __repr__(self):
        return f'<Address (id={self.id}, street={self.street}, number={self.number})>'
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# Tabela intermediária   
order_product = Table('order_product', Base.metadata,
    Column('order_id', Integer, ForeignKey('order.id')),
    Column('product_id', Integer, ForeignKey('product.id'))
)
    
class Order(Base):
    __tablename__ = 'order'

    id = Column(Integer, primary_key=True) 
    date = Column(DateTime)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', backref='order_user')
    product = relationship('Product', secondary=order_product, backref='order_product')

    def __repr__(self):
        return f'<Order(id={self.id}, date={self.date}, user={self.user}, product={self.product})>'
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# Deleção do relacionamento many to many
@event.listens_for(Order, 'after_delete')
def delete_order_product(mapper, connection, target):
    connection.execute(order_product.delete().where(order_product.c.order_id == target.id))

class Product(Base):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    price = Column(Float)

    def __repr__(self):
        return f'<Product (id={self.id}, name={self.name}, price={self.price})>'
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
Base.metadata.create_all(engine)

class Queries():
    # Order
    @staticmethod
    def add_order(**kwargs):
        try:
            with session:
                order = Order()
                columns = [c.name for c in order.__table__.columns][1:]
                for col in columns:
                    if col in kwargs:
                        setattr(order,col,kwargs[col])
                user_id = kwargs['user']['id']
                user = session.query(User).filter(User.id==user_id).scalar()
                order.date = datetime.now()
                order.user = user
                for id in kwargs['product_ids']:
                    product = session.query(Product).filter(Product.id==id).scalar()
                    order.product.append(product)
                session.add(order)
                session.commit()
                return order.id
        except Exception as e:
            print(e)
    @staticmethod
    def get_order_by_user(**kwargs):
        try:
            with session:
                user_id = kwargs['user_id']
                product = subqueryload(Order.product)
                user = subqueryload(Order.user).subqueryload(User.address)
                order = session.query(Order).options(product,user).filter(Order.user_id==user_id).all()
                return order
        except Exception as e:
            print(e)
    @staticmethod
    def get_order(**kwargs):
        try:
            with session:
                id = kwargs['id']
                product = subqueryload(Order.product)
                user = subqueryload(Order.user).subqueryload(User.address)
                order = session.query(Order).options(product,user).filter(Order.id==id).scalar()
                return order
        except Exception as e:
            print(e)
    @staticmethod
    def delete_order(**kwargs):
        try:
            with session:
                id = kwargs['id']
                order = session.query(Order).filter(Order.id==id).scalar()
                session.delete(order)
                session.commit()
                return 'order deleted'
        except Exception as e:
            print(e)
    # User
    @staticmethod
    def add_user(**kwargs):
        try:
             with session:
                user = User()
                columns_user = [c.name for c in user.__table__.columns][1:]
                for col in columns_user:
                    if col in kwargs['user']:
                        setattr(user,col,kwargs['user'][col])
                address = Address()
                columns_address = [c.name for c in address.__table__.columns][1:]
                for col in columns_address:
                    if col in kwargs['address']:
                        setattr(address,col,kwargs['address'][col])
                user.address = address
                session.add(user)
                session.commit()
                return user.id               
        except Exception as e:
            print(e)
    @staticmethod
    def get_user(**kwargs):
        try:
            with session:
                id = kwargs['id']
                address = subqueryload(User.address)
                user = session.query(User).options(address).filter(User.id==id).scalar()
                return user
        except Exception as e:
            print(e)
    @staticmethod
    def update_user(**kwargs):
        try:
            with session:
                id = kwargs['user']['id']
                user = session.query(User).filter(User.id==id).scalar()
                columns_user = [c.name for c in user.__table__.columns][1:]
                for col in columns_user:
                    if col in kwargs['user']:
                        setattr(user,col,kwargs['user'][col])

                address = user.address
                columns_address = [c.name for c in address.__table__.columns][1:]
                for col in columns_address:
                    if col in kwargs['address']:
                        setattr(address,col,kwargs['address'][col])
                session.commit()
                return user.id
        except Exception as e:
            print(e)
    @staticmethod
    def delete_user(**kwargs):
        try:
            with session:
                id = kwargs['id']
                user = session.query(User).filter(User.id==id).scalar()
                session.delete(user)
                session.commit()
                return 'user deleted'
        except Exception as e:
            print(e)
    #Products
    @staticmethod
    def add_product(**kwargs):
        try:
            with session:
                product = Product()
                columns = [c.name for c in product.__table__.columns][1:]
                for col in columns:
                    if col in kwargs:
                        setattr(product,col,kwargs[col])
            session.add(product)
            session.commit()
            return product.id
        except Exception as e:
                print(e)
    @staticmethod
    def get_product(**kwargs):
        try:
            with session:
                id = kwargs['id']
                product = session.query(Product).filter(Product.id==id).scalar()
                return product
        except Exception as e:
                print(e)
    @staticmethod
    def update_product(**kwargs):
        try:
            with session:
                id = kwargs['id']
                product = session.query(Product).filter(Product.id==id).scalar()
                columns = [c.name for c in product.__table__.columns][1:]
                for col in columns:
                     if col  in kwargs:
                          setattr(product,col,kwargs[col])
                session.commit()
                return product.id
        except Exception as e:
                print(e)
    @staticmethod
    def delete_product(**kwargs):
        try:
            with session:
                id = kwargs['id']
                product = session.query(Product).filter(Product.id==id).scalar()
                session.delete(product)
                session.commit()
                return 'product deleted'

        except Exception as e:
                print(e)


# Products
# Add product
# data = {
#     'name':'Mouse',
#     'price':49.99
# }
# add = Queries.add_product(**data)
# print(add)
                
# # Get product
# data = {'id':1}
# get = Queries.get_product(**data)
# print(get)

# # Update product
# data = {
#     'id':1,
#     'name':'Bicicleta',
#     'price':1118.97
# }
# upt = Queries.update_product(**data)
# print(upt)
                
# # Delete product
# data = {'id':1}
# delete = Queries.delete_product(**data)
# print(delete)
                

# # User
# add user
# data = {
#     'user':{
#         'id':3,
#         'name':'Danilo Matos',
#         'email':'danilohen@gmail.com'
#     },
#     'address':{
#         'street':'R. São José',
#         'number':123
#     }
# }
# user = Queries.add_user(**data)
# print(user)
                
# ## Get user
# data = {'id':1}
# user = Queries.get_user(**data)
# print(user)
                
# ## update user
# data = {
#     'user':{
#         'id':1,
#         'name':'José Silva',
#     },
#     'address':{
#         'street':'R. Fagundes',
#         'number':1110
#     }
# }
# user = Queries.update_user(**data)
# print(user)
                
# # Delete user
# data = {'id':1}
# user = Queries.delete_user(**data)
# print(user)

# # Order
# data = {
#     'user': {'id':2},
#     'product_ids':[2,4]
# }
# order = Queries.add_order(**data)
                
# ## Get order by user
# data = {'user': {'id':2}}
# order = Queries.get_order_by_user(**data)
# print(order)
                
# ## Delete Order
# data = {'id':1}
# order = Queries.delete_order(**data)
# print(order)
                
# Usando SQL
from sqlalchemy import text

product = session.query(Product).from_statement(text("SELECT * FROM product")).all()
# print(product)

product = session.query(Product).all()
# print(product)

product = session.query(Product).filter(Product.name.like("Mic%")).all()
# print(product)

from sqlalchemy import and_

product = session.query(Product).filter(and_(Product.price > 50, Product.price < 1000)).all()
# print(product)

from sqlalchemy import or_

product = session.query(Product).filter(or_(Product.id == 3, Product.id == 6)).all()
# print(product)

products = session.query(Product).group_by(Product.price).distinct().all()
# print(products)
