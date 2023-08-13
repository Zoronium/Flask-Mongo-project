from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
from os import environ
import bcrypt

app = Flask(__name__)

# Configure MongoDB connection
MongoURI = environ.get("MongoURl", "mongodb://")
MongoPort = environ.get("MongoPORT", "db:27017/")
MongoDBName = environ.get("MongoBDName", "Test")
MongoDBColl = environ.get("MongoBDColl", "User")

# server
DEBUG = environ.get("SERVERDEBUG", False)
SERVERPORT = int(environ.get("SERVERPORT", 5000))


client = MongoClient(f"{MongoURI}{MongoPort}")
db = client[MongoDBName]
users_collection = db[MongoDBColl]

user_schema = {"name": str, "email": str, "password": str}


@app.route("/server", methods=["GET"])
def getServer():
    return client.server_info()


@app.route("/users", methods=["GET"])
def get_users():
    users = list(users_collection.find({}, {"_id": 0}))
    return jsonify(users)


@app.route("/users/<string:user_id>", methods=["GET"])
def get_user(user_id):
    user = users_collection.find_one({"_id": ObjectId(user_id)}, {"_id": 0})
    if user:
        return jsonify(user)
    return jsonify({"message": "User not found"}), 404


@app.route("/users", methods=["POST"])
def create_user():
    new_user: user_schema = request.json

    if not all(field in new_user for field in user_schema.keys()):
        return jsonify({"message": "Incomplete user data"}), 400

    # Hash password
    new_user["password"] = bcrypt.hashpw(
        new_user["password"].encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")

    user_id = users_collection.insert_one(new_user).inserted_id
    return jsonify({"message": "User created", "user_id": str(user_id)}), 201


@app.route("/users/<string:user_id>", methods=["PUT"])
def update_user(user_id):
    updated_data = request.json

    if "password" in updated_data:
        # Hash password
        password = updated_data["password"].encode("utf-8")
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
        updated_data["password"] = hashed_password.decode("utf-8")

    result = users_collection.update_one(
        {"_id": ObjectId(user_id)}, {"$set": updated_data}
    )
    if result.modified_count > 0:
        return jsonify({"message": "User updated"})
    return jsonify({"message": f"User with ID {user_id} not found"}), 404


@app.route("/users/<string:user_id>", methods=["DELETE"])
def delete_user(user_id):
    result = users_collection.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count > 0:
        return jsonify({"message": "User deleted"})
    return jsonify({"message": f"User with ID {user_id} not found"}), 404


if __name__ == "__main__":
    app.run(debug=DEBUG, port=SERVERPORT)
