# -*- coding: utf-8 -*-
"""

Daniela Ribeiro Castro
Groupe A1b
INF tc3 - TD1 + Projet WEB: Récupération, mise en forme, et stockage de données

"""

# import du module d'accès à la base de données
import sqlite3
from zipfile import ZipFile
import json


###-----------------------------------------------------------------###

with ZipFile('north_america.zip','r') as z:
    # liste des documents contenus dans le fichier zip
    l = z.namelist()

def get_info(pays):
    with ZipFile('north_america.zip','r') as z:
        # infobox de l'un des pays
        info = json.loads(z.read(pays))
    return(info)
    
###-----------------------------------------------------------------###    
    
def get_name(info): # Récupération du nom complet d'un pays depuis l'infobox wikipédia
    if 'conventional_long_name' in info.keys():
        nom = info['conventional_long_name']
    else:
        nom = info['common_name']
    return(nom)
    
    
def get_capital(info): # Récupération de la capitale d'un pays depuis l'infobox wikipédia
    
    capital = info['capital']
    if capital[0] == '[' or capital[-1] == ']':
        capital = capital[2:-2]
    if "|" in capital:
        capital = capital.split("|")[1]
    # Si l'infobox ne contient pas d'information directement exploitable
    if 'conventional_long_name' in info and info['conventional_long_name'] == 'United States of America':
        return ('Washington, D.C.') 
    
    return(capital)
        
    
def get_coords(info): # Récupération des coordonnées de la capitale depuis l'infobox d'un pays
    # S'il existe des coordonnées dans l'infobox du pays (cas le plus courant)
    if 'coordinates' in info.keys():
        coords = info['coordinates'].split(sep='|')
        #Latitute N/S
        lat_d = int(coords[1]) + int(coords[2])/60
        aux = 3
        if coords[aux] != 'S' and coords[aux] != 'N': # Dans le cas où les donnés ont 3 paramètres: degrés, minutes, secondes.
            lat_d += int(coords[aux])/3600
            aux += 1
        if coords[aux] == 'S': # Si est au Sud, c'est negatif
            lat_d = -lat_d
        #Longitude E/W
        lon_d = int(coords[aux+1]) + int(coords[aux+2])/60
        aux += 3
        if coords[aux] != 'W' and coords[aux] != 'E': # Dans le cas où les donnés ont 3 paramètres: degrés, minutes, secondes.
            lon_d += int(coords[aux])/3600
            aux += 1
        if coords[aux] == 'W':
            lon_d = -lon_d
    # Si l'infobox ne contient pas d'information directement exploitable
    if 'conventional_long_name' in info and info['conventional_long_name'] == 'United States of America':
        return ({'lat': 38.88333333, 'lon': -77.01666667})

    coords = {'lat': lat_d, 'lon': lon_d}
    return(coords)
    
    
def get_currency(info):
    if 'currency' in info.keys():
        currency = info['currency']
        if '[[' in currency:
            currency = currency.split("[[")[1]
            currency = currency.split("]]")[0]

    if 'conventional_long_name' in info and info['conventional_long_name'] == 'United States of America':
        currency = 'United States dollar'
        
    return(currency)
    
def get_area(info):
    if 'area_km2' in info:
        area = info['area_km2']
        area = area.replace(",", " ")
        print(area)
    else:
        area = 0 # C'est le cas des États Unis --> on corrige directement dans la table
        
    return(area)
    
    
###-----------------------------------------------------------------###  
    
# Ouverture d'une connexion avec la base de données
conn = sqlite3.connect('table_north_america.sqlite')

def save_country(conn, country, info):
    # préparation de la commande SQL
    c = conn.cursor()
    sql = 'INSERT INTO countries VALUES (?, ?, ?, ?, ?)'

    # les infos à enregistrer
    name = get_name(info)
    capital = get_capital(info)
    coords = get_coords(info)

    # soumission de la commande (noter que le second argument est un tuple)
    c.execute(sql,(country, name, capital, coords['lat'], coords['lon']))
    conn.commit()
    return

#
# Mise à jour de la base de données
#
def update_country_area(conn,country,info):
    # préparation de la commande SQL
    c = conn.cursor()
    sql = 'UPDATE countries SET area=? WHERE wp=?'

    # soumission de la commande (noter que le second argument est un tuple)
    area = get_area(info)
    c.execute(sql,(area,country))
    conn.commit()


def print_country(country, info): # J'ai utilisée pour tester le bon fonctionnement des autres fonctions
    # les infos à enregistrer
    name = get_name(info)
    capital = get_capital(info)
    coords = get_coords(info)
    # print des infos
    print("\n\tFichier: {}\n\t Nom: {}\n\t Capital: {}\n\t Latitude: {}\n\t Longitude: {}".format(country, name, capital, coords['lat'], coords['lon']))
    return
    
###-----------------------------------------------------------------### 
def write_table_SQL(conn, l):
    for country in l:
        info = get_info(country)
        save_country(conn, country, info)
        
def update_table_SQL(conn, l):
    for country in l:
        info = get_info(country)
        update_country_area(conn,country,info)


