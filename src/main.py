"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for, json
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, Character, Favorite
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
# from flask_jwt_extended import create_access_token
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = "super-mega-duper-secret"
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)
jwt = JWTManager(app)

#Create one endpoint for generating new tokens
@app.route("/token", methods=["POST"])
def create_token():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    # Query your database for username and password
    user = User.query.filter_by(username=username, password=password).first()
    if user is None:
        # the user was not found on the database
        return jsonify({"msg": "Bad username or password"}), 401
    
    # create a new token with the user id inside
    access_token = create_access_token(identity=user.id)
    return jsonify({ "token": access_token, "user_id": user.id })


# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
# @jwt_required()
def get_user():
    users = User.query.all()
    map_users = [u.serialize() for u in users]
    return jsonify(map_users), 200

@app.route('/user/<int:user_id>', methods=['GET'])
def get_single_user(user_id):

    single_user = User.query.get(user_id)
    single_user = single_user.serialize()
    return jsonify(single_user), 200

@app.route('/planet', methods=['GET'])
# @jwt_required()
def get_planet():
    planets = Planet.query.all()
    map_planets = [u.serialize() for u in planets]
    return jsonify(map_planets), 200

@app.route('/planet/<int:planet_id>', methods=['GET'])
def get_single_planet(planet_id):

    single_planet = Planet.query.get(planet_id)
    single_planet = single_planet.serialize()
    return jsonify(single_planet), 200

@app.route('/character', methods=['GET'])
def get_char():

    chars = Character.query.all()
    map_chars = [u.serialize() for u in chars]
    return jsonify(map_chars), 200

@app.route('/character/<int:character_id>', methods=['GET'])
def get_single_character(character_id):

    single_character = Character.query.get(character_id)
    single_character = single_character.serialize()
    return jsonify(single_character), 200


@app.route('/user', methods=['POST'])
def post_user():
    request_data = request.data
    body = json.loads(request_data)
    user1 = User(username=body['username'], email=body['email'], first_name=body['first_name'], last_name=body['last_name'])
    db.session.add(user1)
    db.session.commit()
    return jsonify(user1.serialize())

@app.route('/planet', methods=['POST'])
def post_planet():
    request_data = request.data
    body = json.loads(request_data)
    planet1 = Planet(name=body['name'], population=body['population'], terrain=body['terrain'], climate=body['climate'], diameter=body['diameter'], gravity=body['gravity'])
    db.session.add(planet1)
    db.session.commit()
    return jsonify(planet1.serialize())

@app.route('/character', methods=['POST'])
def post_character():
    request_data = request.data
    body = json.loads(request_data)
    char1 = Character(name=body['name'], height=body['height'], hair_color=body['hair_color'], eye_color=body['eye_color'], birth_year=body['birth_year'], gender=body['gender'])
    db.session.add(char1)
    db.session.commit()
    return jsonify(char1.serialize())



@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def post_favorite_planet(planet_id):
    favorite1 = Favorite(planet_id=planet_id, user_id = 1)
    db.session.add(favorite1)
    db.session.commit()
    return jsonify(favorite1.serialize())

@app.route('/favorite/character/<int:character_id>', methods=['POST'])
def post_favorite_character(character_id):
    favorite1 = Favorite(character_id=character_id, user_id = 1)
    db.session.add(favorite1)
    db.session.commit()
    return jsonify(favorite1.serialize())



@app.route('/user/favorite', methods=['GET'])
def user_favorite():
    favorite_query = Favorite.query.filter_by(user_id = 1)
    map_favorite = [item.serialize() for item in favorite_query]
    return jsonify(map_favorite)

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet_from_user(planet_id):
    favorite1 = Favorite.query.filter_by(planet_id=planet_id, user_id = 1).first()
    if favorite1 is None:
        raise APIException('Favorite not found', status_code=404)
    db.session.delete(favorite1)
    db.session.commit()
    return jsonify(None)

@app.route('/favorite/character/<int:character_id>', methods=['DELETE'])
def delete_favorite_character_from_user(character_id):
    favorite1 = Favorite.query.filter_by(character_id=character_id, user_id = 1).first()
    if favorite1 is None:
        raise APIException('Favorite not found', status_code=404)
    db.session.delete(favorite1)
    db.session.commit()
    return jsonify(None)



# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)