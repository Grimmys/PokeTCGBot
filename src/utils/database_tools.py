import psycopg2.extras
from contextlib import contextmanager

from pypika.terms import Function


class JsonAggregate(Function):
    def __init__(self, array):
        super(JsonAggregate, self).__init__('json_agg', array)


class JsonBuildArray(Function):
    def __init__(self, *args, alias=None):
        super(JsonBuildArray, self).__init__('json_build_array', *args, alias=alias)


@contextmanager
def get_cursor(connection_pool):
    connection = connection_pool.getconn()
    try:
        yield connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    finally:
        connection.commit()
        connection_pool.putconn(connection)
