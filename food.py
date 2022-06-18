from turtle import width
from bokeh.plotting import figure, show, output_file
from bokeh.io import export_png
import numpy as np
from pymongo import MongoClient
import matplotlib.pyplot as plt
import pandas as pd
from bokeh.plotting import ColumnDataSource
from bokeh.models import HoverTool, Column, Div,Row
from bokeh.models.widgets import Tabs, Panel

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

data = ColumnDataSource(data=dict(nombre=nb, note=note))



fig = figure(title="Nombre de notes données dans le quartier de Manhattan", x_range=note, height = 400)


fig.vbar(x='note',top='nombre',source = data, width=0.5)


hover_tool = HoverTool(tooltips=[("Nombre de notes", "@nombre")])
fig.add_tools(hover_tool)

div = Div(text="""
<h1> Visualisation libre de données issues de NYfood </h1>
<p> Ce graphique représente le nombre de notes de chaque type données sur les restaurants du quartier de Manhattan à New York. 
</p>

""")

layout = Row(Column(div, fig, width=900))
output_file("question3.html")
show(layout)





