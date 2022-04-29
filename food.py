# -*- coding: utf-8 -*-
"""
Created on Fri Apr 29 21:18:59 2022

@author: Andrea Rogel
"""

from bokeh.plotting import figure, show, output_file
from bokeh.io import export_png
import numpy as np
from pymongo import MongoClient
import matplotlib.pyplot as plt


output_file("food.html")

db_uri = "mongodb+srv://etudiant:ur2@clusterm1.0rm7t.mongodb.net/"
client = MongoClient(db_uri)
db = client["food"]

coll = db["NYfood"]

query =[{"$match": {"borough": "Manhattan"}},
        {"$unwind": "$grades"},
        {"$match": {"grades.grade": {"$ne": "Not Yet Graded"}}},
        {"$project": {"notes": "$grades.grade"}},
        {"$group": {"_id": "$notes",
                    "nb_notes": {"$sum": 1}}},
        {"$sort": {"nb_notes": -1}}]
donnees = db.NYfood.aggregate(query)
a = list(donnees)


note =[]
nb = []
for i in a:
    note.append(i['_id']) 
    nb.append(i['nb_notes'])
 
graph = figure(x_range = note, height = 250, 
               title = "Nombre de notes données dans le quartier de Manhattan",
               toolbar_location = None, tools=""    )
   
graph.vbar(x=note, top = nb, width = 0.5)

show(graph)
output_file("food.html")

export_png(graph, filename="food.png")