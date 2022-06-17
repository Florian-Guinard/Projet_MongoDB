from pymongo import MongoClient
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
from bokeh.io import output_file, show
from bokeh.models import BoxZoomTool, Circle, HoverTool,MultiLine,Plot, Range1d, ResetTool, Column, Div,Row
from bokeh.palettes import Blues8
from bokeh.plotting import from_networkx, figure
from bokeh.transform import linear_cmap

db_uri = "mongodb+srv://etudiant:ur2@clusterm1.0rm7t.mongodb.net/"
client = MongoClient(db_uri)
db = client["publications"]

auteurspublications = db.hal_irisa_2021.aggregate([
    {"$unwind": "$authors"},
    {"$group": {"_id": {"name": "$authors.name",
                    "firstname": "$authors.firstname"},
                "titre": {"$push": "$title"},
                "nbpubli": {"$sum": 1}}},
    {"$sort": {"nbpubli": -1}},
    {"$limit": 20},
    {"$group": {"_id": {"name": "$_id.name",
        "firstname": "$_id.firstname",
        "titre" : "$titre",
        "nbpubli": "$nbpubli"}}}    
])		



# Récupération dans listes les noms des auteurs, leur prénom et leurs publications
auteurs = [nom["_id"] for nom in auteurspublications]

# Création d'un dataframe avec les noms, prénoms et liste de publications associés à chaque auteurs
#data = pd.DataFrame(auteurs) 
rows = []
for data in auteurs:  
    rows.append(data) 
  
df = pd.DataFrame(rows) 

# Création d'une liste avec le nombre de publications associé à chaque auteur
# Création d'une liste de publication commun entre deux auteurs
# Création d'une liste avec le noeud cible et d'une liste avec le noeud source
nbrepubli = []
nbrepublicommun = []
noeudcible = []
noeudsource = []
for source in df.name:
    publisource = list(df.titre[df.name == source])[0]

    for cible in df.name:
        if cible == source:
            continue
        
        publicible = list(df.titre[df.name == cible])[0]
        
        cmp = {}
        publitotale = publisource + publicible
        
        lstelem =[]
        lstcompte = []
        for elem in publitotale:
            if elem not in lstelem:
                lstelem.append(elem)
                compte = publitotale.count(elem)
                if compte != 1:
                    lstcompte.append(compte)
        commun = len(lstcompte)
        
        publitotale = []

        noeudsource.append(source)
        noeudcible.append(cible)
        nbrepublicommun.append(commun)
        nbrepubli.append(int(df.nbpubli[df.name == source]))
        
# dataframe à utiliser pour le network
datagraphbis = pd.DataFrame({"source": noeudsource, "target": noeudcible, "weight": nbrepublicommun, "node_size": nbrepubli})

# sélection des lignes où les individus ont un lien
df_mask=datagraphbis['weight'] > 0
datagraph = datagraphbis[df_mask]


#########################################################
#               PREPARATION BOKEH                       #
#########################################################

# Transformation du dataframe en reseau
G = nx.from_pandas_edgelist(datagraph)

for auteur in datagraphbis.source.unique():
    if auteur not in G.nodes():
        G.add_node(auteur)
        
# visualisation basique
nx.draw(G, with_labels=True,width=datagraph.weight)
nx.draw_circular(G, with_labels=True, width=datagraph.weight)

# Préparation des données
auteurunique = datagraphbis.copy()
auteurunique.drop_duplicates(subset ="source", keep = 'first', inplace=True)

# Dictionnaire auteur et taille de noeud (nbre de publications)
dico = {}
i=0
for auteur in auteurunique.source:
    dico[auteur] = auteurunique.node_size.values[i]
    i+=1

# Dictionnaire liens et taille du lien (nbre de publications en commun)

dicoedges = {}
for edge in G.edges():
    for ind in datagraph.index:
        if (datagraph.source[ind] == edge[0] or datagraph.source[ind] == edge[1]) and (datagraph.target[ind] == edge[0] or datagraph.target[ind] == edge[1]): 
            dicoedges[edge] = datagraph.weight[ind]

#########################################################
#               AFFECTATION POIDS                       #
#########################################################

# ajouter le dico créé comme attribut du nœud.
nx.set_node_attributes(G, name='adjusted_node_size', values=dico)

# ajouter le dicoedges créé comme attribut du lien.
nx.set_edge_attributes(G, name='weight', values=dicoedges)




#########################################################
#                     OUTILS SURVOL                     #
#########################################################

# Outils de survol sur les noueds
HOVER_TOOLTIPS = [
        ("Auteur", "@index"),
        ("Nbre de publications", "@adjusted_node_size")
]


#########################################################
#                CREATION GRAPHIQUE                     #
#########################################################


# Création du graphique
plot = figure(tooltips = HOVER_TOOLTIPS,
              tools="pan,wheel_zoom,save,reset", active_scroll='wheel_zoom',
              x_range=Range1d(-12.1, 12.1), y_range=Range1d(-12.1, 12.1),title='Réseau des 20 auteurs les plus prolifiques et leurs interactions')

# Création du network
network_graph = from_networkx(G, nx.circular_layout, scale=10, center=(0, 0)) #nx.spring_layout

# Choix de la taille et couleur des noeuds en fonction du nombre de publications de l'auteur
minimum_value_color = min(network_graph.node_renderer.data_source.data['adjusted_node_size'])
maximum_value_color = max(network_graph.node_renderer.data_source.data['adjusted_node_size'])
network_graph.node_renderer.glyph = Circle(size='adjusted_node_size', fill_color=linear_cmap('adjusted_node_size', Blues8, minimum_value_color, maximum_value_color))



#########################################################
#               AFFECTATION TAILLE                      #
#########################################################
# Taille des liens
network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.8, line_width='weight') 

plot.renderers.append(network_graph)


#########################################################
#                       CODE HTML                       #
#########################################################

#Ajout de code html
div = Div(text="""
<h1> Réseau de publications scientifiques </h1>
<p> La base publications contient les informations relatives aux publications de scientifiques du laboratoire IRISA . 
On a visualisé les liens entre les auteurs de ces publications, en utilisant un code couleur qui permette de distinguer les auteurs par
leurs nombres de publications et en représentant les liens (co-publications) existant entre les auteurs. 
</p>
<a href="..index.html">
    <img src="img_accueil.htm" alt="retour page d'accueil">
</a>
""")

#########################################################
#               ONGLET + AFFICHAGE WEB                  #
#########################################################

layout = Row(Column(div, plot, width=900))
output_file("page2.html")
show(layout)