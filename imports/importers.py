import json
import zipfile

import shapefile
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry

from nature.models import Feature


class ShapefileImporter:
    """A class that allow importing shapefile features to Feature model

    The class makes a few assumptions on the input shapefiles:

    - The shapefiles must be valid, i.e.
        - all mandatory files (.shp, .shx and .dbf) are present
        - all files have same name prefix
        - the number of shapes and records must match

    - The shapefiles must not include additional fields besides the ones
    listed below and the names must match exactly. Basically they have
    same names as in database but shapefile has a 10 characters limit
    on field names.

    - The shapefile may omit some of the fields that are not required by
    the Feature model.
    """
    required_extensions = ('.shp', '.shx', '.dbf')
    field_mapping = {
        'id': 'id',
        'tunnus': 'fid',
        'luokkatunn': 'feature_class_id',
        'nimi': 'name',
        'kuvaus': 'description',
        'huom': 'notes',
        'voimassa': 'active',
        'digipvm': 'created_time',
        'numero': 'number',
        'digitoija': 'created_by',
        'suojaustas': 'protection_level',
        'pvm_editoi': 'last_modified_time',
        'muokkaaja': 'last_modified_by',
        'pinta_ala': 'area',
    }

    def __init__(self, zipped_shapefile):
        with zipfile.ZipFile(zipped_shapefile) as zfile:
            dbf, shp, shx = sorted([name for name in zfile.namelist() if name.endswith(self.required_extensions)])
            with zfile.open(dbf) as dbf, zfile.open(shp) as shp, zfile.open(shx) as shx:
                self.shp_reader = shapefile.Reader(shp=shp, shx=shx, dbf=dbf)
        self.fields = [self.field_mapping[shape_field[0]] for shape_field in self.shp_reader.fields[1:]]

    def import_features(self):
        for shape_record in self.shp_reader.iterShapeRecords():
            self._import_feature(shape_record)

    def _import_feature(self, shape_record):
        feature_data = dict(zip(self.fields, shape_record.record))
        feature_data['geometry'] = self._get_feature_geometry(shape_record.shape)

        feature_id = feature_data.pop('id', None)
        try:
            feature = Feature.objects.get(id=feature_id)
            for key, value in feature_data.items():
                setattr(feature, key, value)
                feature.save()
        except Feature.DoesNotExist:
            Feature.objects.create(**feature_data)

    def _get_feature_geometry(self, shape):
        geojson = json.dumps(shape.__geo_interface__)
        return GEOSGeometry(geojson, srid=settings.SRID)
