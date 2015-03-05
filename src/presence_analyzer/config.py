"""
Configuration file.
"""
import os.path

USERS_XML_URL = 'http://sargo.bolt.stxnext.pl/users.xml'
USERS_XML_DIR = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data',
)
USERS_XML_FILE = os.path.join(
    USERS_XML_DIR, 'users.xml'
)
USERS_TEST_XML_FILE = os.path.join(
    USERS_XML_DIR, 'users_test.xml'
)
