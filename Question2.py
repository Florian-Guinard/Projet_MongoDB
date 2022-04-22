from pymongo import MongoClient

db_uri = "mongodb+srv://etudiant:ur2@clusterm1.0rm7t.mongodb.net/"
client = MongoClient(db_uri)
db = client["publications"]

cursor = db.hal_irisa_2021.aggregate([
    {"$unwind":"$authors"},
    {"$group":{"_id":"$authors",
             "titres": {"$addToSet": "$title" }}},
    {"$addFields":{"les_titres": "$titres"}},
    {"$project":{"nb_titres":{"$size": "$titres"},
               "les_titres":1}},
    {"$sort":{"nb_titres":-1}},
    {"$limit": 20},
    {"$project":{"nb_titres":0}} 
    
])		

l = list(cursor)
print(l)