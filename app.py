import os
from flask import Flask, abort, send_file, g, request, redirect, jsonify, render_template
from bson.objectid import ObjectId
from flasgger.utils import swag_from
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

from mongoengine import connect, Q
from urllib.parse import urlencode
from dotenv import load_dotenv
from flask_cors import CORS


def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)

    CORS(app)

    load_dotenv()

    connect('dev', alias='default', host=os.getenv('MONGO_URL'))
