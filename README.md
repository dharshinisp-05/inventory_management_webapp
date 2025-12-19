# Inventory Management (Flask)

This is a simple, friendly web app that helps you keep track of products across different places. 
Add your products, create locations (like warehouses or store rooms), and record movements when stock goes in or out. 
The report page shows how much of each product you have in each location right now.

## Features
- Add / Edit / View Products
- Add / Edit / View Locations
- Record Product Movements (from / to / qty)
- Balance report: product quantities per warehouse

## Extra features
- You can add an image URL to a product and see it on the Products page.
- A built-in chatbot helps you write a clear description for any product, without mistakes.

## Run locally
1. `python -m venv venv && source venv/bin/activate`
2. `pip install -r requirements.txt`
3. `python seed.py` (creates sample data)
4. `python app.py` (or `flask run`)
5. Open `http://127.0.0.1:5000/`

## DB schema
- `product(product_id, name, description)`
- `location(location_id, name, address)`
- `product_movement(movement_id, timestamp, from_location, to_location, product_id, qty)`

## Balance calculation
For each movement:
- add `qty` to `to_location` if present
- subtract `qty` from `from_location` if present

See `app.py` for implementation.



