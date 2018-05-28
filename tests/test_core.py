from sqlite3 import OperationalError
from unittest import TestCase, mock
from unittest.mock import patch

from web_python_2018_04_ht06_orm.core import connect, table, Scheme, BaseModel, BaseField, QuerySet


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

        StubParentModel.drop()
        StubParentModel.migrate()

        # m._execute.assert_called()
        # m._execute.assert_called_with('CREATE TABLE testmodel(id int, int1 int, str1 text)')

        self.assertTrue(executeMock.called)
        executeMock.assert_called_with('CREATE TABLE stubparentmodel(id int, int1 int, str1 text)', existed=False)

    def test_model(self):
        m = StubParentModel()
        self.assertEquals(m._values, {})

        # m = StubParentModel()
        # self.assertEquals(m.__dict__.get('a'), None)
        # m.int1 = 37
        # self.assertEquals(m.__dict__.get('a'), 37)

        StubParentModel.drop()
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
        # m2.save()


        qs1 = StubParentModel.query()
        # qs2 = QuerySet(models=[StubParentModel])
        # qs2 = QuerySet([], [], models=[StubParentModel])
        qs2 = QuerySet(StubParentModel)
        # self.assertEqual(qs.names, ['id', 'int1', 'str1'])
        self.assertEqual(qs1.sql, 'SELECT id, int1, str1 FROM stubparentmodel')
        self.assertEqual(qs2.sql, 'SELECT id, int1, str1 FROM stubparentmodel')
        self.assertEqual([m.values for m in qs1.all()], [(3, 45, 'example'), (2, 79, 'sample')])
        self.assertEqual(qs1.values(), [(3, 45, 'example'), (2, 79, 'sample')])
        self.assertEqual(qs1.filter(int1=45).sql, 'SELECT id, int1, str1 FROM stubparentmodel WHERE int1 == "45"')
        self.assertEqual(qs1.filter(int1=45).values(), [(3, 45, 'example')])

    def test_join(self):
        StubParentModel.migrate()
        p1 = StubParentModel(data={'id': 2, 'int1': 78, 'str1': 'example'}).save()
        p2 = StubParentModel(data={'id': 3, 'int1': 45, 'str1': 'example'}).save()
        StubChildModel.migrate()
        StubChildModel(data={'id': 1, 'sup': p2, 'str2': 'text1'}).save()
        StubChildModel(data={'id': 4, 'sup': p1, 'str2': 'text2'}).save()

        qs = StubChildModel.query().join(StubParentModel)
        self.assertEqual(
            qs.sql,
            'SELECT {name1}.id, {name1}.str2, {name1}.sup FROM {name1}, {name2} ON {name1}.sup = {name2}.id'.format(
                name1='stubchildmodel', name2='stubparentmodel'), 'StubChildModel.query().join(StubParentModel).sql')

        # qs = StubChildModel.query().join(StubParentModel)
        # self.assertEqual(qs.sql, 'SELECT stubchildmodel.id, stubchildmodel.str2, stubchildmodel.sup FROM stubchildmodel, stubparentmodel ON stubchildmodel.sup = stubparentmodel.id')
        # # qs = StubChildModel.query(StubChildModel.str2, StubParentModel.str1)
        # self.assertEqual(qs.sql, 'SELECT id, str2, sup FROM stubchildmodel, stubparentmodel ON stubchildmodel.sup = stubparentmodel.id')

        qs = StubChildModel.query().join(StubChildModel.sup)
        self.assertEqual(
            qs.sql,
            'SELECT {name1}.id, {name1}.str2, {name1}.sup FROM {name1}, {name2} ON {name1}.sup = {name2}.id'.format(
                name1='stubchildmodel', name2='stubparentmodel'), 'StubChildModel.query().join(StubChildModel.sup).sql')

    # def test_execute(self):
    #     StubParentModel.migrate()
    #     p1 = StubParentModel(data={'id': 2, 'int1': 78, 'str1': 'example'}).save()
    #     p2 = StubParentModel(data={'id': 3, 'int1': 45, 'str1': 'sample'}).save()
    #     StubChildModel.migrate()
    #     StubChildModel(data={'id': 1, 'sup': p2, 'str2': 'text1'}).save()
    #     StubChildModel(data={'id': 4, 'sup': p1, 'str2': 'text2'}).save()
    #     qs = StubParentModel.query()# .join(StubChildModel)
    #     self.assertEqual(qs.sql, 'SELECT id, int1, str1 FROM stubparentmodel')
    #     self.assertEqual(qs.filter(int1=45).sql, 'SELECT id, int1, str1 FROM stubparentmodel WHERE int1 == "45"')
    #     # self.assertEqual(qs.filter(int1=45).values(), [('sample', 'text1'), ('sample', 'text2')])
    #     # self.assertEqual(qs.all(), [(45, 'example')])
    #
    #     # self.assertEqual(qs.filter(int1=45).all(), [(45, 'example')])
    #     # self.assertEqual(stubparentmodel._execute(
    #     #     'SELECT int1, str1, str2 FROM stubparentmodel, stubchildmodel'
    #     # ), [])

    def test_field(self):
        m = StubFieldModel()
        # print('FIELD', m.color)
        # print('FIELD', m.color)
        self.assertEqual(StubFieldModel.simple.definition, ('simple', str, StubFieldModel, None, None), 'simple')
        self.assertEqual(StubFieldModel.named.definition, ('title', str, StubFieldModel, None, None))
        self.assertEqual(StubFieldModel.inited.definition, ('inited', str, StubFieldModel, None, 'begin'), 'inited')
        self.assertEqual(StubFieldModel.number.definition, ('number', int, StubFieldModel, None, None))
        self.assertEqual(StubFieldModel.parent.definition, ('parent', StubParentModel, StubFieldModel, StubParentModel, None))

    def test_delete(self):
        StubParentModel.migrate()
        m = StubParentModel(data={'id': 3, 'int1': 45, 'str1': 'example'})
        m.save()

        self.assertEqual(StubParentModel.query().values(), [(3, 45, 'example')])
        m.delete()
        self.assertEqual(StubParentModel.query().values(), [])