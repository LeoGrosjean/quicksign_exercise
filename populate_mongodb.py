#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 13:15:37 2019

@author: LeoH
"""

import argparse
import datetime
import hashlib
import io
import numpy as np
import ray
import requests
from os import path
from PIL import Image


class Populator():
    def __init__(self, app, db, file_path='data/urls.txt'):
        """

        :param app: flask_app
        :param db: mongodb database
        :param file_path: path to a local file
        """
        self.file_path = file_path
        self.app = app
        self.db = db

    def __repr__(self):
        return f"Populator(file_path:{self.file_path})"

    def populatemongo(self):
        """
        Main:
        We use ray to paralelize process
        Loop each line of file and make request on each url/line
        Save a dict of info returned by request and processed to mongodb
        :return: Boolean True if no cpu available
        """
        db = self.db
        ray.init(ignore_reinit_error=True)
        if len(ray.available_resources().keys()) == 0:
            self.app.logger.info(f'No CPU available <populatemongo>')
            return True
        elif 'CPU' in ray.available_resources().keys():
            availables_cpus = ray.available_resources()['CPU']
            self.app.logger.info(f'Number of CPU available : {availables_cpus}')
        instruction = []
        for i, line in enumerate(readfile(self.file_path)):
            instruction.append(requesturl.remote(line))
            if i%(availables_cpus*2) == 0:
                self.app.logger.info(f'DOWNLOADING {i}')
                items = [item for item in ray.get(instruction)]
                instruction = []
                loopitems(items, db)
        if len(instruction) != 0:
            self.app.logger.info(f'Final images are downloading...')
            items = [item for item in ray.get(instruction)]
            loopitems(items, db)
        ray.shutdown()
        return False

def readfile(path: str):
    """
    yield lines of a file
    :param path: path to a local file
    :return: an url
    """
    with open(path) as file:
        for line in file.readlines():
            yield line.strip()

@ray.remote
def requesturl(url):
    """
    Request on an url and extract Image and other informations
    :param url: "https://picsum.photos/259/260"
    :return: a dict to be stored in mongodb
    """
    r = requests.get(url)
    text = r.text.strip()
    try:
        image = Image.open(io.BytesIO(r.content))
        return {
            'source_url': url,
            'url': r.url,
            'md5': getmd5(image),
            'img_grey': image_to_byte_array(convertgrey(image)),
            'height': image.height,
            'width': image.width,
            'datetime_created': datetime.datetime.now()
        }
    except:
        if 'Error' in text:
            text = find_between(text)

        return {
            'error': text,
            'source_url': url,
            'url': r.url,
            'datetime_created': datetime.datetime.now()
        }

def getmd5(image: Image):
    """
    Convert image bytes to md5 string
    :param image: <class 'PIL.Image.Image'>
    :return: md5 string
    """
    return hashlib.md5(image.tobytes()).hexdigest()

def convertgrey(image: Image):
    """
    Convert an image to grey (R+G+B)/3 using numpy
    :param image: <class 'PIL.Image.Image'>
    :return: <class 'PIL.Image.Image'>
    """
    matrice = np.asarray(image)
    matrice = np.mean(matrice, axis=2, dtype=np.uint8)
    return Image.fromarray(matrice)

def loopitems(items, db):
    """
    Iter on items and call saveimage depending on error value
    :param items: list of dict
    :param db: <class 'pymongo.database.Database'>
    :return: None
    """
    for item in items:
        if 'error' in item.keys():
            saveimage(item, db, 'collection_image_status')
        else:
            if checkfieldunicity(db, item['md5']):
                saveimage(item, db, 'collection_image')
                saveimage(itemstatus(item, error='RAS'),
                          db,
                          'collection_image_status')
            else:
                saveimage(itemstatus(item), db, 'collection_image_status')

def saveimage(item, db, collection):
    """
    Save an item to a mongodb collection
    :param item: <dict>
    :param db: <class 'pymongo.database.Database'>
    :param collection: <class 'pymongo.collection.Collection'>
    :return: None
    """
    db[collection].insert(item)

def image_to_byte_array(image: Image, f='JPEG'):
    """
    Tranform an image to bytes object
    :param image: <class 'PIL.Image.Image'>
    :param f: Image format in string
    :return: <class 'bytes'>
    """
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, format=f)
    imgByteArr = imgByteArr.getvalue()
    return imgByteArr

def checkfieldunicity(db, value, fieldname='md5', collection='collection_image'):
    """
    Check if an item exist in collection based on unique field (md5 default)
    :param db: <class 'pymongo.database.Database'>
    :param value: value of item to count
    :param fieldname: keys of item to count
    :param collection: <class 'pymongo.collection.Collection'>
    :return: boolean
    """
    return db[collection].find({fieldname: value}).count() == 0

def itemstatus(item, error='Duplicate MD5'):
    """
    Modify input dict to another dict with an error and fewer keys sometimes
    :param item: dict
    :param error: string with "request status"
    :return: dict
    """
    item = {
        'md5': item['md5'],
        'error': error,
        'source_url': item['source_url'],
        'url': item['url'],
        'datetime_created': item['datetime_created']
    }
    return item

def find_between(s, first='<title>', last='</title>'):
    """
    get string between two string
    :param s: string
    :param first: string
    :param last: string
    :return: string
    """
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return s

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="path to urls file")
    args = parser.parse_args()

    if path.exists(args.path):
        Populator(args.path).populatemongo()
    else:
        print("File don't exist, please check your path !")
    print('MongoDb is now populated !')
