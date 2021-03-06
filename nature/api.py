from django.contrib.gis.db.models.functions import Transform
from rest_framework.fields import SerializerMethodField
from rest_framework.reverse import reverse
from rest_framework import serializers, viewsets, routers, relations
from rest_framework_gis.fields import GeometryField

from nature.models import (
    ConservationProgramme, Criterion, Square, Protection,
    Feature, FeatureClass, Value, Publication, Species,
    Abundance, Frequency, MigrationClass, Origin, BreedingDegree,
    Observation, ObservationSeries, TransactionType, Transaction, Person,
    Regulation, HabitatType, HabitatTypeObservation,
    FeatureLink, ProtectionLevelEnabledQuerySet, ProtectedFeatureQueryset,
    ProtectedFeatureClassQueryset,
)


class ProtectedManyRelatedField(relations.ManyRelatedField):
    """
    Handles view permissions for related field listings with protection_level and open_data
    """
    def to_representation(self, iterable):
        if isinstance(iterable, ProtectionLevelEnabledQuerySet):
            iterable = iterable.for_public()

        if isinstance(iterable, (ProtectedFeatureQueryset, ProtectedFeatureClassQueryset)):
            iterable = iterable.open_data()

        return super().to_representation(iterable)


class ProtectedHyperlinkedRelatedField(relations.HyperlinkedRelatedField):
    """
    Handles view permissions for related field listings with protection_level and open_data
    """

    @classmethod
    def many_init(cls, *args, **kwargs):
        # the correct arguments must be passed on to the parent
        list_kwargs = {'child_relation': cls(*args, **kwargs)}
        for key in kwargs.keys():
            if key in relations.MANY_RELATION_KWARGS:
                list_kwargs[key] = kwargs[key]
        return ProtectedManyRelatedField(**list_kwargs)

    def get_queryset(self):
        qs = super().get_queryset()

        if isinstance(qs, ProtectionLevelEnabledQuerySet):
            qs = qs.for_public()

        if isinstance(qs, (ProtectedFeatureQueryset, ProtectedFeatureClassQueryset)):
            qs = qs.open_data()

        return qs


class SpanOneToOneProtectedHyperlinkedRelatedField(ProtectedHyperlinkedRelatedField):
    """
    Allows linking directly back to the feature, instead of an object with the same id as feature.
    Useful for spanning useless one-to-one mappings.
    """

    def get_url(self, obj, view_name, request, format):
        kwargs = {'pk': obj.pk}
        return reverse(view_name, kwargs=kwargs, request=request, format=format)


class ProtectedHyperlinkedModelSerializer(serializers.HyperlinkedModelSerializer):
    """
    Handles view permissions for related field listings with ProtectedNatureModel instances.
    """
    serializer_related_field = ProtectedHyperlinkedRelatedField


class ProtectedViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Handles view permissions for ProtectedNatureModel instances.
    """

    def get_queryset(self):
        qs = super().get_queryset()

        if isinstance(qs, ProtectionLevelEnabledQuerySet):
            qs = qs.for_public()

        if isinstance(qs, (ProtectedFeatureQueryset, ProtectedFeatureClassQueryset)):
            qs = qs.open_data()

        return qs


class ConservationProgrammeSerializer(ProtectedHyperlinkedModelSerializer):
    protected_features = SpanOneToOneProtectedHyperlinkedRelatedField(many=True,
                                                                      source='protections',
                                                                      view_name='feature-detail',
                                                                      queryset=Feature.objects.all())

    class Meta:
        model = ConservationProgramme
        fields = ('id', 'name', 'protected_features')


class CriterionSerializer(ProtectedHyperlinkedModelSerializer):
    protected_features = SpanOneToOneProtectedHyperlinkedRelatedField(many=True,
                                                                      source='protections',
                                                                      view_name='feature-detail',
                                                                      queryset=Feature.objects.all())

    class Meta:
        model = Criterion
        fields = ('id', 'criterion', 'specific_criterion', 'subcriterion', 'protected_features')


class SquareSerializer(ProtectedHyperlinkedModelSerializer):
    class Meta:
        model = Square
        fields = ('number', 'degree_of_determination', 'additional_info')


class ProtectionSerializer(ProtectedHyperlinkedModelSerializer):

    class Meta:
        model = Protection
        fields = ('reported_area', 'land_area', 'water_area', 'hiking', 'regulations', 'additional_info',
                  'criteria', 'conservation_programmes')


class FeatureLinkSerializer(serializers.ModelSerializer):
    link_type = serializers.StringRelatedField()

    class Meta:
        model = FeatureLink
        fields = ('link', 'text', 'link_type', 'ordering', 'link_text')


class FeatureSerializer(ProtectedHyperlinkedModelSerializer):
    square = SquareSerializer()
    protection = ProtectionSerializer()
    text = SerializerMethodField()
    geometry = GeometryField(source='geom')  # using transformed geometry
    links = FeatureLinkSerializer(many=True)

    def get_text(self, obj):
        # now this is a silly feature: text should not be public if text_www exists
        if obj.text_www:
            return obj.text_www
        else:
            return obj.text

    class Meta:
        model = Feature
        fields = ('url', 'name', 'fid', 'feature_class', 'geometry', 'description', 'notes', 'active',
                  'created_time', 'last_modified_time', 'number', 'area', 'text', 'values', 'publications',
                  'observations', 'habitat_type_observations', 'links', 'square', 'protection', 'transactions')


class FeatureClassSerializer(ProtectedHyperlinkedModelSerializer):

    class Meta:
        model = FeatureClass
        fields = ('url', 'name', 'additional_info', 'super_class', 'reporting', 'www', 'metadata', 'features')


class ValueSerializer(ProtectedHyperlinkedModelSerializer):
    class Meta:
        model = Value
        fields = ('url', 'explanation', 'value_type', 'date', 'link', 'features')


class PublicationSerializer(ProtectedHyperlinkedModelSerializer):
    publication_type = serializers.StringRelatedField()

    class Meta:
        model = Publication
        fields = ('url', 'publication_type', 'name', 'author', 'series', 'place_of_printing', 'year',
                  'additional_info', 'link', 'features')


class SpeciesSerializer(ProtectedHyperlinkedModelSerializer):
    class Meta:
        model = Species
        fields = ('url', 'code', 'taxon', 'taxon_1', 'name_fi', 'name_sci_1', 'name_subspecies_1', 'registry_date',
                  'regulations', 'observations')


class AbundanceSerializer(ProtectedHyperlinkedModelSerializer):
    class Meta:
        model = Abundance
        fields = ('id', 'value', 'explanation', 'source')


class FrequencySerializer(ProtectedHyperlinkedModelSerializer):
    class Meta:
        model = Frequency
        fields = ('id', 'value', 'explanation', 'source')


class MigrationClassSerializer(ProtectedHyperlinkedModelSerializer):
    class Meta:
        model = MigrationClass
        fields = ('id', 'value', 'explanation', 'source')


class OriginSerializer(ProtectedHyperlinkedModelSerializer):
    class Meta:
        model = Origin
        fields = ('id', 'explanation', 'source')


class BreedingDegreeSerializer(ProtectedHyperlinkedModelSerializer):
    class Meta:
        model = BreedingDegree
        fields = ('id', 'value', 'explanation', 'source')


class ObservationSerializer(ProtectedHyperlinkedModelSerializer):
    occurrence = serializers.StringRelatedField()
    abundance = AbundanceSerializer()
    frequency = FrequencySerializer()
    migration_class = MigrationClassSerializer()
    origin = OriginSerializer()
    breeding_degree = BreedingDegreeSerializer()

    class Meta:
        model = Observation
        fields = (
            'url', 'feature', 'species', 'series', 'abundance',
            'frequency', 'number', 'migration_class', 'origin',
            'breeding_degree', 'description', 'notes', 'date',
            'occurrence', 'created_time', 'last_modified_time',
        )


class ObservationSeriesSerializer(ProtectedHyperlinkedModelSerializer):
    class Meta:
        model = ObservationSeries
        fields = ('url', 'name', 'description', 'start_date', 'end_date', 'method', 'notes', 'additional_info',
                  'valid', 'observations', 'habitat_type_observations')


class TransactionTypeSerializer(ProtectedHyperlinkedModelSerializer):
    class Meta:
        model = TransactionType
        fields = ('id', 'name')


class TransactionSerializer(ProtectedHyperlinkedModelSerializer):
    transaction_type = TransactionTypeSerializer()

    class Meta:
        model = Transaction
        fields = ('url', 'register_id', 'description', 'transaction_type', 'date', 'link', 'features', 'regulations')


class PersonSerializer(ProtectedHyperlinkedModelSerializer):
    class Meta:
        model = Person


class RegulationSerializer(ProtectedHyperlinkedModelSerializer):
    class Meta:
        model = Regulation
        fields = ('url', 'name', 'paragraph', 'additional_info', 'value', 'value_explanation', 'valid',
                  'date_of_entry', 'link', 'species', 'transactions', 'habitat_types')


class HabitatTypeSerializer(ProtectedHyperlinkedModelSerializer):
    class Meta:
        model = HabitatType
        fields = ('url', 'name', 'code', 'description', 'additional_info', 'group', 'regulations',
                  'habitat_type_observations')


class HabitatTypeObservationSerializer(ProtectedHyperlinkedModelSerializer):
    class Meta:
        model = HabitatTypeObservation
        fields = ('url', 'feature', 'habitat_type', 'group_fraction', 'additional_info', 'observation_series',
                  'created_time', 'last_modified_time')


class FeatureViewSet(ProtectedViewSet):
    queryset = Feature.objects.all().annotate(geom=Transform('geometry', 4326))  # display coordinates in WGS84
    serializer_class = FeatureSerializer


class FeatureClassViewSet(ProtectedViewSet):
    queryset = FeatureClass.objects.all()
    serializer_class = FeatureClassSerializer


class ValueViewSet(ProtectedViewSet):
    queryset = Value.objects.all()
    serializer_class = ValueSerializer


class PublicationViewSet(ProtectedViewSet):
    queryset = Publication.objects.all()
    serializer_class = PublicationSerializer


class RegulationViewSet(ProtectedViewSet):
    queryset = Regulation.objects.all()
    serializer_class = RegulationSerializer


class SpeciesViewSet(ProtectedViewSet):
    queryset = Species.objects.all()
    serializer_class = SpeciesSerializer


class ObservationViewSet(ProtectedViewSet):
    queryset = Observation.objects.all()
    serializer_class = ObservationSerializer


class ObservationSeriesViewSet(ProtectedViewSet):
    queryset = ObservationSeries.objects.all()
    serializer_class = ObservationSeriesSerializer


class HabitatTypeViewSet(ProtectedViewSet):
    queryset = HabitatType.objects.all()
    serializer_class = HabitatTypeSerializer


class HabitatTypeObservationViewSet(ProtectedViewSet):
    queryset = HabitatTypeObservation.objects.all()
    serializer_class = HabitatTypeObservationSerializer


class TransactionViewSet(ProtectedViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class AbundanceViewSet(ProtectedViewSet):
    queryset = Abundance.objects.all()
    serializer_class = AbundanceSerializer


class FrequencyViewSet(ProtectedViewSet):
    queryset = Frequency.objects.all()
    serializer_class = FrequencySerializer


class MigrationClassViewSet(ProtectedViewSet):
    queryset = MigrationClass.objects.all()
    serializer_class = MigrationClassSerializer


class OriginViewSet(ProtectedViewSet):
    queryset = Origin.objects.all()
    serializer_class = OriginSerializer


class BreedingDegreeViewSet(ProtectedViewSet):
    queryset = BreedingDegree.objects.all()
    serializer_class = BreedingDegreeSerializer


class ProtectionCriterionViewSet(ProtectedViewSet):
    queryset = Criterion.objects.all()
    serializer_class = CriterionSerializer


class ConservationProgrammeViewSet(ProtectedViewSet):
    queryset = ConservationProgramme.objects.all()
    serializer_class = ConservationProgrammeSerializer


router = routers.DefaultRouter()
router.register(r'feature', FeatureViewSet)
router.register(r'feature_class', FeatureClassViewSet)
router.register(r'value', ValueViewSet)
router.register(r'species', SpeciesViewSet)
router.register(r'observation', ObservationViewSet)
router.register(r'observation_series', ObservationSeriesViewSet)
router.register(r'habitat_type', HabitatTypeViewSet)
router.register(r'habitat_type_observation', HabitatTypeObservationViewSet)
router.register(r'publication', PublicationViewSet)
router.register(r'regulation', RegulationViewSet)
router.register(r'transaction', TransactionViewSet)
router.register(r'protection_criterion', ProtectionCriterionViewSet)
router.register(r'conservation_programme', ConservationProgrammeViewSet)
