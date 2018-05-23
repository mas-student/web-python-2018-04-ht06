from collections import OrderedDict
import sqlite3


def escape():
    pass

class Scheme:
    def __init__(self):
        self.__models = OrderedDict()

    def add(self, model):
        self.__models[model.__name__] = model

    def migrate(self):
        for name, model in self.__models.items():
            model.migrate()


class FieldDefinition:
    pass


class QuerySet:

    def __init__(self, tablename, definitions):
        self._tablename = tablename
        self._fieldnames = []
        for definition in definitions:
            if type(definition) == tuple:
                self._fieldnames.append(definition[0])

    @property
    def names(self):
        return self._fieldnames

    @property
    def _sql(self):
        return 'SELECT {} FROM {}'.format(', '.join(self._fieldnames), self._tablename)

    @classmethod
    def _execute(cls, query):
        conn = connect()
        c = conn.cursor()
        c.execute(query)
        conn.commit()
        return c.fetchall()

    def all(self):
        return self._execute(self._sql)


class BaseModel:

    def __init__(self, scheme=None, id=0, record=None, data=None):
        self.id = id
        if scheme:
            scheme.add(type(self))
        if id != 0:
            record = self.first(id)
            if record:
                self._load_from_record(record)
                # # print('R', record)
                # # for name, value in zip([c[0] for c in self._columns()], record):
                # #     setattr(self, name, value)
                # for (name, typedef), value in zip([c for c in self._columns()], record):
                #     if type(typedef) == type:
                #         value = typedef.first(value)
                #     setattr(self, name, value)
        if record:
            self._load_from_record(record)
        if data:
            self._load_from_data(data)

    def _load_from_data(self, data):
        # keys = data.keys()
        # record = [data[key] for key in keys]
        # self._load_from_record(record)

        columnMap = dict(self._field_definitions())
        for key, value in data.items():
            typedef = columnMap[key]
            if type(typedef) == type:
                value = typedef.first(value)
            setattr(self, key, value)

    def _load_from_record(self, record):
        for (name, typedef), value in zip([c for c in self._field_definitions()], record):
            if type(typedef) == type:
                value = typedef.first(value)
            setattr(self, name, value)

    @classmethod
    def _execute(cls, query):
        conn = connect()
        c = conn.cursor()
        c.execute(query)
        conn.commit()
        return c.fetchall()

    @classmethod
    def _create_table(cls, tablename):
        # print('TN', tablename)

        # conn = connect()
        # c = conn.cursor()

        # try:
        #     # c.execute('DROP TABLE ?', (tablename, ))
        #     # c.execute('DROP TABLE {}'.format(tablename))
        #     query = 'DROP TABLE {}'.format(tablename)
        #     cls._execute(query)
        #     # print('DROP', tablename)
        # except Exception as e:
        #     print(e)

        try:
            # Create table
            # c.execute('''CREATE TABLE ? (key text)''', (tablename, ))
            # query = '''CREATE TABLE {} (key text)'''.format(tablename)
            columns = cls._field_definitions()
            for i in range(len(columns)):
                # print(type(columns[i][1]), str(type(columns[i][1])))
                if str(type(columns[i][1])) == "<class 'type'>": # FIXME
                    columns[i] = columns[i][0], 'int'
            # print('COLUMNS', columns)
            query = 'CREATE TABLE {}({})'.format(
                tablename,
                ', '.join(' '.join(v) for v in columns))
            # c.execute(query)
            cls._execute(query)
            print('CREATE', query)
        except Exception as e:
            print(e)

        # print('OK')
        # conn.commit()

    @classmethod
    def _drop_table(cls, tablename):
        try:
            # c.execute('DROP TABLE ?', (tablename, ))
            # c.execute('DROP TABLE {}'.format(tablename))
            query = 'DROP TABLE {}'.format(tablename)
            cls._execute(query)
            # print('DROP', tablename)
        except Exception as e:
            print(e)

    @classmethod
    def _field_definitions(cls):
        return [getattr(cls, name) for name in sorted(cls.__dict__.keys()) if not name.startswith('__')]

    def query(self, *definitions):
        return QuerySet(self._tablename(), definitions)

    def save(self, verbose=True):
        fields = OrderedDict()
        # print('ALL 1', self._execute('SELECT * FROM {}'.format(self._tablename())))
        for field in self._field_definitions():
            # print('F', field)
            value = getattr(self, field[0])
            if isinstance(value, BaseModel):
                value = value.id
            fields[field[0]] = value

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
        if verbose:
            print('SAVE', '"'+query+'"')
        self._execute(query)
        # print('ALL 2', self._execute('SELECT * FROM {}'.format(self._tablename())))

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
        # cls.__create_table(cls._tablename())
        cls._drop_table(cls._tablename())
        cls._create_table(cls._tablename())


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
