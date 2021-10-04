import json
import pronotepy
import datetime
import json
import hashlib
from requests import *
from pronotepy.ent import ac_orleans_tours

##############################    A modifier    ###############################################
nc_auth = ('NOM UTILISATEUR','MOTDEPASSE')
pronote = {
    'url': 'https://EXAMPLE.index-education.net/pronote/eleve.html',
    'username': 'NOM UTILISATEUR',
    'password': 'MOTDEPASSE',
}
nextcloud = {
    'baseUrl': 'https://nextcloud.example.com',
    'boardID': 3,
    'stackID': 4
}
# ENT à configurer ici
client = pronotepy.Client(pronote['url'] ,username=pronote['username'] ,password=pronote['password'] ,ent=ac_orleans_tours)
###############################################################################################
nc_headers = {'content-type': 'application/json'}
if client.logged_in:
    r = get(f"{nextcloud['baseUrl']}/index.php/apps/deck/api/v1.0/boards/{nextcloud['boardID']}/stacks/{nextcloud['stackID']}", auth=nc_auth, headers=nc_headers)
    already_registered = []
    count = {"new": 0, 'already':0}
    resp = r.json()
    try:
        for i in resp['cards']:
            already_registered.append(i["description"][-32:])
    except KeyError: pass
    print(already_registered)
    for i in client.homework(datetime.date.today()+datetime.timedelta(days=1), datetime.date.today()+datetime.timedelta(days=7)):
        hash = hashlib.md5(i.description.encode('utf-8')).hexdigest()
        if hash in already_registered: 
            count["already"] +=1
            print(i.id,'already')
        else:
          print(i.id,'new')
          data = {"order":999}
          if len(i.subject.name) + len(i.description) < 200:
              data["title"] = f"{i.subject.name} : {i.description}"
              data["description"]=""
          else:
              data["title"] = i.subject.name
              data["description"] = i.description
          data["duedate"] = datetime.datetime.combine(i.date, datetime.time(8,0,0)).strftime('%Y-%m-%dT%H:%M:%S.%f%z')
          data["description"] += "\n\n\n"
          data["description"] += hash
          data = json.dumps(data)
          r = post(f"{nextcloud['baseUrl']}/index.php/apps/deck/api/v1.0/boards/{nextcloud['boardID']}/stacks/{nextcloud['stackID']}/cards", auth=nc_auth, headers=nc_headers, data=data)
          count["new"]+=1
    print(count)

