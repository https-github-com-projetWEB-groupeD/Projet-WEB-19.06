# -*- coding: utf-8 -*-
"""
INF tc3 - Projet d'application WEB (Groupe D - A1b)
Élèves: Daniela Ribeiro Castro
        Gabriela Moreno de Andrade
        Baptiste Tiberghien
        Nicolas Dumas
        Tristan Grt
        Philippe Berton
"""

import http.server
import socketserver
from urllib.parse import urlparse, parse_qs, unquote
import json
import sqlite3

# Définition du nouveau handler

class RequestHandler(http.server.SimpleHTTPRequestHandler):

  # Version du serveur
  server_version = 'Version_finale.py/0.1'
  
  # sous-répertoire racine des documents statiques
  static_dir = '/client'
  
  # on surcharge la méthode qui traite les requêtes GET
  def do_GET(self):
    # on récupère les paramètres
    self.init_params()

    # requete location - retourne la liste de lieux et leurs coordonnées géogrpahiques
    if self.path_info[0] == 'countries':
        self.send_countries()

    # le chemin d'accès commence par /country et se poursuit par un nom de pays
    elif self.path_info[0] == 'country' and len(self.path_info) > 1:
        self.send_country(self.path_info[1])

    # requête générique
    elif self.path_info[0] == "service":
      self.send_html('<p>Path info : <code>{}</p><p>Chaîne de requête : <code>{}</code></p>' \
          .format('/'.join(self.path_info),self.query_string));

    else:
      self.send_static()

  # On surcharge la méthode qui traite les requêtes HEAD
  def do_HEAD(self):
      self.send_static()

  # On surcharge la méthode pour traiter les requêtes POST - non utilisée dans l'exemple
  def do_POST(self):
    self.init_params()

    # Requête générique
    if self.path_info[0] == "service":
      self.send_html(('<p>Path info : <code>{}</code></p><p>Chaîne de requête : <code>{}</code></p>' \
          + '<p>Corps :</p><pre>{}</pre>').format('/'.join(self.path_info),self.query_string,self.body));
    else:
      self.send_error(405)


  # On envoie le document statique demandé
  def send_static(self):

    # on modifie le chemin d'accès en insérant le répertoire préfixe
    self.path = self.static_dir + self.path

    # on appelle la méthode parent (do_GET ou do_HEAD)
    # à partir du verbe HTTP (GET ou HEAD)
    if (self.command=='HEAD'):
        http.server.SimpleHTTPRequestHandler.do_HEAD(self)
    else:
        http.server.SimpleHTTPRequestHandler.do_GET(self)

  #     
  # on analyse la requête pour initialiser nos paramètres
  #
  def init_params(self):
    # analyse de l'adresse
    info = urlparse(self.path)
    self.path_info = [unquote(v) for v in info.path.split('/')[1:]]  # info.path.split('/')[1:]
    self.query_string = info.query
    self.params = parse_qs(info.query)

    # récupération du corps
    length = self.headers.get('Content-Length')
    ctype = self.headers.get('Content-Type')
    if length:
      self.body = str(self.rfile.read(int(length)),'utf-8')
      if ctype == 'application/x-www-form-urlencoded' : 
        self.params = parse_qs(self.body)
    else:
      self.body = ''
   
    # traces
    print('path_info =',self.path_info)
    print('body =',length,ctype,self.body)
    print('params =', self.params)

  #
  # On renvoie la liste des pays
  #
  def send_countries(self):
    # création d'un curseur (conn est globale)
    c = conn.cursor()
    
    # récupération de la liste des pays dans la base
    c.execute("SELECT * FROM countries")
    r = c.fetchall()

    # construction de la réponse
    data = []
    n = 0
    for pays in r:
       n += 1
       data.append({'id':n,'lat':pays['latitude'],'lon':pays['longitude'],'name':pays['name'],'wp':pays['wp'],'area':pays['area'],'currency':pays['currency']})
    
    # envoi de la réponse
    headers = [('Content-Type','application/json')]
    self.send(json.dumps(data),headers)


  def send_country(self, country):
    # préparation de la requête SQL
    c = conn.cursor()
    sql = 'SELECT * from countries WHERE wp=?'

    # récupération de l'information (ou pas)
    c.execute(sql,(country,))
    r = c.fetchone()

    # on n'a pas trouvé le pays demandé
    if r == None:
      self.send_error(404,'Country not found')

    else:
      headers = [('Content-Type', 'application/json')]
      attributs = {}
      attributs["name"] = r['name']
      attributs["capital"] = r['capital']
      attributs["latitude"] = r['latitude']
      attributs["longitude"] = r['longitude']
      attributs["currency"] = r['currency']
      attributs["area"] = r['area']
      attributs["wp"] = country
      body = json.dumps(attributs)
      
      self.send(body,headers)

  #
  # On envoie les entêtes et le corps fourni
  #
  def send(self,body,headers=[]):

    # on encode la chaine de caractères à envoyer
    encoded = bytes(body, 'UTF-8')

    # on envoie la ligne de statut
    self.send_response(200)

    # on envoie les lignes d'entête et la ligne vide
    [self.send_header(*t) for t in headers]
    self.send_header('Content-Length',int(len(encoded)))
    self.end_headers()

    # on envoie le corps de la réponse
    self.wfile.write(encoded)

 
#
# Ouverture d'une connexion avec la base de données
#
conn = sqlite3.connect('table_north_america.sqlite')

# Pour accéder au résultat des requêtes sous forme d'un dictionnaire
conn.row_factory = sqlite3.Row

#
# Instanciation et lancement du serveur
#
httpd = socketserver.TCPServer(("", 8080), RequestHandler)
httpd.serve_forever()



        
