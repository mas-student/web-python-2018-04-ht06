from unittest import TestCase, mock
from web_python_2018_04_ht06_orm.core import connect, table, Scheme, BaseModel, BaseField


class TestParentModel(BaseModel):
    # id = ('id', int)
    id = BaseField(type=int)
    # int1 = ('int1', int)
    int1 = BaseField(type=int)
    # str1 = ('str1', str)
    str1 = BaseField(type=str)

class TestChildModel(BaseModel):
    # id = ('id', int)
    # sup = ('sup', TestParentModel)
    # str2 = ('str2', str)
    id = BaseField(type=int)
    sup = BaseField(type=TestParentModel)
    str2 = BaseField(type=str)

class TestFieldModel(BaseModel):
    simple = BaseField()
    named = BaseField(name='title')
    inited = BaseField(initval='begin')
    number = BaseField(type=int)
    parent = BaseField(type=TestParentModel)


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
        m = TestParentModel()
        # m._execute = mock.Mock()
        m.migrate()

        # m._execute.assert_called()
        # m._execute.assert_called_with('CREATE TABLE testmodel(id int, int1 int, str1 text)')

        self.assertTrue(executeMock.called)
        executeMock.assert_called_with('CREATE TABLE testparentmodel(id int, int1 int, str1 text)')

    def test_fields(self):
        m = TestParentModel()
        self.assertEqual(m._field_definitions(), [('id', 'int'), ('int1', 'int'), ('str1', 'text')])

    def test_save(self):
        # scheme = Scheme()
        # m1 = TestSupModel(scheme=scheme)
        # scheme.migrate()
        m1 = TestParentModel(data={'id': 3, 'int1': 45, 'str1': 'example'})
        # m1 = TestSupModel(record=(3, 45, 'example'))
        m1.migrate()
        # m1.id = 3
        # m1.int1 = 45
        # m1.str1 = 'example'
        m1.save()
        # self.assertEqual(m._fields(), [('int1', 'int'), ('str1', 'text')])
        self.assertEqual(m1.all(), [(3, 45, 'example')])

        m2 = TestParentModel(id=3)
        m2.int1 = 17
        m2.save()
        self.assertEqual(m2.all(), [(3, 17, 'example')])

    def test_init(self):
        scheme = Scheme()
        m1 = TestParentModel(scheme=scheme)
        scheme.migrate()
        # m1 = TestSupModel()
        # m1.migrate()
        m1.id = 3
        m1.int1 = 45
        m1.str1 = 'example'
        m1.save()
        # self.assertEqual(m._fields(), [('int1', 'int'), ('str1', 'text')])
        m2 = TestParentModel(id=3)
        self.assertEqual(m2.int1, 45)
        self.assertEqual(m2.str1, 'example')

    def test_foreign(self):
        m11 = TestParentModel()
        m11.migrate()
        m11.id = 3
        m11.int1 = 45
        m11.str1 = 'example'
        m11.save()
        m21 = TestChildModel()
        m21.migrate()
        m21.id = 7
        m21.sup = m11
        m21.save(verbose=True)
        m22 = TestChildModel(id=7)
        print('M22', m22, m22.sup)
        # m22.save(verbose=True)

    def test_query(self):
        TestParentModel.migrate()
        # m1 = TestSupModel(data={'id': 3, 'int1': 45, 'str1': 'example'})
        # m1.save()
        TestParentModel(data={'id': 3, 'int1': 45, 'str1': 'example'}).save()
        # m2 = TestSupModel(data={'id': 2, 'int1': 79, 'str1': 'sample'})
        # m2.save()
        m2 = TestParentModel(data={'id': 2, 'int1': 79, 'str1': 'sample'}).save()
        m2.save()
        qs = TestParentModel.query(TestParentModel.int1, TestParentModel.str1)
        self.assertEqual(qs.names, ['int1', 'str1'])
        self.assertEqual(qs.sql, 'SELECT int1, str1 FROM testparentmodel')
        self.assertEqual(qs.all(), [(45, 'example'), (79, 'sample')])
        self.assertEqual(qs.filter(int1=45).sql, 'SELECT int1, str1 FROM testparentmodel WHERE int1 == "45"')
        self.assertEqual(qs.filter(int1=45).all(), [(45, 'example')])

    def test_join(self):
        TestParentModel.migrate()
        p1 = TestParentModel(data={'id': 2, 'int1': 78, 'str1': 'example'}).save()
        p2 = TestParentModel(data={'id': 3, 'int1': 45, 'str1': 'example'}).save()
        TestChildModel.migrate()
        TestChildModel(data={'id': 1, 'sup': p2, 'str2': 'text1'}).save()
        TestChildModel(data={'id': 4, 'sup': p1, 'str2': 'text2'}).save()

    def test_execute(self):
        TestParentModel.migrate()
        p1 = TestParentModel(data={'id': 2, 'int1': 78, 'str1': 'example'}).save()
        p2 = TestParentModel(data={'id': 3, 'int1': 45, 'str1': 'sample'}).save()
        TestChildModel.migrate()
        TestChildModel(data={'id': 1, 'sup': p2, 'str2': 'text1'}).save()
        TestChildModel(data={'id': 4, 'sup': p1, 'str2': 'text2'}).save()
        qs = TestParentModel.query(TestParentModel.str1, TestChildModel.str2).join(TestChildModel)
        self.assertEqual(qs.sql, 'SELECT str1, str2 FROM testparentmodel, testchildmodel')
        self.assertEqual(qs.filter(int1=45).sql, 'SELECT str1, str2 FROM testparentmodel, testchildmodel WHERE int1 == "45"')
        self.assertEqual(qs.filter(int1=45).all(), [('sample', 'text1'), ('sample', 'text2')])
        # self.assertEqual(qs.all(), [(45, 'example')])

        # self.assertEqual(qs.filter(int1=45).all(), [(45, 'example')])
        # self.assertEqual(TestParentModel._execute(
        #     'SELECT int1, str1, str2 FROM testparentmodel, testchildmodel'
        # ), [])

    def test_field(self):
        m = TestFieldModel()
        # print('FIELD', m.color)
        # print('FIELD', m.color)
        self.assertEqual(TestFieldModel.simple, ('simple', str, 'testfieldmodel', None, None))
        self.assertEqual(m.simple, ('simple', str, 'testfieldmodel', None, None))
        self.assertEqual(m.named, ('title', str, 'testfieldmodel', None, None))
        self.assertEqual(m.named, ('title', str, 'testfieldmodel', None, None))
        self.assertEqual(m.number, ('number', int, 'testfieldmodel', None, None))
        self.assertEqual(m.parent, ('parent', TestParentModel, 'testfieldmodel', 'testparentmodel', None))