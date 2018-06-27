import os
import zipfile

from django.core.exceptions import ValidationError
from django.core.files import File
from django.test import TestCase

from .factories import ShpImportFactory
from ..validators import ZippedShapefilesValidator


class TestValidateZippedShapefiles(TestCase):

    def setUp(self):
        self.validator = ZippedShapefilesValidator()

    def test_not_raise_validation_error_for_valid_zipped_shapefiles(self):
        filename = 'test.zip'
        with zipfile.ZipFile(filename, 'w') as zfile:
            with open('test.shp', 'w') as shp, open('test.shx', 'w') as shx, open('test.dbf', 'w') as dbf:
                zfile.write(shp.name)
                zfile.write(shx.name)
                zfile.write(dbf.name)
                os.remove(shp.name)
                os.remove(shx.name)
                os.remove(dbf.name)

        with open(filename, mode='rb') as f:
            shp_import = ShpImportFactory.build(shapefiles=File(f))
            try:
                self.validator(shp_import.shapefiles)
            except ValidationError:
                self.fail('Should not raise ValidationError for valid zipped shapefiles')
            finally:
                f.close()
                os.remove(filename)

    def test_raise_validation_error_for_invalid_zip_file(self):
        filename = 'test.zip'
        with open('test.zip', 'w') as f:
            f.write('test content')

        with open(filename, mode='rb') as f:
            shp_import = ShpImportFactory.build(shapefiles=File(f))
            try:
                self.validator(shp_import.shapefiles)
                self.fail('Does not raise ValidationError for invalid zipfile.')
            except ValidationError as e:
                self.assertEqual(e.code, 'invalid_zipfile')
            finally:
                f.close()
                os.remove(filename)

    def test_raise_validation_error_for_mismatched_filenames(self):
        filename = 'test.zip'
        with zipfile.ZipFile(filename, 'w') as zfile:
            with open('test.shp', 'w') as shp, open('file.shx', 'w') as shx, open('test.dbf', 'w') as dbf:
                zfile.write(shp.name)
                zfile.write(shx.name)
                zfile.write(dbf.name)
                os.remove(shp.name)
                os.remove(shx.name)
                os.remove(dbf.name)

        with open(filename, mode='rb') as f:
            shp_import = ShpImportFactory.build(shapefiles=File(f))
            try:
                self.validator(shp_import.shapefiles)
                self.fail('Does not raise ValidationError for mismatches filenames.')
            except ValidationError as e:
                self.assertEqual(e.code, 'mismatched_filenames')
            finally:
                f.close()
                os.remove(filename)

    def test_raise_validation_error_for_missing_required_filenames(self):
        filename = 'test.zip'
        with zipfile.ZipFile(filename, 'w') as zfile:
            with open('test.shp', 'w') as shp, open('test.dbf', 'w') as dbf:
                zfile.write(shp.name)
                zfile.write(dbf.name)
                os.remove(shp.name)
                os.remove(dbf.name)

        with open(filename, mode='rb') as f:
            shp_import = ShpImportFactory.build(shapefiles=File(f))
            try:
                self.validator(shp_import.shapefiles)
                self.fail('Does not raise ValidationError for missing required files.')
            except ValidationError as e:
                self.assertEqual(e.code, 'missing_required_files')
            finally:
                f.close()
                os.remove(filename)
