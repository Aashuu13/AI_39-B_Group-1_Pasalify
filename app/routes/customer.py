from flask import Blueprint
from app.controllers import customer_controller

customer_bp = Blueprint('customer', __name__)

customer_bp.route('/products')(customer_controller.products)