# -*- coding: utf-8 -*-
from os import environ, path, getcwd
from base64 import b64decode

from athome.items import PropertyAnnouce
from scrapy.exporters import BaseItemExporter

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

import logging

_logger = logging.getLogger(__name__)

class FirebasePipeline(BaseItemExporter):

    def load_spider(self, spider):
        self.crawler = spider.crawler
        self.settings = spider.settings
        self.keys = self.settings['FIREBASE_KEYS']

    def open_spider(self, spider):
        self.load_spider(spider)

        filename = path.normpath(path.join(getcwd(), 'firebase_secrets.json'))
        with open(filename, "w") as json_file:
            json_file.write(b64decode(self.settings['FIREBASE_SECRETS']))

        configuration = {
            'credential': credentials.Certificate(filename),
            'options': {'databaseURL': self.settings['FIREBASE_DATABASE']}
        }

        firebase_admin.initialize_app(**configuration)
        self.raw_ref = db.reference(spider.firebase_raw_collection)
        self.ref = db.reference(self.settings['FIREBASE_REF'])

    def process_item(self, item, spider):
        if isinstance(item, PropertyAnnouce):
            child = self.ref.child(item['id'])
            item = dict(self._get_serialized_fields(item))
            child.set(item)
            _logger.info("Item %s stored as announce into firebase" % item['id'])
        else :
            item = dict(self._get_serialized_fields(item))
            child = self.raw_ref.child('/'.join([item[key] for key in self.keys]))
            child.set(item)
            _logger.info("Item %s stored as raw into firebase" % item['id'])
        
        return item

    def close_spider(self, spider):
        pass
