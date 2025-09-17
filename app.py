from flask import Flask, render_template, redirect, url_for, request, flash
from sqlalchemy import text
from models import db, Product, Location, ProductMovement
from forms import ProductForm, LocationForm, MovementForm
from datetime import datetime
import os


def create_app(test_config=None):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "dev-secret-key"
    db_path = os.path.join(app.instance_path, 'inventory.sqlite')
    os.makedirs(app.instance_path, exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Create tables at startup (Flask 3 removed before_first_request)
    with app.app_context():
        db.create_all()
        # Lightweight migration: ensure image_url exists on product (SQLite only)
        try:
            cols = [row[1] for row in db.session.execute(text("PRAGMA table_info(product)"))]
            if 'image_url' not in cols:
                db.session.execute(text("ALTER TABLE product ADD COLUMN image_url VARCHAR"))
                db.session.commit()
        except Exception:
            # Ignore if not SQLite or alteration not needed
            pass

    # Home
    @app.route('/')
    def index():
        return render_template('base.html')

    # Products: list, add, edit, view
    @app.route('/products')
    def products():
        items = Product.query.order_by(Product.product_id).all()
        return render_template('products.html', products=items)

    @app.route('/product/new', methods=['GET','POST'])
    def product_new():
        form = ProductForm()
        if form.validate_on_submit():
            p = Product(product_id=form.product_id.data.strip(),
                        name=form.name.data.strip(),
                        description=form.description.data,
                        image_url=(form.image_url.data.strip() if form.image_url.data else None))
            db.session.add(p)
            db.session.commit()
            flash('Product added', 'success')
            return redirect(url_for('products'))
        return render_template('product_form.html', form=form)

    @app.route('/product/edit/<product_id>', methods=['GET','POST'])
    def product_edit(product_id):
        p = Product.query.get_or_404(product_id)
        form = ProductForm(obj=p)
        if form.validate_on_submit():
            p.name = form.name.data
            p.description = form.description.data
            p.image_url = form.image_url.data.strip() if form.image_url.data else None
            db.session.commit()
            flash('Product updated', 'success')
            return redirect(url_for('products'))
        return render_template('product_form.html', form=form, edit=True)

    # Locations
    @app.route('/locations')
    def locations():
        items = Location.query.order_by(Location.location_id).all()
        return render_template('locations.html', locations=items)

    @app.route('/location/new', methods=['GET','POST'])
    def location_new():
        form = LocationForm()
        if form.validate_on_submit():
            l = Location(location_id=form.location_id.data.strip(),
                         name=form.name.data.strip(),
                         address=form.address.data)
            db.session.add(l)
            db.session.commit()
            flash('Location added', 'success')
            return redirect(url_for('locations'))
        return render_template('location_form.html', form=form)

    @app.route('/location/edit/<location_id>', methods=['GET','POST'])
    def location_edit(location_id):
        loc = Location.query.get_or_404(location_id)
        form = LocationForm(obj=loc)
        if form.validate_on_submit():
            loc.name = form.name.data
            loc.address = form.address.data
            db.session.commit()
            flash('Location updated', 'success')
            return redirect(url_for('locations'))
        return render_template('location_form.html', form=form, edit=True)

    # Movements
    def _populate_movement_choices(form):
        products = Product.query.order_by(Product.product_id).all()
        form.product_id.choices = [(p.product_id, f"{p.product_id} - {p.name}") for p in products]

    @app.route('/movements')
    def movements():
        moves = ProductMovement.query.order_by(ProductMovement.timestamp.desc()).all()
        return render_template('movements.html', movements=moves)

    @app.route('/movement/new', methods=['GET','POST'])
    def movement_new():
        form = MovementForm()
        _populate_movement_choices(form)
        # For manual entry with suggestions
        all_locations = Location.query.order_by(Location.location_id).all()
        loc_suggestions = [(l.location_id, l.name) for l in all_locations]
        if form.validate_on_submit():
            # coerce blank strings to None
            from_loc = form.from_location.data or None
            to_loc = form.to_location.data or None
            # parse timestamp if provided
            ts = None
            if form.timestamp.data:
                try:
                    ts = datetime.fromisoformat(form.timestamp.data)
                except Exception:
                    ts = datetime.utcnow()
            else:
                ts = datetime.utcnow()

            m = ProductMovement(
                movement_id=form.movement_id.data.strip(),
                timestamp=ts,
                from_location=from_loc,
                to_location=to_loc,
                product_id=form.product_id.data,
                qty=form.qty.data
            )
            db.session.add(m)
            db.session.commit()
            flash('Movement recorded', 'success')
            return redirect(url_for('movements'))
        return render_template('movement_form.html', form=form, loc_suggestions=loc_suggestions)

    # Report: Balance quantity in each location (grid: Product, Warehouse, Qty)
    @app.route('/report')
    def report():
        # Approach: For each product & location compute sum of qty where to_location==loc (in) minus sum where from_location==loc (out)
        products = Product.query.order_by(Product.product_id).all()
        locations = Location.query.order_by(Location.location_id).all()

        # Build balances dict: {(product_id, location_id): qty}
        balances = {}
        # initialize zeros
        for p in products:
            for loc in locations:
                balances[(p.product_id, loc.location_id)] = 0

        # process every movement
        all_moves = ProductMovement.query.order_by(ProductMovement.timestamp).all()
        for m in all_moves:
            pid = m.product_id
            # if to_location present: add qty to that location
            if m.to_location:
                balances[(pid, m.to_location)] = balances.get((pid, m.to_location), 0) + m.qty
            # if from_location present: subtract qty from that location
            if m.from_location:
                balances[(pid, m.from_location)] = balances.get((pid, m.from_location), 0) - m.qty

        # create a viewable list of rows
        rows = []
        for (pid, lid), qty in balances.items():
            rows.append({
                'product_id': pid,
                'product_name': next((p.name for p in products if p.product_id == pid), ""),
                'location_id': lid,
                'location_name': next((l.name for l in locations if l.location_id == lid), ""),
                'qty': qty
            })

        return render_template('report.html', rows=rows)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
