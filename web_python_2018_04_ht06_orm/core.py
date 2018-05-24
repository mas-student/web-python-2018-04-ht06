from collections import OrderedDict
from copy import deepcopy
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


class QuerySet:

    def __init__(self, tablenames, definitions, filters=None, models=None, fields=None):
        self.__models = models if models else []
        self.__fields = fields if fields else []
        print('FIELDS', self.__fields)
        self._tablenames = tablenames
        self._fieldnames = []
        self._definitions = definitions
        ts = []
        for definition in self._definitions:
            if type(definition) == tuple:
                if len(definition) >= 3:
                    ts.append(definition[2])
        print('TS', ts)
        self._filters = filters if filters is not None else {}
        # for definition in definitions:
        #     if type(definition) == tuple:
        #         self._fieldnames.append(definition[0])

    def _get_fieldnames(self):
        # return self._fieldnames
        # return self._fieldnames
        result = []
        for definition in self._definitions:
            if type(definition) == tuple:
                result.append(definition[0])
                if len(definition) >= 3:
                    print('TABLENAME', definition[2])
        return result

    @property
    def names(self):
        return self._get_fieldnames()

    def _get_sql(self):
        ons = []
        for model in self.__models:
            for field in model._get_fields():
                print('MODEL', model, 'FIELD', field)
        # for definition in self._definitions:
        #     if definition[3] and definition[3] in self._tablenames[1:]:
        #         print('ON {}.{} = {}.id'.format(self._tablenames[0], definition[0], definition[3]))

        where = ''
        if len(self._filters) > 0:
            where = 'WHERE {}'.format(', '.join(['{} == "{}"'.format(name, value) for name, value in self._filters.items()]))

        return 'SELECT {select} FROM {from_} {where}'.format(
            select=', '.join(self._get_fieldnames()),
            from_=', '.join(self._tablenames),
            where=where).strip()

    @property
    def sql(self):
        return self._get_sql()

    @classmethod
    def _execute(cls, query):
        conn = connect()
        c = conn.cursor()
        c.execute(query)
        conn.commit()
        return c.fetchall()

    def filter(self, **filters):
        _filters = deepcopy(self._filters)
        _filters.update(filters)
        return QuerySet(
            tablenames=self._tablenames,
            definitions=self._definitions,
            filters=_filters)

    def join(self, model):
        print('JOIN DEFS', self._definitions)
        return QuerySet(
            tablenames=self._tablenames+[model._get_tablename()],
            definitions=self._definitions,
            filters=self._filters)

    def all(self):
        return self._execute(self._get_sql())


class BaseField(object):

    def __init__(self, initval=None, name=None, type=str, tablename=None):
        self.__value = initval
        self.__name = name
        self.__type = type
        self.__tablename = tablename
        self.__foreign = None
        if issubclass(self.__type, BaseModel):
            self.__foreign = self.__type

    def __get__(self, obj, atype=None):
        # print('GET', self, self.__hash__(), obj, type)
        # print('NAME', type.get_name(self))
        name = self.__name
        if name is None:
            name = atype.get_name(self)
        foreign = None
        if issubclass(self.__type, BaseModel):
        # if isinstance(1self.__type, BaseModel):
        # if type(self.__type).__name__ == 'type':
            foreign = self.__type._get_tablename()
            print('foreign', foreign)
        return (name, self.__type, atype._get_tablename(), foreign, self.__value)

    # def __set__(self, obj, val):
    #     print('Updating', self.name)
    #     self.val = val

    @property
    def type(self):
        return self.__type

    @property
    def foreign(self):
        return self.__foreign

    @property
    def name(self):
        return self.__name

    @property
    def tablename(self):
        return self.__tablename

    pass


class BaseModel:

    @classmethod
    def get_name(cls, des):
        for name, field in cls.__dict__.items():
            if field is des:
                return name
        return

    @classmethod
    def _get_class_attrs(cls):
        attrs = []
        for name in sorted(cls.__dict__.keys()):
            if not name.startswith('__'):
                attrs.append((name, cls.__dict__[name]))
                # attrs.append((name, getattr(cls, name)))
                # print('ATTR', attr)
        return attrs

    @classmethod
    def _get_field_dict(cls):
        # return cls._get_class_attrs()
        field_dict = OrderedDict()
        for name, attr in cls._get_class_attrs():
            field_dict[name] = attr
        return field_dict

    @classmethod
    def _get_fields(cls):
        # return cls._get_class_attrs()
        fields = []
        for name, attr in cls._get_class_attrs():
            fields.append(attr)
        return fields

    @property
    def fields(self):
        return self._get_fields()

    @classmethod
    def _field_definitions(cls):
        typeMap = {
            'int': 'int',
            'str': 'text'
        }
        # return [getattr(cls, name) for name in sorted(cls.__dict__.keys()) if not name.startswith('__')]
        # return [(name, getattr(cls, name)[1]) for name in sorted(cls.__dict__.keys()) if not name.startswith('__')]

        defs = []
        # for name in sorted(cls.__dict__.keys()):
        #     if not name.startswith('__'):
        #         attr = getattr(cls, name)
        #         # print('ATTR', attr)
        #         if isinstance(attr, BaseField):
        #             # print('BaseField', attr)
        #             defs.append((attr.name, typeMap.get(attr.type.__name__, attr.type)))
        #         else:
        #             defs.append((name, typeMap.get(attr[1].__name__, attr[1])))
        for name, attr in cls._get_class_attrs():
            if isinstance(attr, BaseField):
                # print('BaseField', attr, attr.type, attr.type.__name__)
                defs.append((name, typeMap.get(attr.type.__name__, attr.type)))
            else:
                defs.append((name, typeMap.get(attr[1].__name__, attr[1])))
        return defs

        # return [(name, typeMap.get(getattr(cls, name)[1].__name__, getattr(cls, name)[1])) for name in sorted(cls.__dict__.keys()) if not name.startswith('__')]


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

        fieldDefinitions = dict(self._field_definitions())
        for key, value in data.items():
            typedef = fieldDefinitions[key]
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
            # print('CREATE', query)
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
    def query(cls, *definitions):
        field_dict = cls._get_field_dict()
        print('FIELD_DICT', field_dict)
        return QuerySet(
            tablenames=[cls._get_tablename()],
            definitions=definitions,
            models=[cls],
            fields=[field_dict.get(definition[0]) for definition in definitions]
        )

    def save(self, verbose=False):
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
                self._get_tablename(),
                ', '.join(['{} = "{}"'.format(k, v) for k, v in fields.items() if k != 'id']),
                # self._tablename(),
                self.id
            )
        else:
            query = 'INSERT INTO {} ({}) VALUES ({})'.format(
                self._get_tablename(),
                ', '.join(['{}'.format(k) for k in fields.keys()]),
                ', '.join(['"{}"'.format(v) for v in fields.values()]),
                # self._tablename(),
                # self.id
            )
        if verbose:
            print('SAVE', '"'+query+'"')
        self._execute(query)
        # print('ALL 2', self._execute('SELECT * FROM {}'.format(self._tablename())))
        return self

    @classmethod
    def all(cls):
        return cls._execute('SELECT * FROM {}'.format(cls._get_tablename()))

    @classmethod
    def first(cls, id):
        records = cls._execute('SELECT * FROM {} WHERE id = "{}"'.format(cls._get_tablename(), id))
        if records:
            return records[0]

    @classmethod
    def _get_tablename(cls):
        return cls.__name__.lower()

    @classmethod
    def migrate(cls):
        # tablename = self.__class__.__name__.lower()
        # self.__create_table(tablename)
        # cls.__create_table(cls._tablename())
        cls._drop_table(cls._get_tablename())
        cls._create_table(cls._get_tablename())


# class FirstModel(BaseModel):
#
#     pass

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
    pass
    # # table(connect())
    # m = FirstModel()
    # m.migrate()


if __name__ == '__main__':
    main()
