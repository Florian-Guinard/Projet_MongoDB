from pymongo import MongoClient
import networkx as nx
import numpy as pd

db_uri = "mongodb+srv://etudiant:ur2@clusterm1.0rm7t.mongodb.net/"
client = MongoClient(db_uri)
db = client["publications"]

cursor = db.hal_irisa_2021.aggregate([
    {"$unwind":"$authors"},
    {"$group":{"_id":"$authors",
             "titres": {"$addToSet": "$title" }}},
    {"$addFields":{"les_titres": "$titres"}},
    {"$project":{"nb_publications":{"$size": "$titres"},
               "les_titres":1}},
    {"$sort":{"nb_publications":-1}},
    {"$limit": 20}
    
])		

l = list(cursor)




# création d'une liste de dictionnaire avec son nom_prenom, son nombres de publications et ses publications
liste_dico = []
for elem in l:
    dico = {}
    nom = elem["_id"]["name"]
    prenom = elem["_id"]["firstname"]
    dico["id"] = nom + "_" + prenom
    dico["nb_publi"] = elem["nb_publications"]
    dico["publications"] = elem["les_titres"]
    liste_dico.append(dico)

print(liste_dico)
print("*"*20)

# Comparaison des auteurs 2 à 2 pour savoir leurs nombres de co-publications
myNodesList = [] # liste des auteurs
myEdgeList = [] # listes des liens de co-publications
for auteur1 in liste_dico:
    myNodesList.append(auteur1["id"])
    for auteur2 in liste_dico:
        if auteur1["id"] != auteur2["id"]:
            nb_co_publications = 0
            for publi1 in auteur1["publications"]:
                for publi2 in auteur2["publications"]:
                    if publi1 == publi2:
                        nb_co_publications += 1
            tuple_liens_publications = (auteur1["id"], auteur2["id"], {"weight":nb_co_publications})
            myEdgeList.append(tuple_liens_publications)

G = nx.Graph()
G.add_nodes_from(myNodesList)
G.add_edges_from(myEdgeList) 

pods_of_links = []
for (node1,node2,data) in G.edges(data=True):
        pods_of_links.append(data['weight'])


list_color = []
for auteur in liste_dico:
    if auteur["nb_publi"] > 12:
        list_color.append("red")
    elif auteur["nb_publi"] > 11:
        list_color.append("orange")
    else:
        list_color.append("green")


nx.draw_circular(G,node_color = list_color, width=pods_of_links ,node_size=100,with_labels=True)

