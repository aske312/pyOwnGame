# -*- coding: utf-8 -*-
import psycopg2
from psycopg2 import extras
from configparser import ConfigParser


def config(filename, section):
    parser = ConfigParser()
    parser.read(filename)
    result = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            result[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    return result


class SqlDataBase:
    def __init__(self, base, request):
        self.base = base
        if type(request) == str:
            self.request = request
        else:
            self.request = request
            self.table_name = list(request.keys())
            self.key_table = ", ".join(request[self.table_name[0]].keys())
            self.val_table = ", ".join(request[self.table_name[0]].values())

    def raw(self):
        sql_request = self.request
        return self.connect(sql_request)

    def select(self):
        sql_request = f'''SELECT {self.table_name[0]} FROM {self.key_table} WHERE {self.val_table};'''
        return self.connect(sql_request)

    def drop(self):
        sql_request = f'''DROP TABLE {self.table_name[0]};'''
        return self.connect(sql_request)

    def insert(self):
        sql_request = f'''INSERT INTO {self.table_name[0]} ({self.key_table}) VALUES({self.val_table});'''
        print(sql_request)
        return self.connect(sql_request)

    def create(self):
        sql_request = f'''CREATE TABLE {self.table_name[0]} ({self.key_table});'''
        print(sql_request)
        return self.connect(sql_request)

    def connect(self, execute):
        conn = None
        try:
            conn = psycopg2.connect(**self.base)
            cur = conn.cursor(cursor_factory=extras.DictCursor)
            cur.execute(execute)
            conn.commit()
            sources = cur.fetchall()
            arg = []
            for source in sources:
                if source != 'no results to fetch':
                    arg.append(dict(source))
            cur.close()
            return arg
        except (Exception, psycopg2.DatabaseError) as error:
            pass
        finally:
            if conn is not None:
                conn.close()
