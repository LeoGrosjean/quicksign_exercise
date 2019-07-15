# Quicksign Exercise
## Sujet

Developper un workflow asynchrone de distribution de taches en python3 sous docker.

Objectifs:
- Recuperer les images accessibles par les urls contenues dans le fichier urls.txt.
- Developper une tache qui calculera la MD5 de l'image
- Developper une tache qui transformera l'image en niveau de gris avec le calcul suivant: (R + G + B) / 3
- Developper une tache qui recuperera les outputs des deux precedents workers. Il devra egalement inserer dans une base
de donnees MongoDB, les informations (md5, l'image en niveau de gris, la hauteur et la largeur de l'image, la date d'insertion).
- Developper une api en Flask pour visualiser les images stockees dans MongoDB via l'url http://localhost:5000/image/<MD5>
- Developper une api en Flask de monitoring via l'url http://localhost:5000/monitoring. Cette api devra retourner un
histogramme decrivant le nombre d'images traitees avec succes ou erreur par interval d'une minute. (Prevoir une collection dans MongoDB pour recuperer ces informations)


Notes:
- Certaines URLs retournent une erreur
- Il ne doit pas y avoir de doublons d'image dans la base MongoDB (unicite du MD5)
- Les technologies autres que celles citees sont libres
- Le travail sera rendu sur un repo git public

## Installation

It uses Docker-compose: 

Compose is a tool for defining and running complex applications with Docker. 

With Compose, you define a multi-container application in a single file, then spin your application up in a single command which does everything that needs to be done to get it running.

[Docker Install](https://docs.docker.com/compose/install/)

After installing Docker and Docker-compose on your machine, you can go to the project main folder and type:
```bash
docker-compose up
```

## Usage

Run locally at :

[localhost:5000](http://localhost:5000/)


### Endpoints
- [/](http://localhost:5000/) - Populate MongoDb (click button)
- [/randomimage](http://localhost:5000/randomimage) - Display a random image if mongodb is not empty
- [/image/<MD5>](http://localhost:5000/image/<MD5>) - Display an image with defined MD5
- [/monitoring](http://localhost:5000/monitoring) - Monitoring images ingestion
- [/testmonitoring](http://localhost:5000/testmonitoring) - Diplay html generated by altair
