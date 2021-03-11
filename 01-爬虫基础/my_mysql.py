import pymysql
import time
import logging
import traceback


class MySqlHelper(object):
    """
    max_idle_time 数据库连接时长
    """
    def __init__(self,host,database,user=None,password=None,port=3306,
                 max_idle_time = 7*3600,
                 connect_timeout = 10,
                 time_zone = "+0:00",charset='utf8mb4',sql_mode="TRADITIONAL"
                 ):
        self.host = host
        self.database = database
        self.max_idle_time = float(max_idle_time)

        args = dict(use_unicode=True,charset=charset,database=database,
                    init_command="set time_zone = '%s'"%(time_zone),
                    cursorclass=pymysql.cursors.DictCursor,
                    connect_timeout=connect_timeout,sql_mode=sql_mode)
        if user is not None:
            args['user'] = user
        if password is not None:
            args['password'] = password

        if "/" in host:
            args['unix_socket'] = host
        else:
            self.socket = None
            pair = host.split(':')
            if len(pair) == 2:
                args['host'] = pair[0]
                args['port'] = int(pair[1])
            else:
                args['host'] = host
                args['port'] = 3306
        if port:
            args['port'] = port

        self._db = None
        self._db_args = args
        self._last_use_time = time.time()
        try:
            self.reconnect()
        except Exception:
            logging.error('cannot connect to mysql no %s'%(self.host),exc_info=True)

    def _ensure_connected(self):
        if (self._db is None or (time.time() - self._last_use_time > self.max_idle_time)):
            self.reconnect()
        self._last_use_time = time.time()

    def _cursor(self):
        self._ensure_connected()
        return self._db.cursor()

    def __del__(self):
        self.close()

    def close(self):
        if getattr(self,"_db",None) is not None:
            self._db.close()
            self._db = None

    def reconnect(self):
        self.close()
        self._db = pymysql.connect(**self._db_args)
        self._db.autocommit(True)

    def query(self,query,*parameters,**kwparameters):
        cursor = self._cursor()
        try:
            cursor.excute(query,kwparameters or parameters)
            result = cursor.fetchall()
            return result
        finally:
            cursor.close()

    def get(self,query,*parameters,**kwparameters):
        cursor = self._cursor()
        try:
            cursor.execute(query, kwparameters or parameters)
            return cursor.fetchone()
        finally:
            cursor.close()

    def execute(self, query, *parameters, **kwparameters):
        cursor = self._cursor()
        try:
            cursor.execute(query, kwparameters or parameters)
            return cursor.lastrowid
        except Exception as e:
            if e.args[0] == 1062:
                pass
            else:
                traceback.print_exc()
                raise e
        finally:
            cursor.close()

    def table_has(self, table_name, field, value):
        if isinstance(value, str):
            value = value.encode('utf8')
        sql = 'SELECT %s FROM %s WHERE %s="%s"' % (
            field,
            table_name,
            field,
            value)
        d = self.get(sql)
        return d

    def table_insert(self, table_name, item):

        fields = list(item.keys())
        values = list(item.values())
        fieldstr = ','.join(fields)
        valstr = ','.join(['%s'] * len(item))
        for i in range(len(values)):
            if isinstance(values[i], str):
                values[i] = values[i].encode('utf8')
        sql = 'INSERT INTO %s (%s) VALUES(%s)' % (table_name, fieldstr, valstr)
        try:
            last_id = self.execute(sql, *values)
            return last_id
        except Exception as e:
            if e.args[0] == 1062:
                # just skip duplicated item
                pass
            else:
                traceback.print_exc()
                print('sql:', sql)
                print('item:')
                for i in range(len(fields)):
                    vs = str(values[i])
                    if len(vs) > 300:
                        print(fields[i], ' : ', len(vs), type(values[i]))
                    else:
                        print(fields[i], ' : ', vs, type(values[i]))
                raise e

    def table_update(self, table_name, updates,
                     field_where, value_where):
        '''updates is a dict of {field_update:value_update}'''
        upsets = []
        values = []
        for k, v in updates.items():
            s = '%s=%%s' % k
            upsets.append(s)
            values.append(v)
        upsets = ','.join(upsets)
        sql = 'UPDATE %s SET %s WHERE %s="%s"' % (
            table_name,
            upsets,
            field_where, value_where,
        )
        self.execute(sql, *(values))

if __name__ == '__main__':
    db = MySqlHelper('host','db','username','password')

    sql = 'select * from table_name where id=%s'
    data = db.get(sql,2)
    print(data)