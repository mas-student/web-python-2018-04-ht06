from unittest import TestCase, mock
from web_python_2018_04_ht06_orm.core import connect, table, Scheme, BaseModel


class TestSupModel(BaseModel):
    id = ('id', 'int')
    int1 = ('int1', 'int')
    str1 = ('str1', 'text')

class TestSubModel(BaseModel):
    id = ('id', 'int')
    sup = ('sup', TestSupModel)


class TestCore(TestCase):
    def test_connect(self):
        self.assertIsNotNone(connect())

    def test_table(self):
        self.assertEqual(table(connect()), ('2006-01-05', 'BUY', 'RHAT', 100.0, 35.14))


class TestBaseModel(TestCase):
    # @mock.patch('web_python_2018_04_ht06_orm.core', '_execute')
    # @mock.patch('tests.test_core.TestModel', '_execute')
    # @mock.patch('tests.test_core.TestModel._execute')
    # @mock.patch('__main__.TestModel._execute')
    @mock.patch('web_python_2018_04_ht06_orm.core.BaseModel._execute')
    def test_migrate(self, executeMock):
        m = TestSupModel()
        # m._execute = mock.Mock()
        m.migrate()

        # m._execute.assert_called()
        # m._execute.assert_called_with('CREATE TABLE testmodel(id int, int1 int, str1 text)')

        executeMock.called
        executeMock.assert_called_with('CREATE TABLE testsupmodel(id int, int1 int, str1 text)')

    def test_fields(self):
        m = TestSupModel()
        self.assertEqual(m._field_definitions(), [('id', 'int'), ('int1', 'int'), ('str1', 'text')])

    def test_save(self):
        # scheme = Scheme()
        # m1 = TestSupModel(scheme=scheme)
        # scheme.migrate()
        m1 = TestSupModel(data={'id': 3, 'int1': 45, 'str1': 'example'})
        # m1 = TestSupModel(record=(3, 45, 'example'))
        m1.migrate()
        # m1.id = 3
        # m1.int1 = 45
        # m1.str1 = 'example'
        m1.save()
        # self.assertEqual(m._fields(), [('int1', 'int'), ('str1', 'text')])
        self.assertEqual(m1.all(), [(3, 45, 'example')])

        m2 = TestSupModel(id=3)
        m2.int1 = 17
        m2.save()
        self.assertEqual(m2.all(), [(3, 17, 'example')])

    def test_init(self):
        scheme = Scheme()
        m1 = TestSupModel(scheme=scheme)
        scheme.migrate()
        # m1 = TestSupModel()
        # m1.migrate()
        m1.id = 3
        m1.int1 = 45
        m1.str1 = 'example'
        m1.save()
        # self.assertEqual(m._fields(), [('int1', 'int'), ('str1', 'text')])
        m2 = TestSupModel(id=3)
        self.assertEqual(m2.int1, 45)
        self.assertEqual(m2.str1, 'example')

    def test_foreign(self):
        m11 = TestSupModel()
        m11.migrate()
        m11.id = 3
        m11.int1 = 45
        m11.str1 = 'example'
        m11.save()
        m21 = TestSubModel()
        m21.migrate()
        m21.id = 7
        m21.sup = m11
        m21.save(verbose=True)
        m22 = TestSubModel(id=7)
        print('M22', m22, m22.sup)
        # m22.save(verbose=True)

    def test_query(self):
        TestSupModel.migrate()
        m11 = TestSupModel(data={'id': 3, 'int1': 45, 'str1': 'example'})
        m11.save()
        qs = m11.query(TestSupModel.int1, TestSupModel.str1)
        self.assertEqual(qs.names, ['int1', 'str1'])
        self.assertEqual(qs._sql, 'SELECT int1, str1 FROM testsupmodel')
        self.assertEqual(qs.all(), [(45, 'example')])