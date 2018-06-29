import os

from django.test import TestCase

from nature.models import Feature
from nature.tests.factories import FeatureFactory
from .utils import ZippedShapefilesGenerator
from ..importers import ShapefileImporter


class TestShapefileImporter(TestCase):

    def setUp(self):
        self.feature_1 = FeatureFactory()
        self.feature_2 = FeatureFactory.build(feature_class=self.feature_1.feature_class)

    def test_import(self):
        # make sure only feature 1 exist before importing
        self.assertQuerysetEqual(Feature.objects.all(), [repr(self.feature_1)])

        self.feature_1.name = 'new name'
        filename = ZippedShapefilesGenerator.create_shapefiles([self.feature_1, self.feature_2])
        importer = ShapefileImporter(filename)
        importer.import_features()
        os.remove(filename)

        # new feature created
        self.assertEqual(Feature.objects.count(), 2)

        # existing feature updated
        self.feature_1.refresh_from_db()
        self.assertEqual(self.feature_1.name, 'new name')
