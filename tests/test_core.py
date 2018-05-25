from sqlite3 import OperationalError
from unittest import TestCase, mock
from unittest.mock import patch

from web_python_2018_04_ht06_orm.core import connect, table, Scheme, BaseModel, BaseField


class StubParentModel(BaseModel):
    # id = ('id', int)
    id = BaseField(type=int)
    # int1 = ('int1', int)
    int1 = BaseField(type=int)
    # str1 = ('str1', str)
    str1 = BaseField(type=str)

class StubChildModel(BaseModel):
    # id = ('id', int)
    # sup = ('sup', stubparentmodel)
    # str2 = ('str2', str)
    id = BaseField(type=int)
    sup = BaseField(type=StubParentModel)
    str2 = BaseField(type=str)

class StubFieldModel(BaseModel):
    simple = BaseField()
    named = BaseField(name='title')
    inited = BaseField(default='begin')
    number = BaseField(type=int)
    parent = BaseField(type=StubParentModel)


class TestCore(TestCase):
    def test_connect(self):
        self.assertIsNotNone(connect())
    #
    # def test_table(self):
    #     self.assertEqual(table(connect()), ('2006-01-05', 'BUY', 'RHAT', 100.0, 35.14))


class TestBaseModel(TestCase):
    # @mock.patch('web_python_2018_04_ht06_orm.core', '_execute')
    # @mock.patch('tests.test_core.TestModel', '_execute')
    # @mock.patch('tests.test_core.TestModel._execute')
    # @mock.patch('__main__.TestModel._execute')
    @mock.patch('web_python_2018_04_ht06_orm.core.BaseModel._execute')
    def test_migrate(self, executeMock):
        # m = StubParentModel()
        # # m._execute = mock.Mock()
        # m.migrate()

        StubParentModel._drop_table()
        StubParentModel.migrate()

        # m._execute.assert_called()
        # m._execute.assert_called_with('CREATE TABLE testmodel(id int, int1 int, str1 text)')

        self.assertTrue(executeMock.called)
        executeMock.assert_called_with('CREATE TABLE stubparentmodel(id int, int1 int, str1 text)', existed=False)

    def test_model(self):
        m = StubParentModel()
        self.assertEquals(m._values, {})

        StubParentModel._drop_table()
        m = StubParentModel(data={'id': 3, 'int1': 45, 'str1': 'example'})
        # m.save()
        self.assertRaises(LookupError, lambda : m.save())

    def test_fields(self):
        m = StubParentModel()
        self.assertEqual(m._get_column_defintions(), [('id', 'int'), ('int1', 'int'), ('str1', 'text')])

    def test_save(self):
        # scheme = Scheme()
        # m1 = TestSupModel(scheme=scheme)
        # scheme.migrate()
        m1 = StubParentModel(data={'id': 3, 'int1': 45, 'str1': 'example'})
        # m1 = TestSupModel(record=(3, 45, 'example'))
        m1.migrate()
        # m1.id = 3
        # m1.int1 = 45
        # m1.str1 = 'example'
        m1.save()
        # self.assertEqual(m._fields(), [('int1', 'int'), ('str1', 'text')])
        self.assertEqual(m1.all(), [(3, 45, 'example')])

        m2 = StubParentModel.get(id=3)
        m2.int1 = 17
        self.assertEqual(m2._values, {'id': 3, 'int1': 17, 'str1': 'example'})
        m2.save()
        self.assertEqual(m2.all(), [(3, 17, 'example')])

    def test_init(self):
        scheme = Scheme()
        m1 = StubParentModel(scheme=scheme)
        scheme.migrate()
        # m1 = TestSupModel()
        # m1.migrate()
        m1.id = 3
        m1.int1 = 45
        m1.str1 = 'example'
        m1.save()
        # self.assertEqual(m._fields(), [('int1', 'int'), ('str1', 'text')])
        m2 = StubParentModel.get(id=3)
        self.assertEqual(m2.int1, 45)
        self.assertEqual(m2.str1, 'example')

    def test_foreign(self):
        m11 = StubParentModel()
        m11.migrate()
        m11.id = 3
        m11.int1 = 45
        m11.str1 = 'example'
        m11.save()
        m21 = StubChildModel()
        m21.migrate()
        m21.id = 7
        m21.sup = m11
        with patch('web_python_2018_04_ht06_orm.core.BaseModel._insert') as mockInsert:
            m21.save()
            mockInsert.assert_called_with(id=7, sup=3)

        # m21.save(verbose=True)
        # m22 = stubchildmodel(id=7)
        # # print('M22', m22, m22.sup)
        # # m22.save(verbose=True)

    def test_query(self):
        StubParentModel.migrate()
        # m1 = TestSupModel(data={'id': 3, 'int1': 45, 'str1': 'example'})
        # m1.save()
        StubParentModel(data={'id': 3, 'int1': 45, 'str1': 'example'}).save()
        # m2 = TestSupModel(data={'id': 2, 'int1': 79, 'str1': 'sample'})
        # m2.save()
        m2 = StubParentModel(data={'id': 2, 'int1': 79, 'str1': 'sample'}).save()
        m2.save()
        qs = StubParentModel.query(StubParentModel.int1, StubParentModel.str1)
        self.assertEqual(qs.names, ['int1', 'str1'])
        self.assertEqual(qs.sql, 'SELECT int1, str1 FROM stubparentmodel')
        self.assertEqual(qs.all(), [(45, 'example'), (79, 'sample')])
        self.assertEqual(qs.filter(int1=45).sql, 'SELECT int1, str1 FROM stubparentmodel WHERE int1 == "45"')
        self.assertEqual(qs.filter(int1=45).all(), [(45, 'example')])

    def test_join(self):
        StubParentModel.migrate()
        p1 = StubParentModel(data={'id': 2, 'int1': 78, 'str1': 'example'}).save()
        p2 = StubParentModel(data={'id': 3, 'int1': 45, 'str1': 'example'}).save()
        StubChildModel.migrate()
        StubChildModel(data={'id': 1, 'sup': p2, 'str2': 'text1'}).save()
        StubChildModel(data={'id': 4, 'sup': p1, 'str2': 'text2'}).save()
        qs = StubChildModel.query(StubChildModel.str2, StubParentModel.str1)
        self.assertEqual(qs.sql, 'SELECT str2, str1 FROM stubchildmodel, stubparentmodel ON stubchildmodel.sup = stubparentmodel.id')

    def test_execute(self):
        StubParentModel.migrate()
        p1 = StubParentModel(data={'id': 2, 'int1': 78, 'str1': 'example'}).save()
        p2 = StubParentModel(data={'id': 3, 'int1': 45, 'str1': 'sample'}).save()
        StubChildModel.migrate()
        StubChildModel(data={'id': 1, 'sup': p2, 'str2': 'text1'}).save()
        StubChildModel(data={'id': 4, 'sup': p1, 'str2': 'text2'}).save()
        qs = StubParentModel.query(StubParentModel.str1, StubChildModel.str2).join(StubChildModel)
        self.assertEqual(qs.sql, 'SELECT str1, str2 FROM stubparentmodel, stubchildmodel')
        self.assertEqual(qs.filter(int1=45).sql, 'SELECT str1, str2 FROM stubparentmodel, stubchildmodel WHERE int1 == "45"')
        self.assertEqual(qs.filter(int1=45).all(), [('sample', 'text1'), ('sample', 'text2')])
        # self.assertEqual(qs.all(), [(45, 'example')])

        # self.assertEqual(qs.filter(int1=45).all(), [(45, 'example')])
        # self.assertEqual(stubparentmodel._execute(
        #     'SELECT int1, str1, str2 FROM stubparentmodel, stubchildmodel'
        # ), [])

    def test_field(self):
        m = StubFieldModel()
        # print('FIELD', m.color)
        # print('FIELD', m.color)
        self.assertEqual(StubFieldModel.simple.definition, ('simple', str, StubFieldModel, None, None))
        self.assertEqual(StubFieldModel.named.definition, ('title', str, StubFieldModel, None, None))
        self.assertEqual(StubFieldModel.inited.definition, ('inited', str, StubFieldModel, None, 'begin'))
        self.assertEqual(StubFieldModel.number.definition, ('number', int, StubFieldModel, None, None))
        self.assertEqual(StubFieldModel.parent.definition, ('parent', StubParentModel, StubFieldModel, StubParentModel, None))