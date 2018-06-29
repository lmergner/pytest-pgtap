import subprocess
import shlex
import pytest

# xxx: are we actually using this?
pytest_plugins = ['pytester']


# def get_dbname(config):
#     return config.getoption('pgtap_uri').split('/')[-1]


# @pytest.hookimpl(trylast=True)
# def pytest_configure(config):
#     dbname = get_dbname(config)
#     try:
#         subprocess.run(shlex.split('dropdb -e --if-exists ' + dbname), check=True)
#         subprocess.run(shlex.split('createdb -e ' + dbname), check=True)
#         subprocess.run(shlex.split(
#             'psql -a -d ' + dbname + ' -f tests/setup.sql'), check=True)
#             # yield
#     except subprocess.CalledProcessError as e:
#         # TODO: handle in pytestable way
#         raise


# @pytest.hookimpl(trylast=True)
# def pytest_unconfigure(config):
#     dbname = get_dbname(config)
#     subprocess.run(shlex.split('dropdb -e --if-exists ' + dbname), check=True)


# # https://github.com/ClearcodeHQ/pytest-postgresql/blob/master/src/pytest_postgresql/factories.py
# def drop_postgresql_database(user, host, port, db, version):

#     conn = psycopg2.connect(user=user, host=host, port=port)
#     conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
#     cur = conn.cursor()
#     # We cannot drop the database while there are connections to it, so we
#     # terminate all connections first while not allowing new connections.
#     if float(version) >= 9.2:
#         pid_column = 'pid'
#     else:
#         pid_column = 'procpid'
#     cur.execute(
#         'UPDATE pg_database SET datallowconn=false WHERE datname = %s;',
#         (db,))
#     cur.execute(
#         'SELECT pg_terminate_backend(pg_stat_activity.{0})'
#         'FROM pg_stat_activity WHERE pg_stat_activity.datname = %s;'.format(
#             pid_column),
#         (db,))
#     cur.execute('DROP DATABASE IF EXISTS {0};'.format(db))
#     cur.close()
#     conn.close()
