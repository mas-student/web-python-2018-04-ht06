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

# def pprint():
#     from pprint import pformat
#     print('__DICT__', pformat(self.__dict__))
#     print('LOCALS', pformat(locals()))

# def _execute(query, tablename, existed=True):
#     # raise LookupError('Table {} does not exist'.format(cls._get_tablename()))
#     conn = connect()
#     c = conn.cursor()
#
#     c.execute('SELECT name FROM sqlite_master')
#     # print('TABLES', c.fetchall())
#
#     if existed:
#         sql = 'SELECT name FROM sqlite_master WHERE type=\'table\' AND name=\'{table_name}\''.format(
#             table_name=tablename)
#         # print('SQL', sql)
#         c.execute(sql)
#         if len(list(c.fetchall())) == 0:
#             raise LookupError('Table {} does not exist'.format(tablename))
#
#     c.execute(query)
#     conn.commit()
#     return c.fetchall()


# def _update(tablename, pk, **fields):
#     if self.first(self.id):
#         query = 'UPDATE {} SET {} WHERE id = "{}"'.format(
#             self._get_tablename(),
#             ', '.join(['{} = "{}"'.format(k, v) for k, v in values.items() if k != 'id']),
#             # self._tablename(),
#             self.id
#         )


class Scheme:
    def __init__(self):
        self.__models = OrderedDict()

    def add(self, model):
        self.__models[model.__name__] = model

    def migrate(self):
        for name, model in self.__models.items():
            model.migrate()


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
        # print('GET', self, self.__hash__(), obj, type)
        # print('NAME', type.get_name(self))
        # print('NAME', self.__name, model.get_field_name(self))
        name = self.__name
        if name is None:
            name = model.get_field_name(self)
        foreign = None
        if issubclass(self.__type, BaseModel):
        # if isinstance(1self.__type, BaseModel):
        # if type(self.__type).__name__ == 'type':
            foreign = self.__type
            # print('foreign', foreign)

        if not obj:
            return BaseField(name=name, type=self.__type, model=model, tablename=self.__tablename, foreign=foreign, default=self.__default)

        # return obj._values[name]
        return obj.get_value(name)

        # if self.__name not in obj._values:
        #     print('KEY', self.__name)
        # return obj._values[self.__name]


        # return (name, self.__type, model, foreign, self.__default)

    @property
    def model(self):
        return self.__model

    @property
    def definition(self):
        return (self.__name, self.__type, self.__model, self.__foreign, self.__default)

    def __set__(self, model, val):
        # print(self.__set__, obj, val)
        # print('Updating', self.name)
        if not model:
            raise TypeError('SET', model)
        name = self.__name
        if name is None:
            name = model.get_field_name(self)
        # print('SET', type(obj), obj)
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

    def get_value(self, name):
        return self._values[name]

    def set_value(self, name, value):
        self._values[name] = value

    @classmethod
    def _get_class_attr_names(cls):
        return [name for name in sorted(cls.__dict__.keys()) if not name.startswith('__')]

    @classmethod
    def _get_class_attrs(cls):
        return [(name, cls.__dict__[name]) for name in cls._get_class_attr_names()]
        # attrs = []
        # for name in sorted(cls.__dict__.keys()):
        #     if not name.startswith('__'):
        #         attrs.append((name, cls.__dict__[name]))
        #         # attrs.append((name, getattr(cls, name)))
        #         # print('ATTR', attr)
        # return attrs

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
        # for name, attr in cls._get_class_attrs():
        #     fields.append(attr)
        for key, value in cls.__dict__.items():
            if isinstance(value, BaseField):
                # fields.append(value)
                fields.append(getattr(cls, key))
        # return fields
        return sorted(fields, key=lambda field: field.name)

    @classmethod
    def _get_field(cls, name):
        # return cls._get_class_attrs()
        fields = []
        for key, value in cls._get_class_attrs():
            if key == name:
                return value
        return

    @property
    def fields(self):
        return self._get_fields()

    @property
    def values(self):
        # print('NAMES', [field.name for field in self._get_fields()])
        # return [field.value for field in self._get_fields()]
        return tuple([self._values.get(field.name) for field in self._get_fields()])

    @classmethod
    def _get_column_defintions(cls):
        typeMap = {
            'int': 'int',
            'str': 'text'
        }
        
        defintions = []
        # print('FIELDS', cls._get_fields())
        for field in cls._get_fields():
            # name = [k for k, v in cls.__dict__.items() if v is field][0] # FIXME
            # print('FIELD', name, field)
            # defintions.append((name, typeMap.get(field.type.__name__, field.type)))
            #
            defintions.append((field.name, typeMap.get(field.type.__name__, field.type)))
        return defintions

        # # return [getattr(cls, name) for name in sorted(cls.__dict__.keys()) if not name.startswith('__')]
        # # return [(name, getattr(cls, name)[1]) for name in sorted(cls.__dict__.keys()) if not name.startswith('__')]
        #
        # defs = []
        # # for name in sorted(cls.__dict__.keys()):
        # #     if not name.startswith('__'):
        # #         attr = getattr(cls, name)
        # #         # print('ATTR', attr)
        # #         if isinstance(attr, BaseField):
        # #             # print('BaseField', attr)
        # #             defs.append((attr.name, typeMap.get(attr.type.__name__, attr.type)))
        # #         else:
        # #             defs.append((name, typeMap.get(attr[1].__name__, attr[1])))
        # for name, attr in cls._get_class_attrs():
        #     if isinstance(attr, BaseField):
        #         # print('BaseField', attr, attr.type, attr.type.__name__)
        #         defs.append((name, typeMap.get(attr.type.__name__, attr.type)))
        #     else:
        #         defs.append((name, typeMap.get(attr[1].__name__, attr[1])))
        # return defs
        #
        # # return [(name, typeMap.get(getattr(cls, name)[1].__name__, getattr(cls, name)[1])) for name in sorted(cls.__dict__.keys()) if not name.startswith('__')]

    @classmethod
    def _get_field_definitions(cls):
        return [getattr(cls, name).definition for name in cls._get_class_attr_names()]

    @classmethod
    def all(cls):
        return cls._execute('SELECT * FROM {}'.format(cls._get_tablename()))

    @classmethod
    def first(cls, id):
        return cls._first(id)
        # records = cls._execute('SELECT * FROM {} WHERE id = "{}"'.format(cls._get_tablename(), id))
        # if records:
        #     return records[0]

    @classmethod
    def get(cls, id):
        records = cls._execute('SELECT * FROM {} WHERE id = "{}"'.format(cls._get_tablename(), id))

        if len(records) == 0:
            raise Exception('{} has not record with id = {}'.format(cls.__name__, id))

        return cls(record=records[0])

    @classmethod
    def query(cls, *fields):
        definitions = [field.definition for field in fields]
        models = [field.model for field in fields]
        field_dict = cls._get_field_dict()
        # print('FIELD_DICT', field_dict)
        return QuerySet(
            cls
            # [], # tablenames=[cls._get_tablename()],
            # [], # definitions=definitions,
            # # models=[definition[2] for definition in definitions],
            # models=[cls],
            # fields=[], # fields=[field_dict.get(definition[0]) for definition in definitions],
            # # parent=cls
        )

    @classmethod
    def _get_tablename(cls):
        return cls.__name__.lower()

    @property
    def tablename(self):
        return type(self)._get_tablename()

    @classmethod
    def migrate(cls):
        # tablename = self.__class__.__name__.lower()
        # self.__create_table(tablename)
        # cls.__create_table(cls._tablename())
        cls._drop_table(cls._get_tablename())
        cls._create_table(cls._get_tablename())

    @classmethod
    def _execute(cls, query, existed=True):
        # print('EXECUTE', query)
        # return _execute(query, existed)

        # raise LookupError('Table {} does not exist'.format(cls._get_tablename()))
        conn = connect()
        c = conn.cursor()

        c.execute('SELECT name FROM sqlite_master')
        # print('TABLES', c.fetchall())

        if existed:
            sql = 'SELECT name FROM sqlite_master WHERE type=\'table\' AND name=\'{table_name}\''.format(
                table_name=cls._get_tablename())
            # print('SQL', sql)
            c.execute(sql)
            if len(list(c.fetchall())) == 0:
                raise LookupError('Table {} does not exist'.format(cls._get_tablename()))

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
            columns = cls._get_column_defintions()
            for i in range(len(columns)):
                # print(type(columns[i][1]), str(type(columns[i][1])))
                if str(type(columns[i][1])) == "<class 'type'>": # FIXME
                    columns[i] = columns[i][0], 'int'
            # print('COLUMNS', columns)
            query = 'CREATE TABLE {}({})'.format(
                cls._get_tablename(),
                ', '.join(' '.join(v) for v in columns))
            # c.execute(query)
            cls._execute(query, existed=False)
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
            # self._tablename(),
            # self.id
        )
        # query = 'UPDATE {} SET {} WHERE id = "{}"'.format(
        #     cls._get_tablename(),
        #     ', '.join(['{} = "{}"'.format(k, v) for k, v in values.items() if k != 'id']),
        #     # self._tablename(),
        #     pk
        # )
        return cls._execute(query)

    @classmethod
    def _update(cls, pk, **values):
        # print('_UPDATE', pk, values)
        query = 'UPDATE {} SET {} WHERE id = "{}"'.format(
            cls._get_tablename(),
            # ', '.join(['{} = "{}"'.format(k, v) for k, v in values.items() if k != 'id']),
            ', '.join(['{} = "{}"'.format(k, v) for k, v in values.items()]),
            # self._tablename(),
            pk
        )
        return cls._execute(query)

    @classmethod
    def _delete(cls, pk, **values):
        # print('_DELETE', pk, values)
        query = 'DELETE FROM {} WHERE id == "{}";'.format(cls._get_tablename(), pk)
        return cls._execute(query)

    @classmethod
    def create(cls):
        cls._create_table(cls._get_tablename())

    @classmethod
    def drop(cls):
        cls._drop_table(cls._get_tablename())

    ### INIT
    # def __init__(self, scheme=None, id=0, record=None, data=None):
    def __init__(self, scheme=None, record=None, data=None):
        # print('INIT')
        self._values = {}
        # self.id = id
        if scheme:
            scheme.add(type(self))
        # if id != 0:
        #     record = self.first(id)
        #     if record:
        #         self._load_from_record(record)
        #         # # print('R', record)
        #         # # for name, value in zip([c[0] for c in self._columns()], record):
        #         # #     setattr(self, name, value)
        #         # for (name, typedef), value in zip([c for c in self._columns()], record):
        #         #     if type(typedef) == type:
        #         #         value = typedef.first(value)
        #         #     setattr(self, name, value)
        if record:
            self._load_from_record(record)
        if data:
            self._load_from_data(data)
        pass # __init__

    def _load_from_data(self, data):
        # keys = data.keys()
        # record = [data[key] for key in keys]
        # self._load_from_record(record)

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

    def save(self, verbose=False): # FIXME verbose
        values = OrderedDict()
        # print('ALL 1', self._execute('SELECT * FROM {}'.format(self._tablename())))
        # for column_defintions in self._get_column_defintions():
        #     # print('F', field)
        #     value = getattr(self, column_defintions[0])
        #     if isinstance(value, BaseModel):
        #         value = value.id
        #     values[column_defintions[0]] = value
        for key, value in self._values.items():
            # print('KEY', key, 'VALUE', value)
            if isinstance(value, BaseModel):
                value = value.id
            values[key] = value

        if self.first(self.id):
        # if self.first(self.id):
        #     if 'id' in values:
        #         del values['id']
            type(self)._update(self.id, **values)
            # query = 'UPDATE {} SET {} WHERE id = "{}"'.format(
            #     self._get_tablename(),
            #     ', '.join(['{} = "{}"'.format(k, v) for k, v in values.items() if k != 'id']),
            #     # self._tablename(),
            #     self.id
            # )
        else:
            type(self)._insert(**values)
            # query = 'INSERT INTO {} ({}) VALUES ({})'.format(
            #     self._get_tablename(),
            #     ', '.join(['{}'.format(k) for k in values.keys()]),
            #     ', '.join(['"{}"'.format(v) for v in values.values()]),
            #     # self._tablename(),
            #     # self.id
            # )
            # self._execute(query)
        # if verbose:
        #     print('SAVE', '"'+query+'"')
        # self._execute(query)
        # print('ALL 2', self._execute('SELECT * FROM {}'.format(self._tablename())))
        return self

    def delete(self):
        type(self)._delete(self.id)


class QuerySet:

    @staticmethod
    def _pack_models(models):
        result = []
        for model in models:
            if model not in result:
                result.append(model)
        return result

    # def __init__(self, tablenames, definitions, filters=None, models=None, fields=None, parent=None, joins=None, ons=None):
    def __init__(self, *models, joins=None, filters=None):
        self.__models = list(models)
        self.__joins = joins if joins is not None else []
        self._tablenames = [model._get_tablename() for model in self.__models]
        self._fieldnames = []
        self.__filters = filters if filters is not None else {}

        # # self._definitions = definitions
        # # self.__fields = [definition[2]._get_field(definition[0]) for definition in definitions]
        # # self.__parent = parent
        # # self.__joins = joins if joins else []
        # # self.__ons = ons if ons else []
        # self.__models = list(models) # self._pack_models(models if models else [])
        # # print('MODELS', self.__models)
        # # self.__fields = fields if fields else []
        # # print('FIELDS', self.__fields)
        # # self._tablenames = tablenames
        # self._tablenames = [model._get_tablename() for model in self.__models]
        # self._fieldnames = []
        # # ts = []
        # # for definition in self._definitions:
        # #     if type(definition) == tuple:
        # #         if len(definition) >= 3:
        # #             ts.append(definition[2])
        # # print('TS', ts)
        # # self.__filters = filters if filters is not None else {}
        # # for definition in definitions:
        # #     if type(definition) == tuple:
        # #         self._fieldnames.append(definition[0])
        # self.__filters = filters if filters is not None else {}

    # def _get_fieldnames(self):
    #     # return self._fieldnames
    #     # return self._fieldnames
    #     result = []
    #     for definition in self._definitions:
    #         if type(definition) == tuple:
    #             result.append(definition[0])
    #             # if len(definition) >= 3:
    #             #     print('TABLENAME', definition[2])
    #     return result

    # @property
    # def names(self):
    #     return self._get_fieldnames()

    def _get_sql(self):
        # print('_GET_SQL', self)
        # print('MODELS', self.__models)
        # print('JOINS', self.__joins)

        # tablename = self.__parent._get_tablename()

        if not self.__models:
            raise Exception('No models')

        # tablename = self.__models[0]._get_tablename()

        # ons = []
        on = ''
        # for model in self.__models:
        #     for field in model._get_fields():
        #         print('MODEL', model, 'FIELD', field)
        # for definition in self._definitions:
        #     if definition[3] and definition[3] in self._tablenames[1:]:
        #         print('ON {}.{} = {}.id'.format(self._tablenames[0], definition[0], definition[3]))
        # for model in self.__models:
        #     for definition in model._get_field_definitions():
        #         # print('!!!', definition, self.__parent, definition[2] is self.__parent)
        #         if definition[3] and definition[2] is self.__parent:
        #             on = ' ON {}.{} = {}.id'.format(definition[2]._get_tablename(), definition[0], definition[3]._get_tablename())
        #             # print('ON', on)
        # for join in self.__joins:
        #     if isinstance(join, BaseModel)

        # ons = []
        # for field in self.__parent._get_fields():
        #     for join in self.__joins:
        #         if field.foreign is join:
        #             ons.append('{}.{} = {}.id'.format(tablename, field.name, field.foreign._get_tablename()))

        main_tablename = self.__models[0]._get_tablename()

        # tablenames = [self.__models[0]._get_tablename()]
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
        # for model in self.__models:
        #     tablenames.append(model._get_tablename())
        from_ = ', '.join(tablenames)
        # print('TABLENAMES', tablenames)
        # print('FROM_', from_)

        ons = []
        for field in self.__models[0]._get_fields():
            # for join in self.__models[1:]:
            for join in self.__joins:
                foreign = None
                if type(join) == type and issubclass(join, BaseModel):
                    # tablename = join._get_tablename()
                    foreign = join
                elif isinstance(join, BaseField) and join.foreign:
                    # tablename = join.foreign._get_tablename()
                    foreign = join.foreign
                else:
                    raise TypeError('_get_sql model')
                if field.foreign is foreign:
                    ons.append('{}.{} = {}.id'.format(main_tablename, field.name, foreign._get_tablename()))

        # ons = []
        # for field in self.__models[0]._get_fields():
        #     # for join in self.__models[1:]:
        #     for join in self.__joins:
        #         if field.foreign is join:
        #             ons.append('{}.{} = {}.id'.format(main_tablename, field.name, field.foreign._get_tablename()))

        # prefix = tablename+'.' if len(self.__joins) > 0 else ''
        # prefix = tablename+'.' if len(self.__models) > 1 else ''
        # prefix = main_tablename+'.' if len(self.__models + self.__joins) > 1 else ''
        fields = []
        for model in self.__models:
            prefix = model._get_tablename() + '.' if len(self.__models + self.__joins) > 1 else ''
            fields += [prefix+field.name for field in model._get_fields()]
        select = ', '.join(fields)

        where = ''
        if len(self.__filters) > 0:
            where = ' WHERE {}'.format(', '.join(['{} == "{}"'.format(name, value) for name, value in self.__filters.items()]))

        # from pprint import pformat # FIXME
        # print('__DICT__', pformat(self.__dict__))
        # print('LOCALS', pformat(locals()))
        sql = 'SELECT {select} FROM {from_}{on}{where}'.format(
            # select=', '.join(self._get_fieldnames()),
            # select=', '.join([prefix+field.name for field in self.__parent._get_fields()]),
            # select=', '.join([prefix+field.name for field in self.__models[0]._get_fields()]),
            select=select,
            # on=on,
            on=' ON '+' AND '.join(ons) if ons else '',
            # from_=', '.join(self._tablenames),
            # from_=', '.join([m._get_tablename() for m in [self.__parent]+self.__joins]),
            # from_=', '.join([m._get_tablename() for m in self.__models]),
            from_=from_,
            where=where).strip()
        # print('SQL', sql)

        return sql

    @classmethod
    def _execute(cls, query):
        conn = connect()
        c = conn.cursor()
        c.execute(query)
        conn.commit()
        return c.fetchall()

    # def _get_modified_copy(self, *models):
    #     return QuerySet(self.__models + )

    def _get_modified_copy(self, *models, **kwargs):
        data = dict(
            filters=self.__filters,
            joins=self.__joins,
        )
        data.update(kwargs)
        # models = self.__models + list(models)
        models = list(models)
        # print('MODELS', models)
        return QuerySet(*models, **data)

        # data = dict(
        #     tablenames=self._tablenames,
        #     definitions=self._definitions,
        #     filters=self.__filters,
        #     models=self.__models,
        #     parent=self.__parent,
        #     joins=self.__joins,
        #     # ons=self.__ons,
        # )
        # data.update(kwargs)
        # return QuerySet(**data)

    def filter(self, **filters):
        # return self._get_modified_copy(filters = filters)
        return self._get_modified_copy(*self.__models, filters = dict(chain(self.__filters.items(), filters.items())))
        # _filters = deepcopy(self._filters)
        # _filters.update(filters)
        # return QuerySet(
        #     tablenames=self._tablenames,
        #     definitions=self._definitions,
        #     filters=_filters,
        #     models=self.__models,
        #     parent=self.__parent,
        # )

    # def join(self, model):
    #     return self._get_modified_copy(models=self._pack_models(self.__models + [model]))

    def join(self, obj):

        if isinstance(obj, BaseField):
            if not obj.foreign:
                return self._get_modified_copy()

            # models = self._pack_models(self.__models + [obj.foreign]) # FIXME pack

            # return self._get_modified_copy(*models, joins=self.__joins+[obj])
            return self._get_modified_copy(*self.__models, joins=self.__joins+[obj])

            # if obj.model is self.__models[0]:
            #     return self._get_modified_copy()
            # models = self._pack_models(self.__models + [obj.model])
            # return self._get_modified_copy(*models, joins=self.__joins+[obj.model])

            # return self._get_modified_copy(
            #     fields=self.__fields+[obj] if obj not in self.__fields else self.__fields,
            #     models=self._pack_models(self.__models+[obj.model]),
            #     # joins=pack(self.__joins+[obj.model])
            #     joins=self.__joins+[obj.model],
            #     # joins=list(OrderedDict.fromkeys(self.__joins+[obj.model])),
            #     # ons=list(OrderedDict.fromkeys(self.__ons+[obj])),
            # )
        elif issubclass(obj, BaseModel):
            models = self._pack_models(self.__models + [obj]) # FIXME pack
            # return self._get_modified_copy(*models, joins=self.__joins+[obj])
            return self._get_modified_copy(*self.__models, joins=self.__joins+[obj])
            # on = None
            # return self._get_modified_copy(
            #     models=self._pack_models(self.__models+[obj]),
            #     # joins=list(OrderedDict.fromkeys(self.__joins + [obj])),
            #     # ons=list(OrderedDict.fromkeys(self.__ons + [])),
            # )
        else:
            raise TypeError('JOIN', type(obj))
        # # print('JOIN DEFS', self._definitions, 'models', self.__models),
        # return QuerySet(
        #     tablenames=self._tablenames+[model._get_tablename()],
        #     definitions=self._definitions,
        #     filters=self._filters,
        #     models=self._pack_models(self.__models+[model]),
        #     parent=self.__parent,
        # )

    def all(self):
        if not self.__models:
            raise Exception('No models')

        # return [self.__parent(record=record) for record in self._execute(self._get_sql())]
        return [self.__models[0](record=record) for record in self._execute(self._get_sql())]

    def values(self):
        return self._execute(self._get_sql())

    @property
    def sql(self):
        return self._get_sql()


# class FirstModel(BaseModel):
#
#     pass

def table(conn): # FIXME
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
