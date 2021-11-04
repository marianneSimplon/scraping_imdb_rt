#!/usr/bin/env python
# coding: utf-8

# In[1]:


from bs4 import BeautifulSoup
import requests
import numpy as np
import pandas as pd


# In[12]:


#Permet de créer la BeatifulSoup à partir d'une URL et avec les paramètres que l'on souhaite en headers
def soup_url(url,headers={'User-Agent': 'python-requests/2.25.1', 'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*', 'Connection': 'keep-alive'}):
        req = requests.get(url,headers=headers)
        soup = BeautifulSoup(req.text, "lxml")
        return soup


# # Top 250 sur IMDb

# In[20]:


def fetch_film_IMDb():
    
    #Initialisation de l'index pour avoir les bonnes pages (avec les bons premiers films)
    index=1
    
    #Création de listes vides qui seront remplies par les données récupérées puis concaténées dans un DataFrame
    titre = []
    genre = []
    duree = []
    annee = []
    
    #Création d'une variable headers qui permettra de récupérer les infos nécessaires du site en version américaine
    headers = {"Accept-Language": "en-US,en;q=0.5"}
    
    #Boucle de récupération des données visées
    for page in range(0,5):
        IMDb_url = f"https://www.imdb.com/search/title/?groups=top_250&sort=user_rating,desc&start={index}&ref_=adv_nxt"
        soup = soup_url(IMDb_url,headers=headers)
        for titre_film in soup.find_all(class_="lister-item-header"):
            titre.append(titre_film.a.text)
        for genre_film in soup.find_all(class_="genre"):
            genre.append(genre_film.get_text(strip=True))
        for duree_film in soup.find_all(class_="runtime"):
            duree.append(duree_film.get_text(strip=True).split()[0])
        for annee_film in soup.find_all(class_="lister-item-year"):
            annee.append(annee_film.get_text(strip=True).split()[-1][1:5])            
        index+=50 #Incrémente de 50 car par défaut il y a 50 films par page
        
    df = pd.DataFrame(list(zip(titre,annee,duree,genre)),columns =['titre', 'annee','duree','genre'])
    
    return df


# In[21]:


films = fetch_film_IMDb()


# In[99]:


films.to_csv('top_film_imdb.csv', index = False, header=True,sep='|')


# # Rotten tomatoes : tomatometer and audience score

# In[100]:


df=pd.read_csv("top_film.csv", delimiter="|")


# In[101]:


df['tomatometer'] = None
df['audience_score'] = None
df['url_tomatoes'] = None


# In[102]:


def fetch_film_rt(df):
    #Pour chaque ligne du DataFrame on va effectuer une recherche à partir du titre du film
    for ligne in range(len(df)):
        recherche = df['titre'].iloc[ligne]
        annee = df['annee'].iloc[ligne]
        recherche = recherche.replace(" ","%20")           
        rt2_url = f"https://www.rottentomatoes.com/search?search={recherche}"
        soup2 = soup_url(rt2_url)
        #Sélection du bon film à enregistrer selon le match avec sa date de sortie
        if soup2.find_all("search-page-media-row",{"releaseyear":annee}):
            new_url=soup2.find_all("search-page-media-row",{"releaseyear":annee})[0]("a")[0]["href"]
            df['url_tomatoes'].iloc[ligne] = new_url
            #On crée une nouvelle requete qui va sur la page du film visé
            soup3 = soup_url(new_url)       
            df["tomatometer"].iloc[ligne] = soup3.find('score-board')['tomatometerscore']
            df["audience_score"].iloc[ligne] = soup3.find('score-board')['audiencescore']
    return df


# In[103]:


df2 = fetch_film_rt(df)


# In[ ]:


df2.to_csv('top_film_imdb_rt.csv', index = False, header=True,sep='|')

