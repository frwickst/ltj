import os
import zipfile

import shapefile


class ZippedShapefilesGenerator:
    """A helper class to generate zipped shapefiles for given features"""

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

    shape_fields = [
        ['id', 'N', 10, 0],
        ['tunnus', 'C', 10, 0],
        ['luokkatunn', 'C', 10, 0],
        ['nimi', 'C', 80, 0],
        ['kuvaus', 'C', 254, 0],
        ['huom', 'C', 254, 0],
        ['voimassa', 'C', 254, 0],
        ['digipvm', 'D', 8, 0],
        ['numero', 'N', 10, 0],
        ['digitoija', 'C', 50, 0],
        ['suojaustas', 'N', 10, 0],
        ['pvm_editoi', 'C', 24, 0],
        ['muokkaaja', 'C', 10, 0],
        ['pinta_ala', 'N', 24, 15],
    ]

    @classmethod
    def create_shapefiles(cls, features):
        shp_writer = shapefile.Writer(shapeType=shapefile.POINT)
        shp_writer.fields = cls.shape_fields
        for feature in features:
            shp_writer.point(*feature.geometry)
            shp_writer.record(*cls._get_record(feature))
        target = shp_writer.save()

        with zipfile.ZipFile('testshapefiles.zip', 'w') as zfile:
            shapefiles = ['{0}.{1}'.format(target, ext) for ext in ['shp', 'shx', 'dbf']]
            for file in shapefiles:
                zfile.write(file)
                os.remove(file)
            return zfile.filename

    @classmethod
    def _get_record(cls, feature):
        shape_field_names = [shape_field[0] for shape_field in cls.shape_fields]
        return [getattr(feature, cls.field_mapping[field_name]) for field_name in shape_field_names]
