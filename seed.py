from app import create_app
from models import db, Product, Location, ProductMovement
from datetime import datetime, timedelta
import uuid

app = create_app()
app.app_context().push()

db.drop_all()
db.create_all()

# create products
prods = [
    Product(product_id="P-A", name="Product A", description="Sample A"),
    Product(product_id="P-B", name="Product B", description="Sample B"),
    Product(product_id="P-C", name="Product C", description="Sample C"),
    Product(product_id="P-D", name="Product D", description="Sample D"),
]
for p in prods:
    db.session.add(p)

# create locations
locs = [
    Location(location_id="L-X", name="Warehouse X", address="Location X addr"),
    Location(location_id="L-Y", name="Warehouse Y", address="Location Y addr"),
    Location(location_id="L-Z", name="Warehouse Z", address="Location Z addr"),
]
for l in locs:
    db.session.add(l)
db.session.commit()

# create about 20 movements
moves = []
t0 = datetime.utcnow()
# add stock: move into L-X or L-Y from None
for i in range(1, 8):
    moves.append(ProductMovement(
        movement_id=f"M-IN-{i}",
        timestamp=t0 + timedelta(minutes=i),
        from_location=None,
        to_location="L-X" if i % 2 == 0 else "L-Y",
        product_id="P-A" if i % 3 == 0 else "P-B",
        qty=10 + (i % 5)
    ))

# internal transfers and removals
for i in range(8, 21):
    moves.append(ProductMovement(
        movement_id=f"M-{i}",
        timestamp=t0 + timedelta(minutes=i),
        from_location="L-X" if i % 2 == 0 else "L-Y",
        to_location="L-Z" if i % 3 == 0 else ("L-Y" if i % 2 == 0 else "L-X"),
        product_id="P-A" if i % 2 == 0 else "P-C",
        qty=(i % 6) + 1
    ))

for m in moves:
    db.session.add(m)
db.session.commit()
print("Seeded DB with products, locations and movements.")
