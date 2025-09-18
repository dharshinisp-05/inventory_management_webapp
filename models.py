from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Product(db.Model):
    __tablename__ = "product"
    product_id = db.Column(db.String, primary_key=True) 
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    image_url = db.Column(db.String, nullable=True)

    def __repr__(self):
        return f"<Product {self.product_id} - {self.name}>"

class Location(db.Model):
    __tablename__ = "location"
    location_id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=True)

    def __repr__(self):
        return f"<Location {self.location_id} - {self.name}>"

class ProductMovement(db.Model):
    __tablename__ = "product_movement"
    movement_id = db.Column(db.String, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    from_location = db.Column(db.String, db.ForeignKey("location.location_id"), nullable=True)
    to_location = db.Column(db.String, db.ForeignKey("location.location_id"), nullable=True)
    product_id = db.Column(db.String, db.ForeignKey("product.product_id"), nullable=False)
    qty = db.Column(db.Integer, nullable=False)

    product = db.relationship("Product", backref="movements")
    from_loc = db.relationship("Location", foreign_keys=[from_location], backref="out_movements")
    to_loc = db.relationship("Location", foreign_keys=[to_location], backref="in_movements")

    def __repr__(self):
        return f"<Move {self.movement_id}: {self.product_id} {self.qty} {self.from_location}->{self.to_location}>"
