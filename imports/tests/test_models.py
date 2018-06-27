import os

from django.test import TestCase

from nature.tests.utils import make_user
from .factories import ShpImportFactory


class TestShpImport(TestCase):

    def setUp(self):
        self.shp_import = ShpImportFactory(created_by=make_user())

    def tearDown(self):
        os.remove(self.shp_import.shapefiles.path)

    def test__str__(self):
        self.assertEqual(self.shp_import.__str__(), 'testshapefiles.zip')
