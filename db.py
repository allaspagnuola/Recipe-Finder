from flask_pymongo import pymongo


CONNECTION_STRING = "mongodb+srv://hazelchen1214:a12345@cluster0.jzt2jns.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"


# Create user that sends/receives requests
client = pymongo.MongoClient(CONNECTION_STRING)


# Find or create database
db = client.get_database("flask_mongodb_recipes")


# Create a collection (JSON format dict) within the database
collection = pymongo.collection.Collection(db, "collection")

