from collections import OrderedDict
from copy import deepcopy
from itertools import chain
from functools import reduce
import sqlite3


def connect(): # FIXME
    conn = sqlite3.connect('local.db')
    return conn

def pack(values):
    return reduce(lambda acc, val: acc + [val] if val not in acc else acc, values, [])

def escape():
    pass

def dump(obj):
    from pprint import pformat # FIXME
    print('__DICT__', pformat(obj.__dict__))
    print('LOCALS', pformat(locals()))


class BaseField(object):

    def __init__(self, name=None, type=str, model=None, tablename=None, foreign=None, default=None):
        self.__default = default
        self.__name = name
        self.__type = type
        self.__model = model
        self.__tablename = tablename
        self.__foreign = foreign

        if issubclass(self.__type, BaseModel):
            self.__foreign = self.__type

    def __str__(self):
        return '<BaseField {}.{}>'.format(self.__model.tablename if self.__model else None, self.__name)

    def __unicode__(self):
        return self.__str__()

    def __repr__(self):
        return 'BaseField(name="{}", type={}, model={})'.format(self.__name, self.__type.__name__, self.__model.__name__)

    def __get__(self, obj, model=None):
        name = self.__name
        if name is None:
            name = model.get_field_name(self)
        foreign = None
        if issubclass(self.__type, BaseModel):
            foreign = self.__type

        if not obj:
            return BaseField(name=name, type=self.__type, model=model, tablename=self.__tablename, foreign=foreign, default=self.__default)

        return obj.get_value(name)

    @property
    def model(self):
        return self.__model

    @property
    def definition(self):
        return (self.__name, self.__type, self.__model, self.__foreign, self.__default)

    def __set__(self, model, val):
        if not model:
            raise TypeError('SET', model)
        name = self.__name
        if name is None:
            name = model.get_field_name(self)
        model._values[name] = val

    @property
    def name(self):
        return self.__name

    @property
    def type(self):
        return self.__type

    @property
    def foreign(self):
        return self.__foreign

    @property
    def tablename(self):
        return self.__tablename

    # @property
    # def value(self):
    #     return self.__model.get_value(self.__name)

    pass


class BaseModel:

    @classmethod
    def get_field_name(cls, field):
        for k, v in sorted(cls.__dict__.items(), key=lambda item: item[0]):
            if v is field:
                return k
        return

    @classmethod
    def _get_class_attr_names(cls):
        return [name for name in sorted(cls.__dict__.keys()) if not name.startswith('__')]

    @classmethod
    def _get_class_attrs(cls):
        return [(name, cls.__dict__[name]) for name in cls._get_class_attr_names()]

    @classmethod
    def _get_field_dict(cls):
        field_dict = OrderedDict()
        for name, attr in cls._get_class_attrs():
            field_dict[name] = attr
        return field_dict

    @classmethod
    def _get_fields(cls):
        fields = []
        for key, value in cls.__dict__.items():
            if isinstance(value, BaseField):
                fields.append(getattr(cls, key))
        return sorted(fields, key=lambda field: field.name)

    @classmethod
    def _get_field(cls, name):
        for key, value in cls._get_class_attrs():
            if key == name:
                return value
        return

    @classmethod
    def _get_column_defintions(cls):
        typeMap = {
            'int': 'int',
            'str': 'text'
        }
        
        defintions = []
        for field in cls._get_fields():
            defintions.append((field.name, typeMap.get(field.type.__name__, field.type)))
        return defintions

    @classmethod
    def _get_field_definitions(cls):
        return [getattr(cls, name).definition for name in cls._get_class_attr_names()]

    @classmethod
    def all(cls):
        return cls._execute('SELECT * FROM {}'.format(cls._get_tablename()))

    @classmethod
    def first(cls, id):
        return cls._first(id)

    @classmethod
    def get(cls, id):
        records = cls._execute('SELECT * FROM {} WHERE id = "{}"'.format(cls._get_tablename(), id))

        if len(records) == 0:
            raise Exception('{} has not record with id = {}'.format(cls.__name__, id))

        return cls(record=records[0])

    @classmethod
    def query(cls, *fields):
        return QuerySet(
            cls
        )

    @classmethod
    def _get_tablename(cls):
        return cls.__name__.lower()

    @property
    def tablename(self):
        return type(self)._get_tablename()

    @classmethod
    def migrate(cls):
        cls._drop_table(cls._get_tablename())
        cls._create_table(cls._get_tablename())

    @classmethod
    def _execute(cls, query, existed=True):
        conn = connect()
        c = conn.cursor()

        c.execute('SELECT name FROM sqlite_master')

        if existed:
            sql = 'SELECT name FROM sqlite_master WHERE type=\'table\' AND name=\'{table_name}\''.format(
                table_name=cls._get_tablename())
            c.execute(sql)
            if len(list(c.fetchall())) == 0:
                raise LookupError('Table {} does not exist'.format(cls._get_tablename()))

        c.execute(query)
        conn.commit()
        return c.fetchall()

    @classmethod
    def _create_table(cls, tablename):
        try:
            columns = cls._get_column_defintions()
            for i in range(len(columns)):
                if str(type(columns[i][1])) == "<class 'type'>": # FIXME
                    columns[i] = columns[i][0], 'int'
            query = 'CREATE TABLE {}({})'.format(
                cls._get_tablename(),
                ', '.join(' '.join(v) for v in columns))
            cls._execute(query, existed=False)

        except Exception as e:
            print(e)

    @classmethod
    def _drop_table(cls, tablename):
        try:
            query = 'DROP TABLE {}'.format(tablename)
            cls._execute(query)

        except Exception as e:
            print(e)

    @classmethod
    def _first(cls, pk):
        records = cls._execute('SELECT * FROM {} WHERE id = "{}"'.format(cls._get_tablename(), pk))
        if records:
            return records[0]

    @classmethod
    def _insert(cls, **values):
        query = 'INSERT INTO {} ({}) VALUES ({})'.format(
            cls._get_tablename(),
            ', '.join(['{}'.format(k) for k in values.keys()]),
            ', '.join(['"{}"'.format(v) for v in values.values()]),
        )
        return cls._execute(query)

    @classmethod
    def _update(cls, pk, **values):
        query = 'UPDATE {} SET {} WHERE id = "{}"'.format(
            cls._get_tablename(),
            ', '.join(['{} = "{}"'.format(k, v) for k, v in values.items()]),
            pk
        )
        return cls._execute(query)

    @classmethod
    def _delete(cls, pk, **values):
        query = 'DELETE FROM {} WHERE id == "{}";'.format(cls._get_tablename(), pk)
        return cls._execute(query)

    @classmethod
    def create(cls):
        cls._create_table(cls._get_tablename())

    @classmethod
    def drop(cls):
        cls._drop_table(cls._get_tablename())

    def __init__(self, record=None, data=None):
        self._values = {}

        if record:
            self._load_from_record(record)

        if data:
            self._load_from_data(data)

        pass # __init__

    def _load_from_data(self, data):
        column_defintions = dict(self._get_column_defintions())
        for key, value in data.items():
            typedef = column_defintions[key]
            if type(typedef) == type:
                value = typedef.first(value)
            setattr(self, key, value)

    def _load_from_record(self, record):
        for (name, column_defintion), value in zip([c for c in self._get_column_defintions()], record):
            if type(column_defintion) == type:
                value = column_defintion.first(value)
            setattr(self, name, value)

    def _get_pk(self):
        return self.id

    def _get_values(self):
        return tuple([self._values.get(field.name) for field in type(self)._get_fields()])

    def get_value(self, name):
        return self._values[name]

    def set_value(self, name, value):
        self._values[name] = value

    @property
    def pk(self):
        return self._get_pk()

    @property
    def fields(self):
        return self._get_fields()

    @property
    def values(self):
        return self._get_values()

    def save(self):
        values = OrderedDict()
        for key, value in self._values.items():
            if isinstance(value, BaseModel):
                value = value.pk
            values[key] = value

        if self.first(self.pk):
            type(self)._update(self.pk, **values)
        else:
            type(self)._insert(**values)
        return self

    def delete(self):
        type(self)._delete(self._get_pk())


class QuerySet:

    @staticmethod
    def _pack_models(models):
        result = []
        for model in models:
            if model not in result:
                result.append(model)
        return result

    def __init__(self, *models, joins=None, filters=None):
        self.__models = list(models)
        self.__joins = joins if joins is not None else []
        self._tablenames = [model._get_tablename() for model in self.__models]
        self._fieldnames = []
        self.__filters = filters if filters is not None else {}

    def _get_sql(self):
        if not self.__models:
            raise Exception('No models')

        main_tablename = self.__models[0]._get_tablename()

        tablenames = [model._get_tablename() for model in self.__models]
        for join in self.__joins:
            if type(join) == type and issubclass(join, BaseModel):
                tablename = join._get_tablename()
            elif isinstance(join, BaseField) and join.foreign:
                tablename = join.foreign._get_tablename()
            else:
                raise TypeError('_get_sql model')

            if tablename not in tablenames:
                tablenames.append(tablename)
        from_ = ', '.join(tablenames)

        ons = []
        for field in self.__models[0]._get_fields():
            for join in self.__joins:
                if type(join) == type and issubclass(join, BaseModel):
                    foreign = join
                elif isinstance(join, BaseField) and join.foreign:
                    foreign = join.foreign
                else:
                    raise TypeError('_get_sql model')
                if field.foreign is foreign:
                    ons.append('{}.{} = {}.id'.format(main_tablename, field.name, foreign._get_tablename()))

        fields = []
        for model in self.__models:
            prefix = model._get_tablename() + '.' if len(self.__models + self.__joins) > 1 else ''
            fields += [prefix+field.name for field in model._get_fields()]
        select = ', '.join(fields)

        where = ''
        if len(self.__filters) > 0:
            where = ' WHERE {}'.format(', '.join(['{} == "{}"'.format(name, value) for name, value in self.__filters.items()]))

        sql = 'SELECT {select} FROM {from_}{on}{where}'.format(
            select=select,
            on=' ON '+' AND '.join(ons) if ons else '',
            from_=from_,
            where=where).strip()

        return sql

    @classmethod
    def _execute(cls, query):
        conn = connect()
        c = conn.cursor()
        c.execute(query)
        conn.commit()
        return c.fetchall()

    def _get_modified_copy(self, *models, **kwargs):
        data = dict(
            filters=self.__filters,
            joins=self.__joins,
        )
        data.update(kwargs)
        models = list(models)
        return QuerySet(*models, **data)

    def filter(self, **filters):
        return self._get_modified_copy(*self.__models, filters = dict(chain(self.__filters.items(), filters.items())))

    def join(self, obj):

        if isinstance(obj, BaseField):
            if not obj.foreign:
                return self._get_modified_copy()

            return self._get_modified_copy(*self.__models, joins=self.__joins+[obj])

        elif issubclass(obj, BaseModel):
            models = self._pack_models(self.__models + [obj]) # FIXME pack
            return self._get_modified_copy(*self.__models, joins=self.__joins+[obj])

        else:
            raise TypeError('JOIN', type(obj))

    @property
    def sql(self):
        return self._get_sql()

    def all(self):
        if not self.__models:
            raise Exception('No models')

        return [self.__models[0](record=record) for record in self._execute(self._get_sql())]

    def values(self):
        return self._execute(self._get_sql())



def main():
    pass


if __name__ == '__main__':
    main()
