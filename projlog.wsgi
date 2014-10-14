#!/usr/bin/python
import sys, os
import logging

logging.basicConfig(stream=sys.stderr)
sys.path.append('/home/fochiller/projlog/')
os.environ["PROJLOG_SETTINGS"] = '/home/fochiller/projlog/config/prod.py'

os.environ["PROJLOG_SECRET_KEY"]="kastdgsfd&uupplilc)$7p+5mzmdu89fe804rot8!1o)^-p)!)$xsl"
os.environ["DB_POSTGRES_PASS"]="Cycl0n#"
os.environ["AWS_STORAGE_BUCKET_NAME"]="projlog"
os.environ["AWS_ACCESS_KEY_ID"]="AKIAJIFJLMOEHNCLFPCA"
os.environ["AWS_SECRET_ACCESS_KEY"]="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"

from app import app as application

