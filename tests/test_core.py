from unittest import TestCase, mock
from web_python_2018_04_ht06_orm.core import connect, table, BaseModel


class TestModel(BaseModel):
    id = ('id', 'int')
    int1 = ('int1', 'int')
    str1 = ('str1', 'text')


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
        m = TestModel()
        # m._execute = mock.Mock()
        m.migrate()

        # m._execute.assert_called()
        # m._execute.assert_called_with('CREATE TABLE testmodel(id int, int1 int, str1 text)')

        executeMock.assert_called()
        executeMock.assert_called_with('CREATE TABLE testmodel(id int, int1 int, str1 text)')

    def test_fields(self):
        m = TestModel()
        self.assertEqual(m._columns(), [('id', 'int'), ('int1', 'int'), ('str1', 'text')])

    def test_save(self):
        m1 = TestModel()
        m1.migrate()
        m1.id = 3
        m1.int1 = 45
        m1.str1 = 'example'
        m1.save()
        # self.assertEqual(m._fields(), [('int1', 'int'), ('str1', 'text')])
        self.assertEqual(m1.all(), [(3, 45, 'example')])

        m2 = TestModel(3)
        m2.int1 = 17
        m2.save()
        self.assertEqual(m2.all(), [(3, 17, 'example')])

    def test_init(self):
        m1 = TestModel()
        m1.migrate()
        m1.id = 3
        m1.int1 = 45
        m1.str1 = 'example'
        m1.save()
        # self.assertEqual(m._fields(), [('int1', 'int'), ('str1', 'text')])
        m2 = TestModel(3)
        self.assertEqual(m2.int1, 45)
        self.assertEqual(m2.str1, 'example')