from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional

class ProductForm(FlaskForm):
    product_id = StringField("Product ID", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[Optional()])
    image_url = StringField("Image URL", validators=[Optional()])
    submit = SubmitField("Save")

class LocationForm(FlaskForm):
    location_id = StringField("Location ID", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    address = TextAreaField("Address", validators=[Optional()])
    submit = SubmitField("Save")

class MovementForm(FlaskForm):
    movement_id = StringField("Movement ID", validators=[DataRequired()])
    timestamp = StringField("Timestamp (optional)", validators=[Optional()])  # could parse later if provided
    from_location = StringField("From Location", validators=[Optional()])
    to_location = StringField("To Location", validators=[Optional()])
    product_id = SelectField("Product", validators=[DataRequired()], coerce=str, choices=[])
    qty = IntegerField("Quantity", validators=[DataRequired()])
    submit = SubmitField("Save")
