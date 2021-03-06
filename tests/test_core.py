from sqlite3 import OperationalError
from unittest import TestCase, mock
from unittest.mock import patch

from web_python_2018_04_ht06_orm.core import connect, Scheme, BaseModel, BaseField, QuerySet


Scheme.getInstance().database = 'local.db'


class StubParentModel(BaseModel):
    id = BaseField(type=int, pk=True)
    int1 = BaseField(type=int)
    str1 = BaseField(type=str)

class StubChildModel(BaseModel):
    id = BaseField(type=int, pk=True)
    sup = BaseField(type=StubParentModel)
    str2 = BaseField(type=str)

class StubFieldModel(BaseModel):
    id = BaseField(type=int, pk=True)
    simple = BaseField()
    named = BaseField(name='title')
    inited = BaseField(default='begin')
    number = BaseField(type=int)
    parent = BaseField(type=StubParentModel)


class TestCore(TestCase):
    def test_connect(self):
        self.assertIsNotNone(connect())

    def test_columns(self):
        StubParentModel.generate()
        self.assertEqual(list(map(lambda t: t[1], StubParentModel._get_column_names())), ['id', 'int1', 'str1'])


class TestBaseField(TestCase):

    def test_value_get(self):
        StubParentModel.generate()
        m = StubParentModel(data={'id': 3, 'int1': 45, 'str1': 'example'})
        self.assertEqual(m.int1, 45)
        self.assertEqual(m.str1, 'example')


class TestBaseModel(TestCase):

    @mock.patch('web_python_2018_04_ht06_orm.core.BaseModel._execute')
    def test_migrate(self, executeMock):
        StubParentModel.drop()
        StubParentModel.generate()

        self.assertTrue(executeMock.called)
        executeMock.assert_called_with('CREATE TABLE stubparentmodel(id int PRIMARY KEY, int1 int, str1 text)', existed=False)

    def test_table_not_found(self):
        StubParentModel.drop()
        m = StubParentModel(data={'id': 3, 'int1': 45, 'str1': 'example'})
        self.assertRaises(LookupError, lambda : m.save())

    def test_column_not_found(self):
        StubParentModel.drop()
        m = StubParentModel(data={'id': 3, 'int1': 45, 'str1': 'example'})
        self.assertRaises(LookupError, lambda : m.save())

    def test__column_defintions(self):
        m = StubParentModel()
        self.assertEqual(m._get_column_defintions(), [('id', 'int'), ('int1', 'int'), ('str1', 'text')])

    def test_init_record(self):
        m1 = StubParentModel(record=(3, 45, 'example'))
        self.assertEqual(m1._values, {'id': 3, 'int1': 45, 'str1': 'example'})

    def test_init_data(self):
        m1 = StubParentModel(data={'id': 3, 'int1': 45, 'str1': 'example'})
        self.assertEqual(m1._values, {'id': 3, 'int1': 45, 'str1': 'example'})

    def test_values(self):
        m1 = StubParentModel(data={'id': 3, 'int1': 45, 'str1': 'example'})
        m1.int1 = 17
        self.assertEqual(m1._values, {'id': 3, 'int1': 17, 'str1': 'example'})

    def test_get(self):
        StubParentModel.generate()
        StubParentModel(data={'id': 3, 'int1': 45, 'str1': 'example'}).save()
        m2 = StubParentModel.get(id=3)
        self.assertEqual(m2._values, {'id': 3, 'int1': 45, 'str1': 'example'})

    def test_save(self):
        StubParentModel.generate()
        m = StubParentModel(data={'id': 3, 'int1': 45, 'str1': 'example'})
        with patch('web_python_2018_04_ht06_orm.core.BaseModel._insert') as mockInsert:
            m.save()
            mockInsert.assert_called_with(id=3, int1=45, str1='example')

    def test_field(self):
        m = StubFieldModel()
        self.assertEqual(StubFieldModel.id.definition, ('id', int, StubFieldModel, None, None, True), 'id')
        self.assertEqual(StubFieldModel.simple.definition, ('simple', str, StubFieldModel, None, None, False), 'simple')
        self.assertEqual(StubFieldModel.named.definition, ('title', str, StubFieldModel, None, None, False))
        self.assertEqual(StubFieldModel.inited.definition, ('inited', str, StubFieldModel, None, 'begin', False), 'inited')
        self.assertEqual(StubFieldModel.number.definition, ('number', int, StubFieldModel, None, None, False))
        self.assertEqual(StubFieldModel.parent.definition, ('parent', StubParentModel, StubFieldModel, StubParentModel, None, False))

    def test_delete(self):
        StubParentModel.generate()
        m = StubParentModel(data={'id': 3, 'int1': 45, 'str1': 'example'}).save()

        self.assertEqual(StubParentModel.query().values(), [(3, 45, 'example')])
        StubParentModel.get(id=3).delete()
        self.assertEqual(StubParentModel.query().values(), [])


class TestQuerySet(TestCase):

    def test_query(self):
        StubParentModel.generate()
        StubParentModel(data={'id': 3, 'int1': 45, 'str1': 'example'}).save()
        m2 = StubParentModel(data={'id': 2, 'int1': 79, 'str1': 'sample'}).save()

        qs1 = StubParentModel.query()
        qs2 = QuerySet(StubParentModel)
        self.assertEqual(qs1.sql, 'SELECT id, int1, str1 FROM stubparentmodel')
        self.assertEqual(qs2.sql, 'SELECT id, int1, str1 FROM stubparentmodel')
        self.assertEqual(qs1.filter(int1=45).sql, 'SELECT id, int1, str1 FROM stubparentmodel WHERE int1 == "45"')
        self.assertEqual(qs1.filter(int1=45).values(), [(3, 45, 'example')])
        qs3 = QuerySet(StubChildModel, StubParentModel)
        self.assertEqual(
            qs3.sql,
            'SELECT {name1}.id, {name1}.str2, {name1}.sup, {name2}.id, {name2}.int1, {name2}.str1 FROM {name1}, {name2}'.format(
                name1='stubchildmodel', name2='stubparentmodel'), 'QuerySet(StubChildModel, StubParentModel)')

    def test_sql(self):
        self.assertEqual(StubParentModel.query().sql, 'SELECT id, int1, str1 FROM stubparentmodel')
        self.assertEqual(QuerySet(StubParentModel).sql, 'SELECT id, int1, str1 FROM stubparentmodel')
        self.assertEqual(QuerySet(StubParentModel.int1).sql, 'SELECT int1 FROM stubparentmodel', 'only int1')
        self.assertEqual(
            QuerySet(StubChildModel, StubParentModel).sql,
            'SELECT {name1}.id, {name1}.str2, {name1}.sup, {name2}.id, {name2}.int1, {name2}.str1 FROM {name1}, {name2}'.format(
                name1='stubchildmodel', name2='stubparentmodel'), 'QuerySet(StubChildModel, StubParentModel)')

    def test_values(self):
        StubParentModel.generate()
        StubParentModel(data={'id': 3, 'int1': 45, 'str1': 'example'}).save()
        StubParentModel(data={'id': 2, 'int1': 79, 'str1': 'sample'}).save()

        self.assertEqual(StubParentModel.query().values(), [(3, 45, 'example'), (2, 79, 'sample')])

    def test_join(self):
        StubParentModel.generate()
        p1 = StubParentModel(data={'id': 2, 'int1': 78, 'str1': 'example'}).save()
        p2 = StubParentModel(data={'id': 3, 'int1': 45, 'str1': 'example'}).save()
        StubChildModel.generate()
        StubChildModel(data={'id': 1, 'sup': p2, 'str2': 'text1'}).save()
        StubChildModel(data={'id': 4, 'sup': p1, 'str2': 'text2'}).save()

        qs = StubChildModel.query().join(StubParentModel)
        self.assertEqual(
            qs.sql,
            'SELECT {name1}.id, {name1}.str2, {name1}.sup FROM {name1}, {name2} ON {name1}.sup = {name2}.id'.format(
                name1='stubchildmodel', name2='stubparentmodel'), 'StubChildModel.query().join(StubParentModel).sql')

        qs = StubChildModel.query().join(StubChildModel.sup)
        self.assertEqual(
            qs.sql,
            'SELECT {name1}.id, {name1}.str2, {name1}.sup FROM {name1}, {name2} ON {name1}.sup = {name2}.id'.format(
                name1='stubchildmodel', name2='stubparentmodel'), 'StubChildModel.query().join(StubChildModel.sup).sql')

