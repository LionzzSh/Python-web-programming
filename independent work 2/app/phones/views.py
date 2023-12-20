from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity 
from . import phones_bp
from .models import Phone
from app import db

@phones_bp.route('/test', methods=['GET'])
def ping():
    return jsonify({"message": "you on phone api"})

@phones_bp.route('/phones', methods=['GET'])
def get_phones():
    phones = Phone.query.all()
    phones_list = [{'id': phone.id, 'brand': phone.brand, 'model': phone.model, 'year': phone.year} for phone in phones]
    return jsonify({'phones': phones_list})

@phones_bp.route('/phones/<int:phone_id>', methods=['GET'])
def get_phone(phone_id):
    phone = Phone.query.get_or_404(phone_id)
    return jsonify({'id': phone.id, 'brand': phone.brand, 'model': phone.model, 'year': phone.year})

@phones_bp.route('/phones', methods=['POST'])
@jwt_required()
def create_phone():
    current_user = get_jwt_identity()  

    data = request.get_json()
    brand, model, year = data.get('brand'), data.get('model'), data.get('year')

    if not all([brand, model, year]):
        return jsonify({'error': 'Missing data'}), 400

    new_phone = Phone(brand=brand, model=model, year=year)
    db.session.add(new_phone)
    db.session.commit()

    return jsonify({'id': new_phone.id, 'brand': new_phone.brand, 'model': new_phone.model, 'year': new_phone.year}), 201

@phones_bp.route('/phones/<int:phone_id>', methods=['PUT'])
@jwt_required()
def update_phone(phone_id):
    phone = Phone.query.get_or_404(phone_id)
    data = request.get_json()
    brand, model, year = data.get('brand'), data.get('model'), data.get('year')

    if not all([brand, model, year]):
        return jsonify({'error': 'Missing data'}), 400

    phone.brand, phone.model, phone.year = brand, model, year
    db.session.commit()

    return jsonify({'id': phone.id, 'brand': phone.brand, 'model': phone.model, 'year': phone.year})

@phones_bp.route('/phones/<int:phone_id>', methods=['DELETE'])
@jwt_required()
def delete_phone(phone_id):
    phone = Phone.query.get_or_404(phone_id)
    db.session.delete(phone)
    db.session.commit()
    return jsonify({'message': 'Phone deleted successfully'})
