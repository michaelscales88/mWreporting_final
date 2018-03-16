import unittest


class TestBase(unittest.TestCase):

    # initialization logic for the tests suite declared in the tests module
    # code that is executed before all tests in one tests run
    @classmethod
    def setUpClass(cls):
        pass

    # clean up logic for the tests suite declared in the tests module
    # code that is executed after all tests in one tests run
    @classmethod
    def tearDownClass(cls):
        pass

    # initialization logic
    # code that is executed before each tests
    def setUp(self):
        pass

    # clean up logic
    # code that is executed after each tests
    def tearDown(self):
        pass

    # tests method
    def test_equal_numbers(self):
        self.assertEqual(2, 2)

    # runs the unit tests in the module
