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

    - If a feature in shapefiles has an id that already exists in database,
    then the importer will update the feature, otherwise it will create
    new ones.
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

    @classmethod
    def import_features(cls, zipped_shapefiles):
        shp_reader = cls._get_shp_reader(zipped_shapefiles)
        fields = [cls.field_mapping[shape_field[0]] for shape_field in shp_reader.fields[1:]]
        for shape_record in shp_reader.iterShapeRecords():
            cls._import_feature(fields, shape_record)

    @classmethod
    def _get_shp_reader(cls, zipped_shapefiles):
        with zipfile.ZipFile(zipped_shapefiles) as zfile:
            dbf, shp, shx = sorted([name for name in zfile.namelist() if name.endswith(cls.required_extensions)])
            with zfile.open(dbf) as dbf, zfile.open(shp) as shp, zfile.open(shx) as shx:
                return shapefile.Reader(shp=shp, shx=shx, dbf=dbf)

    @classmethod
    def _import_feature(cls, fields, shape_record):
        feature_data = dict(zip(fields, shape_record.record))
        feature_data['geometry'] = cls._get_feature_geometry(shape_record.shape)

        feature_id = feature_data.pop('id', None)
        try:
            feature = Feature.objects.get(id=feature_id)
            for key, value in feature_data.items():
                setattr(feature, key, value)
                feature.save()
        except Feature.DoesNotExist:
            Feature.objects.create(**feature_data)

    @classmethod
    def _get_feature_geometry(cls, shape):
        geojson = json.dumps(shape.__geo_interface__)
        return GEOSGeometry(geojson, srid=settings.SRID)
