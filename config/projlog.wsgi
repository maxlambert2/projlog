#!/usr/bin/python
import sys, os
import logging

logging.basicConfig(stream=sys.stderr)
sys.path.append('/home/fochiller/projlog/')
os.environ["PROJLOG_SETTINGS"] = '/home/fochiller/projlog/config/prod.py'

from app import app as application

