from parking import db, app, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id: int):
    return Users.query.get(int(user_id))


# application users model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, db.Identity(), primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(30), nullable=False)


# customers model
class Customers(db.Model):
    __tablename__ = "customers"
    customer_id = db.Column(db.Integer, db.Identity(), primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(18), unique=True, nullable=False)
    address = db.Column(db.String(100), nullable=True)
    registration_date = db.Column(db.DateTime, nullable=False)
    date_of_editing = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"{self.first_name} {self.last_name} / phone: {self.phone} / address: {self.address})"


# vehicle model
class Vehicles(db.Model):
    __tablename__ = "vehicles"
    vehicle_id = db.Column(db.Integer, db.Identity(), primary_key=True)
    vehicle_registration_number = db.Column(db.String(20), unique=True, nullable=False)
    vehicle_type = db.Column(db.String(15), nullable=False)
    brand = db.Column(db.String(20), nullable=False)
    model = db.Column(db.String(30), nullable=False)
    color = db.Column(db.String(25), nullable=False)
    registration_date = db.Column(db.DateTime, nullable=False)
    date_of_editing = db.Column(db.DateTime, nullable=True)
    is_subscribed = db.Column(db.Boolean, nullable=False)
    customer_id = db.Column(
        db.Integer, db.ForeignKey("customers.customer_id", ondelete="CASCADE"), nullable=False)


# subscription model
class Subscriptions(db.Model):
    __tablename__ = "subscriptions"
    subscription_id = db.Column(db.Integer, db.Identity(), primary_key=True)
    parking_spot_number = db.Column(db.String(2), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    tax = db.Column(db.Numeric(6, 2), nullable=False)
    overdue_fee = db.Column(db.Numeric(6, 2), nullable=True)
    date_of_editing = db.Column(db.DateTime, nullable=True)
    subscription_status = db.Column(db.String(8), nullable=True)
    vehicle_id = db.Column(
        db.Integer, db.ForeignKey("vehicles.vehicle_id", ondelete="CASCADE"), nullable=False)

    def __repr__(self):
        return f"{self.parking_spot_number}"


# create table models
with app.app_context():
    # clear all the table definitions held in memory in order to declare tables again
    # db.metadata.clear()
    db.create_all()
    # db.drop_all()
