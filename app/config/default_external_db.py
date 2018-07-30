import os

"""
DB Config
"""
EXTERNAL_DATABASE_URI = 'postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{name}'.format(
    user=os.environ.get('DBUSER', ''),
    pwd=os.environ.get('DBPASS', ''),
    host=os.environ.get('DBHOST', ''),
    port=os.environ.get('DBPORT', 9999),
    name=os.environ.get('DBNAME', '')
)
