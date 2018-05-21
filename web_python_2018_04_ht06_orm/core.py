from collections import OrderedDict
import sqlite3


class BaseModel:

    def __init__(self, id=0):
        self.id = id
        if id != 0:
            record = self.first(id)
            if record:
                print('R', record)
                for name, value in zip([c[0] for c in self._columns()], record):
                    setattr(self, name, value)

    @classmethod
    def _execute(cls, query):
        conn = connect()
        c = conn.cursor()
        c.execute(query)
        conn.commit()
        return c.fetchall()

    @classmethod
    def __create_table(cls, tablename):
        print('TN', tablename)

        # conn = connect()
        # c = conn.cursor()

        try:
            # c.execute('DROP TABLE ?', (tablename, ))
            # c.execute('DROP TABLE {}'.format(tablename))
            query = 'DROP TABLE {}'.format(tablename)
            cls._execute(query)
            print('DROP', tablename)
        except Exception as e:
            print(e)

        try:
            # Create table
            # c.execute('''CREATE TABLE ? (key text)''', (tablename, ))
            # query = '''CREATE TABLE {} (key text)'''.format(tablename)
            query = 'CREATE TABLE {}({})'.format(
                tablename,
                ', '.join(' '.join(v) for v in cls._columns()))
            # c.execute(query)
            cls._execute(query)
            print('CREATE', query)
        except Exception as e:
            print(e)

        print('OK')
        # conn.commit()

    @classmethod
    def _columns(cls):
        return [getattr(cls, name) for name in cls.__dict__.keys() if not name.startswith('__')]

    def save(self):
        fields = OrderedDict()
        print('ALL 1', self._execute('SELECT * FROM {}'.format(self._tablename())))
        for field in self._columns():
            print('F', field)
            fields[field[0]] = getattr(self, field[0])

        if self.first(self.id):
            query = 'UPDATE {} SET {} WHERE id = {}'.format(
                self._tablename(),
                ', '.join(['{} = "{}"'.format(k, v) for k, v in fields.items() if k != 'id']),
                # self._tablename(),
                self.id
            )
        else:
            query = 'INSERT INTO {} ({}) VALUES ({})'.format(
                self._tablename(),
                ', '.join(['{}'.format(k) for k in fields.keys()]),
                ', '.join(['"{}"'.format(v) for v in fields.values()]),
                # self._tablename(),
                # self.id
            )
        print('SAVE', '"'+query+'"')
        self._execute(query)
        print('ALL 2', self._execute('SELECT * FROM {}'.format(self._tablename())))

    @classmethod
    def all(cls):
        return cls._execute('SELECT * FROM {}'.format(cls._tablename()))

    @classmethod
    def first(cls, id):
        records = cls._execute('SELECT * FROM {} WHERE id = "{}"'.format(cls._tablename(), id))
        if records:
            return records[0]

    @classmethod
    def _tablename(cls):
        return cls.__name__.lower()

    @classmethod
    def migrate(cls):
        # tablename = self.__class__.__name__.lower()
        # self.__create_table(tablename)
        cls.__create_table(cls._tablename())


class FirstModel(BaseModel):

    pass

def connect():
    conn = sqlite3.connect('local.db')
    return conn

def table(conn):
    c = conn.cursor()

    # try:
    #     c.execute('DROP TABLE stocks')
    # except:
    #     pass
    #
    # try:
    #     # Create table
    #     c.execute('''CREATE TABLE stocks
    #                  (date text, trans text, symbol text, qty real, price real)''')
    # except:
    #     pass

    # Insert a row of data
    c.execute("INSERT INTO stocks(date, trans, symbol, qty, price) VALUES ('2006-01-05','BUY','RHAT',100,35.14)")

    # Save (commit) the changes
    conn.commit()

    t = ('RHAT',)
    c.execute('SELECT * FROM stocks WHERE symbol=?', t)
    # conn.execute('SELECT * FROM stocks')
    record = c.fetchone()
    # record = c.fetchall()
    # print(record)

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()

    return record

def main():
    # table(connect())
    m = FirstModel()
    m.migrate()



if __name__ == '__main__':
    main()
