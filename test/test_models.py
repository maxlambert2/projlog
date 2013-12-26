from projlog import models
from projlog import db_session
import unittest

class CreateUser(unittest.TestCase):
    u = models.User(username='max',email='maxlambert@gmail.com', password='Cyclone1')
    db_session.add(u)
    db_session.commit(u)