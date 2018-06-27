import factory


class ShpImportFactory(factory.django.DjangoModelFactory):
    shapefiles = factory.django.FileField(filename='testshapefiles.zip')

    class Meta:
        model = 'imports.ShpImport'
