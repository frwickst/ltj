# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.geos import GEOSException
from django.utils.translation import ugettext_lazy as _

PROTECTION_LEVELS = {
    'ADMIN_ONLY': 1,
    'ADMIN_AND_STAFF': 2,
    'PUBLIC': 3,
}

AUTHORIZATION_LEVELS = {
    'ADMIN': 1,
    'OFFICER': 2,
    'PUBLIC': 3,
    'OPEN_DATA': 4,
}

AUTHORIZATION_PROTECTION_MAP = {
    AUTHORIZATION_LEVELS['ADMIN']: [
        PROTECTION_LEVELS['ADMIN_ONLY'],
        PROTECTION_LEVELS['ADMIN_AND_STAFF'],
        PROTECTION_LEVELS['PUBLIC']
    ],
    AUTHORIZATION_LEVELS['OFFICER']: [
        PROTECTION_LEVELS['ADMIN_AND_STAFF'],
        PROTECTION_LEVELS['PUBLIC']
    ],
    AUTHORIZATION_LEVELS['PUBLIC']: [PROTECTION_LEVELS['PUBLIC']],
    AUTHORIZATION_LEVELS['OPEN_DATA']: [PROTECTION_LEVELS['PUBLIC']],
}


class ProtectedQuerySet(models.QuerySet):
    def __init__(self, model=None, *args, **kwargs):
        self._model_fields = []
        if model:
            self._model_fields = [f.name for f in model._meta.get_fields()]
        super().__init__(model=model, *args, **kwargs)

    def for_admin(self):
        return self.filter_protected(AUTHORIZATION_LEVELS['ADMIN'])

    def for_admin_and_staff(self):
        return self.filter_protected(AUTHORIZATION_LEVELS['OFFICER'])

    def for_public(self):
        return self.filter_protected(AUTHORIZATION_LEVELS['PUBLIC'])

    def open_data(self):
        return self.filter_protected(AUTHORIZATION_LEVELS['OPEN_DATA'])

    def filter_protected(self, auth_level=AUTHORIZATION_LEVELS['OPEN_DATA']):
        protection_levels = AUTHORIZATION_PROTECTION_MAP[auth_level]
        open_data_only = auth_level == AUTHORIZATION_LEVELS['OPEN_DATA']

        filters = self._create_qs_filters(protection_levels, open_data_only)

        return self.filter(**filters)

    def _create_qs_filters(self, protection_levels, open_data_only):
        filters = {}

        filters.update(self._create_protection_level_filters(protection_levels=protection_levels))

        if open_data_only:
            filters.update(self._create_open_data_filters())
        return filters

    def _create_open_data_filters(self):
        """
        Creates a queryset filter dict based on open data restrictions

        If the model includes fields that have open data restrictions
        or if the model has open data restrictions directly, those fields
        or relations are checked in order to make sure that only open data
        instance are included.
        """
        filters = {}
        if 'feature' in self._model_fields:
            filters['feature__feature_class__open_data'] = True
        elif 'feature_class' in self._model_fields:
            filters['feature_class__open_data'] = True

        if 'open_data' in self._model_fields:
            filters['open_data'] = True

        return filters

    def _create_protection_level_filters(self, protection_levels):
        """
        Creates a queryset filter dict base on given permission levels

        If the model includes fields that have protection level restrictions
        or if the model has protection level restrictions directly, those fields
        or relations are checked in order to make sure that only instances
        matching the `protection_level` parameter are included.
        """
        filters = {}
        if 'feature' in self._model_fields:
            filters['feature__protection_level__in'] = protection_levels

        if 'protection_level' in self._model_fields:
            filters['protection_level__in'] = protection_levels

        return filters


class ProtectionLevelMixin(models.Model):
    PROTECTION_LEVEL_CHOICES = (
        (PROTECTION_LEVELS['ADMIN_ONLY'], "Administrators only"),
        (PROTECTION_LEVELS['ADMIN_AND_STAFF'], "Administrators and staff"),
        (PROTECTION_LEVELS['PUBLIC'], "Public"),
    )

    protection_level = models.IntegerField(_('protection level'), choices=PROTECTION_LEVEL_CHOICES,
                                           default=PROTECTION_LEVELS['PUBLIC'], db_column='suojaustasoid')

    objects = ProtectedQuerySet.as_manager()

    class Meta:
        abstract = True


class PermissiveGeometryField(models.GeometryField):
    """
    Required to catch exceptions if curved geometries are encountered. Currently, the GEOS library, GeoDjango
    and GeoJSON do not support curved geometries.
    """

    def from_db_value(self, value, expression, connection, context):
        try:
            value = super().from_db_value(value, expression, connection, context)
        except GEOSException:
            value = None
        return value


class Origin(models.Model):
    explanation = models.CharField(_('explanation'), max_length=50, blank=True, null=True, db_column='selitys')
    source = models.CharField(_('source'), max_length=50, blank=True, null=True, db_column='lahde')

    class Meta:
        ordering = ['id']
        db_table = 'alkupera'
        verbose_name = _('origin')
        verbose_name_plural = _('origins')

    def __str__(self):
        return str(self.explanation)


class Value(models.Model):
    explanation = models.CharField(_('explanation'), max_length=50, blank=True, null=True, db_column='selite')
    value = models.CharField(_('value class'), max_length=10, blank=True, null=True, db_column='luokka')
    valuator = models.CharField(_('valuator'), max_length=50, blank=True, null=True, db_column='arvottaja')
    date = models.DateField(_('date'), blank=True, null=True, db_column='pvm')
    link = models.CharField(_('link'), max_length=4000, blank=True, null=True, db_column='linkki')

    class Meta:
        ordering = ['id']
        db_table = 'arvo'
        verbose_name = _('value')
        verbose_name_plural = _('values')

    def __str__(self):
        return str(self.explanation)


class FeatureValue(models.Model):
    """Through model for Value & Feature m2m relation"""
    value = models.ForeignKey(Value, models.CASCADE, db_column='arvoid', verbose_name=_('value'))
    feature = models.ForeignKey('Feature', models.CASCADE, db_column='kohdeid', verbose_name=_('feature'))

    objects = ProtectedQuerySet.as_manager()

    class Meta:
        db_table = 'arvo_kohde'
        unique_together = (('value', 'feature'),)
        verbose_name = _('feature value')
        verbose_name_plural = _('features values')


class Occurrence(models.Model):
    explanation = models.CharField(_('explanation'), max_length=50, blank=True, null=True, db_column='selitys')

    class Meta:
        ordering = ['id']
        db_table = 'esiintyma'
        verbose_name = _('occurrence')
        verbose_name_plural = _('occurrences')

    def __str__(self):
        return str(self.explanation)


class ObservationSeries(models.Model):
    name = models.CharField(_('name'), max_length=50, blank=True, null=True, db_column='nimi')
    person = models.ForeignKey('Person', models.PROTECT, blank=True, null=True, db_column='hloid',
                               related_name='observation_series', verbose_name=_('person'))
    description = models.CharField(_('description'), max_length=255, blank=True, null=True, db_column='kuvaus')
    start_date = models.DateField(_('start date'), blank=True, null=True, db_column='alkupvm')
    end_date = models.DateField(_('end date'), blank=True, null=True, db_column='loppupvm')
    method = models.CharField(_('method'), max_length=255, blank=True, null=True, db_column='menetelma')
    notes = models.CharField(_('notes'), max_length=255, blank=True, null=True, db_column='huomioitavaa')
    additional_info = models.CharField(_('additional info'), max_length=255, blank=True, null=True,
                                       db_column='lisatieto')
    valid = models.BooleanField(_('valid'), db_column='voimassa')

    class Meta:
        ordering = ['id']
        db_table = 'havaintosarja'
        verbose_name = _('observation series')
        verbose_name_plural = _('observation series')

    def __str__(self):
        return self.name or 'Observation series {0}'.format(self.id)


class Person(models.Model):
    surname = models.CharField(_('surname'), max_length=25, blank=True, null=True, db_column='sukunimi')
    first_name = models.CharField(_('first name'), max_length=25, blank=True, null=True, db_column='etunimi')
    expertise = models.CharField(_('expertise'), max_length=150, blank=True, null=True, db_column='asiantuntemus')
    notes = models.CharField(_('notes'), max_length=255, blank=True, null=True, db_column='huomioitavaa')
    company = models.CharField(_('company'), max_length=100, blank=True, null=True, db_column='yritys')
    public_servant = models.BooleanField(_('public servant'), db_column='viranomainen')
    telephone = models.CharField(_('telephone'), max_length=50, blank=True, null=True, db_column='puhnro')
    email = models.CharField(_('email'), max_length=100, blank=True, null=True, db_column='email')
    created_time = models.DateTimeField(_('created time'), blank=True, null=True, auto_now_add=True,
                                        db_column='lisaysaika')

    class Meta:
        ordering = ['id']
        db_table = 'henkilo'
        verbose_name = _('person')
        verbose_name_plural = _('persons')

    def __str__(self):
        return '{0} {1}'.format(self.first_name, self.surname)


class Publication(models.Model):
    name = models.CharField(_('name'), max_length=150, blank=True, null=True, db_column='nimi')
    author = models.CharField(_('author'), max_length=100, blank=True, null=True, db_column='tekija')
    series = models.CharField(_('series'), max_length=100, blank=True, null=True, db_column='sarja')
    place_of_printing = models.CharField(_('place of printing'), max_length=50, blank=True, null=True,
                                         db_column='painopaikka')
    year = models.CharField(_('year'), max_length=50, blank=True, null=True, db_column='vuosi')
    additional_info = models.CharField(_('additional information'), max_length=255, blank=True, null=True,
                                       db_column='lisatieto')
    publication_type = models.ForeignKey('PublicationType', models.PROTECT, db_column='julktyyppiid',
                                         related_name='publications', verbose_name=_('publication type'))
    link = models.CharField(_('link'), max_length=4000, blank=True, null=True, db_column='linkki')

    class Meta:
        ordering = ['id']
        db_table = 'julkaisu'
        verbose_name = _('publication')
        verbose_name_plural = _('publications')

    def __str__(self):
        return str(self.name)


class PublicationType(models.Model):
    name = models.CharField(_('name'), max_length=20, blank=True, null=True, db_column='nimi')

    class Meta:
        ordering = ['id']
        db_table = 'julktyyppi'
        verbose_name = _('publication type')
        verbose_name_plural = _('publication types')

    def __str__(self):
        return str(self.name)


class AbstractFeature(ProtectionLevelMixin, models.Model):
    """AbstractFeature model that provides common fields for Feature and HistoricalFeature """
    fid = models.CharField(_('fid'), max_length=10, blank=True, null=True, db_column='tunnus')
    geometry = PermissiveGeometryField(db_column='geometry1', srid=settings.SRID, verbose_name=_('geometry'))
    name = models.CharField(_('name'), max_length=80, blank=True, null=True, db_column='nimi')
    description = models.CharField(_('description'), max_length=255, blank=True, null=True, db_column='kuvaus')
    notes = models.CharField(_('notes'), max_length=255, blank=True, null=True, db_column='huom')
    active = models.BooleanField(_('active'), db_column='voimassa', default=True)
    created_time = models.DateField(_('created time'), blank=True, null=True, auto_now_add=True, db_column='digipvm')
    number = models.IntegerField(_('number'), blank=True, null=True, db_column='numero')
    created_by = models.CharField(_('created by'), max_length=50, blank=True, null=True, db_column='digitoija')
    last_modified_time = models.DateTimeField(_('last modified time'), blank=True, null=True, auto_now=True,
                                              db_column='pvm_editoitu')
    last_modified_by = models.CharField(_('last modified by'), max_length=150, blank=True, null=True,
                                        db_column='muokkaaja')
    area = models.FloatField(_('area (ha)'), blank=True, null=True, editable=False, db_column='pinta_ala')
    text = models.CharField(_('text'), max_length=40000, blank=True, null=True, db_column='teksti')
    text_www = models.CharField(_('text www'), max_length=40000, blank=True, null=True, db_column='teksti_www')

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.geometry and self.geometry.dims == 2:
            # save area for Polygon, MultiPolygon or GeometryCollection with Polygon
            # or MultiPolygon
            self.area = self.geometry.area / 10000  # area in hectare
        super().save(*args, **kwargs)

    @property
    def formatted_area(self):
        if not self.area:
            return 0.0
        return float("{0:.2f}".format(self.area))


class Feature(AbstractFeature):
    feature_class = models.ForeignKey('FeatureClass', models.PROTECT, db_column='luokkatunnus', related_name='features',
                                      verbose_name=_('feature class'))
    values = models.ManyToManyField('Value', through=FeatureValue, related_name='features', verbose_name=_('values'))
    publications = models.ManyToManyField('Publication', through='FeaturePublication', related_name='features',
                                          verbose_name=_('publications'))

    class Meta:
        ordering = ['id']
        db_table = 'kohde'
        verbose_name = _('feature')
        verbose_name_plural = _('features')

    def __str__(self):
        return self.name or 'Feature {0}'.format(self.id)

    @property
    def is_protected(self):
        return self.feature_class.is_protected

    @property
    def is_square(self):
        return self.feature_class.is_square


class HistoricalFeature(AbstractFeature):
    feature_class = models.ForeignKey('FeatureClass', models.PROTECT, db_column='luokkatunnus',
                                      related_name='historical_features', verbose_name=_('feature class'))
    archived_time = models.DateTimeField(_('archived time'), db_column='historia_pvm')
    feature = models.ForeignKey(Feature, models.SET_NULL, db_column='kohde_id', blank=True, null=True,
                                related_name='historical_features', verbose_name=_('feature'))

    class Meta:
        ordering = ['id']
        db_table = 'kohde_historia'
        verbose_name = _('historical feature')
        verbose_name_plural = _('historical features')

    def __str__(self):
        return self.name or 'Historical feature {0}'.format(self.id)


class FeaturePublication(models.Model):
    """Through model for Feature & Publication m2m relation"""
    feature = models.ForeignKey(Feature, models.CASCADE, db_column='kohdeid', verbose_name=_('feature'))
    publication = models.ForeignKey(Publication, models.CASCADE, db_column='julkid', verbose_name=_('publication'))

    objects = ProtectedQuerySet.as_manager()

    class Meta:
        db_table = 'kohde_julk'
        unique_together = (('feature', 'publication'),)
        verbose_name = _('feature publication')
        verbose_name_plural = _('feature publications')


class FeatureLink(ProtectionLevelMixin, models.Model):
    feature = models.ForeignKey(Feature, models.CASCADE, db_column='tekstiid', related_name='links',
                                verbose_name=_('feature'))
    link = models.CharField(_('link'), max_length=4000, blank=True, null=True, db_column='linkki')
    text = models.CharField(_('text'), max_length=4000, blank=True, null=True, db_column='linkkiteksti')
    link_type = models.ForeignKey('LinkType', models.PROTECT, db_column='tyyppiid', verbose_name=_('link type'))
    ordering = models.IntegerField(_('ordering'), blank=True, null=True, db_column='jarjestys')
    link_text = models.CharField(_('link text'), max_length=100, blank=True, null=True, db_column='linkin_teksti')

    class Meta:
        ordering = ['id']
        db_table = 'kohdelinkki'
        verbose_name = _('feature link')
        verbose_name_plural = _('feature links')

    def __str__(self):
        return str(self.link)


class SpeciesRegulation(models.Model):
    """Through model for Species & Regulation m2m relation"""
    species = models.ForeignKey('Species', models.CASCADE, db_column='lajid', verbose_name=_('species'))
    regulation = models.ForeignKey('Regulation', models.CASCADE, db_column='saaid', verbose_name=_('regulation'))

    class Meta:
        db_table = 'laj_saa'
        unique_together = (('species', 'regulation'),)
        verbose_name = _('species regulation')
        verbose_name_plural = _('species regulations')


class Observation(ProtectionLevelMixin, models.Model):
    code = models.CharField(_('code'), max_length=100, blank=True, null=True, db_column='hav_koodi')
    # This field should be filled and unique, but we do not know the values yet, see details
    # in https://github.com/City-of-Helsinki/ltj/issues/4
    uri = models.URLField(_('uri'), blank=True)
    feature = models.ForeignKey(Feature, models.PROTECT, db_column='kohdeid', related_name='observations',
                                verbose_name=_('feature'))
    species = models.ForeignKey('Species', models.PROTECT, db_column='lajid', related_name='observations',
                                verbose_name=_('species'))
    series = models.ForeignKey(ObservationSeries, models.PROTECT, db_column='hsaid', blank=True, null=True,
                               related_name='observations', verbose_name=_('series'))
    abundance = models.ForeignKey('Abundance', models.PROTECT, db_column='runsausid', blank=True, null=True,
                                  related_name='observations', verbose_name=_('abundance'))
    frequency = models.ForeignKey('Frequency', models.PROTECT, db_column='yleisyysid', blank=True, null=True,
                                  related_name='observations', verbose_name=_('frequence'))
    observer = models.ForeignKey(Person, models.PROTECT, db_column='hloid', blank=True, null=True,
                                 related_name='observations', verbose_name=_('observer'))
    number = models.CharField(_('number'), max_length=30, blank=True, null=True, db_column='lkm')
    migration_class = models.ForeignKey('MigrationClass', models.PROTECT, db_column='liikkumislkid', blank=True,
                                        null=True,
                                        related_name='observations',
                                        verbose_name=_('migration class'))
    origin = models.ForeignKey(Origin, models.PROTECT, db_column='alkuperaid', blank=True, null=True,
                               related_name='observations', verbose_name=_('origin'))
    breeding_degree = models.ForeignKey('BreedingDegree', models.PROTECT, db_column='pesimisvarmuusid', blank=True,
                                        null=True, related_name='observations', verbose_name=_('breeding degree'))
    description = models.CharField(_('description'), max_length=255, blank=True, null=True, db_column='kuvaus')
    notes = models.CharField(_('notes'), max_length=100, blank=True, null=True, db_column='huom')
    date = models.DateField(_('date'), blank=True, null=True, db_column='pvm')
    occurrence = models.ForeignKey(Occurrence, models.PROTECT, db_column='esiintymaid', blank=True, null=True,
                                   verbose_name=_('occurrence'))
    created_time = models.DateTimeField(_('created time'), auto_now_add=True, db_column='pvm_luotu')
    last_modified_time = models.DateTimeField(_('last modified time'), blank=True, null=True, auto_now=True,
                                              db_column='pvm_editoitu')

    class Meta:
        ordering = ['id']
        db_table = 'lajihavainto'
        verbose_name = _('observation')
        verbose_name_plural = _('observations')

    def __str__(self):
        return self.code or 'Observation {0}'.format(self.id)


class Species(ProtectionLevelMixin, models.Model):
    taxon = models.CharField(_('taxon'), max_length=5, blank=True, null=True, db_column='ryhma')
    taxon_1 = models.CharField(_('taxon 1'), max_length=50, blank=True, null=True, db_column='elioryhma1')
    taxon_2 = models.CharField(_('taxon 2'), max_length=50, blank=True, null=True, db_column='elioryhma2')
    order_fi = models.CharField(_('order (fi)'), max_length=150, blank=True, null=True, db_column='lahko_suomi')
    order_la = models.CharField(_('order (la)'), max_length=150, blank=True, null=True, db_column='lahko_tiet')
    family_fi = models.CharField(_('family (fi)'), max_length=150, blank=True, null=True, db_column='heimo_suomi')
    family_la = models.CharField(_('family (la)'), max_length=150, blank=True, null=True, db_column='heimo_tiet')
    name_fi = models.CharField(_('name (fi)'), max_length=150, blank=True, null=True, db_column='nimi_suomi1')
    name_fi_2 = models.CharField(_('name 2 (fi)'), max_length=150, blank=True, null=True, db_column='nimi_suomi2')
    name_sci_1 = models.CharField(_('scientific name 1'), max_length=150, blank=True, null=True, db_column='nimi_tiet1')
    name_sci_2 = models.CharField(_('scientific name 2'), max_length=150, blank=True, null=True, db_column='nimi_tiet2')
    name_subspecies_1 = models.CharField(_('subspecies 1'), max_length=150, blank=True, null=True, db_column='alalaji1')
    name_subspecies_2 = models.CharField(_('subscecies 2'), max_length=150, blank=True, null=True, db_column='alalaji2')
    author_1 = models.CharField(_('author 1'), max_length=150, blank=True, null=True, db_column='auktori1')
    author_2 = models.CharField(_('author 2'), max_length=150, blank=True, null=True, db_column='auktori2')
    name_abbreviated_1 = models.CharField(_('name abbreviated 1'), max_length=10, blank=True, null=True,
                                          db_column='nimilyhenne1')
    name_abbreviated_2 = models.CharField(_('name abbreviated 2'), max_length=10, blank=True, null=True,
                                          db_column='nimilyhenne2')
    name_sv = models.CharField(_('name (sv)'), max_length=150, blank=True, null=True, db_column='nimi_ruotsi')
    name_en = models.CharField(_('name (en)'), max_length=150, blank=True, null=True, db_column='nimi_englanti')
    registry_date = models.DateTimeField(_('registry date'), blank=True, null=True, db_column='rekisteripvm')
    additional_info = models.CharField(_('additional info'), max_length=255, blank=True, null=True,
                                       db_column='lisatieto')
    code = models.CharField(_('code'), max_length=100, blank=True, null=True, db_column='koodi')
    link = models.CharField(_('link'), max_length=4000, blank=True, null=True, db_column='linkki')
    regulations = models.ManyToManyField('Regulation', through=SpeciesRegulation, related_name='species',
                                         verbose_name=_('regulations'))

    class Meta:
        ordering = ['id']
        db_table = 'lajirekisteri'
        verbose_name = _('species')
        verbose_name_plural = _('species')

    def __str__(self):
        name_list = [self.name_fi, self.name_sci_1, self.name_subspecies_1]
        return ', '.join([name for name in name_list if name])


class MigrationClass(models.Model):
    explanation = models.CharField(_('explanation'), max_length=50, blank=True, null=True, db_column='selitys')
    source = models.CharField(_('source'), max_length=50, blank=True, null=True, db_column='lahde')
    value = models.IntegerField(_('value'), blank=True, null=True, db_column='arvo')

    class Meta:
        ordering = ['id']
        db_table = 'liikkumislk'
        verbose_name = _('migration class')
        verbose_name_plural = _('migration class')

    def __str__(self):
        return str(self.explanation)


class LinkType(models.Model):
    name = models.CharField(_('name'), max_length=20, blank=True, null=True, db_column='nimi')  # type name

    class Meta:
        ordering = ['id']
        db_table = 'linkkityyppi'
        verbose_name = _('link type')
        verbose_name_plural = _('link types')

    def __str__(self):
        return str(self.name)


class HabitatTypeRegulation(models.Model):
    """Through model for HabitatType & Regulation m2m relation"""
    habitat_type = models.ForeignKey('HabitatType', models.CASCADE, db_column='ltyyppiid',
                                     verbose_name=_('habitat type'))
    regulation = models.ForeignKey('Regulation', models.CASCADE, db_column='saadosid', verbose_name=_('regulation'))

    class Meta:
        db_table = 'ltyyppi_saados'
        unique_together = (('habitat_type', 'regulation'),)
        verbose_name = _('habitat type regulation')
        verbose_name_plural = _('habitat type regulations')


class HabitatTypeObservation(models.Model):
    feature = models.ForeignKey(Feature, models.PROTECT, db_column='kohdeid', related_name='habitat_type_observations',
                                verbose_name=_('feature'))
    habitat_type = models.ForeignKey('HabitatType', models.PROTECT, db_column='ltyypid',
                                     related_name='habitat_type_observations', verbose_name=_('habitat type'))
    group_fraction = models.IntegerField(_('group fraction'), blank=True, null=True, db_column='osuus_kuviosta')
    additional_info = models.CharField(_('additional info'), max_length=255, blank=True, null=True,
                                       db_column='lisatieto')
    observation_series = models.ForeignKey(ObservationSeries, models.PROTECT, db_column='hsaid',
                                           related_name='habitat_type_observations',
                                           verbose_name=_('observation series'))
    created_time = models.DateTimeField(_('created time'), auto_now_add=True, db_column='pvm_luotu')
    last_modified_time = models.DateTimeField(_('last modified time'), blank=True, null=True, auto_now=True,
                                              db_column='pvm_editoitu')

    objects = ProtectedQuerySet.as_manager()

    class Meta:
        ordering = ['id']
        db_table = 'ltyyppihavainto'
        verbose_name = _('habitat type observation')
        verbose_name_plural = _('habitat type observations')

    def __str__(self):
        return '{0} {1}'.format(self.habitat_type, self.feature)


class HabitatType(models.Model):
    name = models.CharField(_('name'), max_length=50, blank=True, null=True, db_column='nimi')
    code = models.CharField(_('code'), max_length=10, blank=True, null=True, db_column='koodi')
    description = models.CharField(_('description'), max_length=255, blank=True, null=True, db_column='kuvaus')
    additional_info = models.CharField(_('additional info'), max_length=255, blank=True, null=True,
                                       db_column='lisatieto')
    group = models.CharField(_('group'), max_length=50, blank=True, null=True, db_column='ltyyppiryhma')
    regulations = models.ManyToManyField('Regulation', through=HabitatTypeRegulation, related_name='habitat_types',
                                         verbose_name=_('regulations'))

    class Meta:
        ordering = ['id']
        db_table = 'ltyyppirekisteri'
        verbose_name = _('habitat type')
        verbose_name_plural = _('habitat types')

    def __str__(self):
        return str(self.name)


class FeatureClass(models.Model):
    PROTECTED_SUPER_CLASS_ID = 'SK'
    SQUARE_SUPER_CLASS_ID = 'RK'

    id = models.CharField(_('id'), primary_key=True, max_length=10, db_column='tunnus')
    name = models.CharField(_('name'), max_length=50, blank=True, null=True, db_column='nimi')
    additional_info = models.CharField(_('additional info'), max_length=255, blank=True, null=True,
                                       db_column='lisatieto')
    super_class = models.ForeignKey('FeatureClass', models.PROTECT, blank=True, null=True, db_column='paatunnus',
                                    related_name='subclasses', verbose_name=_('super class'))
    reporting = models.BooleanField(_('reporting'), db_column='raportointi', default=True)
    open_data = models.BooleanField(_('open data'), db_column='avoin_data', default=False)
    www = models.BooleanField(_('www'), default=True)
    metadata = models.CharField(_('metadata'), max_length=4000, blank=True, null=True)

    objects = ProtectedQuerySet.as_manager()

    class Meta:
        ordering = ['id']
        db_table = 'luokka'
        verbose_name = _('feature class')
        verbose_name_plural = _('feature classes')

    def __str__(self):
        return self.name or 'Feature class {0}'.format(self.id)

    @property
    def is_protected(self):
        return self.super_class_id == self.PROTECTED_SUPER_CLASS_ID

    @property
    def is_square(self):
        return self.super_class_id == self.SQUARE_SUPER_CLASS_ID


class BreedingDegree(models.Model):
    explanation = models.CharField(_('explanation'), max_length=50, blank=True, null=True, db_column='selitys')
    source = models.CharField(_('source'), max_length=50, blank=True, null=True, db_column='lahde')
    value = models.CharField(_('value'), max_length=50, blank=True, null=True, db_column='arvo')

    class Meta:
        ordering = ['id']
        db_table = 'pesimisvarmuus'
        verbose_name = _('breeding degree')
        verbose_name_plural = _('breeding degrees')

    def __str__(self):
        return str(self.explanation)


class Abundance(models.Model):
    explanation = models.CharField(_('explanation'), max_length=50, blank=True, null=True, db_column='selitys')
    source = models.CharField(_('source'), max_length=50, blank=True, null=True, db_column='lahde')
    value = models.CharField(_('value'), max_length=5, blank=True, null=True, db_column='arvo')

    class Meta:
        ordering = ['id']
        db_table = 'runsaus'
        verbose_name = _('abundance')
        verbose_name_plural = _('abundance')

    def __str__(self):
        return str(self.explanation)


class Square(models.Model):
    id = models.OneToOneField(Feature, models.CASCADE, db_column='id', primary_key=True, related_name='square',
                              verbose_name=_('id'))
    number = models.CharField(_('number'), max_length=10, blank=True, null=True, db_column='nro')
    degree_of_determination = models.IntegerField(_('degree of determination'), blank=True, null=True,
                                                  db_column='selvitysaste')
    additional_info = models.CharField(_('additional info'), max_length=255, blank=True, null=True,
                                       db_column='lisatieto')

    class Meta:
        ordering = ['id']
        db_table = 'ruutu'
        verbose_name = _('square')
        verbose_name_plural = _('squares')

    def __str__(self):
        return str(self.number)


class Regulation(models.Model):
    name = models.CharField(_('name'), max_length=255, blank=True, null=True, db_column='nimi')
    paragraph = models.CharField(_('paragraph'), max_length=100, blank=True, null=True, db_column='pykala')
    additional_info = models.CharField(_('additional info'), max_length=255, blank=True, null=True,
                                       db_column='lisatieto')
    value = models.CharField(_('value'), max_length=10, blank=True, null=True, db_column='arvo')
    value_explanation = models.CharField(_('value explanation'), max_length=255, blank=True, null=True,
                                         db_column='arvon_selitys')
    valid = models.BooleanField(_('valid'), db_column='voimassa')
    date_of_entry = models.DateTimeField(_('date of entry'), blank=True, null=True, db_column='voimaantulo')
    link = models.CharField(_('link'), max_length=4000, blank=True, null=True, db_column='linkki')

    class Meta:
        ordering = ['id']
        db_table = 'saados'
        verbose_name = _('regulation')
        verbose_name_plural = _('regulations')

    def __str__(self):
        return str(self.name)


class ConservationProgramme(models.Model):
    name = models.CharField(_('name'), max_length=20, blank=True, null=True, db_column='nimi')

    class Meta:
        ordering = ['id']
        db_table = 'sohjelma'
        verbose_name = _('conservation programme')
        verbose_name_plural = _('conservation programmes')

    def __str__(self):
        return str(self.name)


class ProtectionCriterion(models.Model):
    """Through model for Protection & Criterion m2m relation """
    criterion = models.ForeignKey('Criterion', models.CASCADE, db_column='perusteid', verbose_name=_('criterion'))
    protection = models.ForeignKey('Protection', models.CASCADE, db_column='suoid', verbose_name=_('protection'))

    class Meta:
        db_table = 'suo_peruste'
        unique_together = (('criterion', 'protection'),)
        verbose_name = _('protection criterion')
        verbose_name_plural = _('protection criteria')


class ProtectionLevel(models.Model):
    explanation = models.CharField(_('explanation'), max_length=50, blank=True, null=True, db_column='selitys')

    class Meta:
        ordering = ['id']
        db_table = 'suojaustaso'
        verbose_name = _('protection level')
        verbose_name_plural = _('protection levels')

    def __str__(self):
        return str(self.explanation)


class Protection(models.Model):
    id = models.OneToOneField(Feature, models.CASCADE, db_column='id', primary_key=True, related_name='protection',
                              verbose_name=_('id'))
    reported_area = models.CharField(_('reported area'), max_length=50, blank=True, null=True,
                                     db_column='ilmoitettu_pinta_ala')
    land_area = models.CharField(_('land area'), max_length=50, blank=True, null=True, db_column='maapinta_ala')
    water_area = models.CharField(_('water area'), max_length=50, blank=True, null=True, db_column='vesipinta_ala')
    hiking = models.CharField(_('hiking'), max_length=255, blank=True, null=True, db_column='liikkuminen')
    regulations = models.CharField(_('regulations'), max_length=255, blank=True, null=True, db_column='maaraykset')
    additional_info = models.CharField(_('additional info'), max_length=255, blank=True, null=True,
                                       db_column='lisatieto')
    criteria = models.ManyToManyField('Criterion', through=ProtectionCriterion, related_name='protections',
                                      verbose_name=_('criteria'), blank=True)
    conservation_programmes = models.ManyToManyField('ConservationProgramme',
                                                     through='ProtectionConservationProgramme',
                                                     related_name='protections',
                                                     verbose_name=_('conservation programmes'),
                                                     blank=True)

    class Meta:
        ordering = ['id']
        db_table = 'suojelu'
        verbose_name = _('protection')
        verbose_name_plural = _('protections')

    def __str__(self):
        return str(self.id)


class ProtectionConservationProgramme(models.Model):
    """Through model for Protection & ConservationProgramme m2m relation"""
    protection = models.ForeignKey(Protection, models.CASCADE, db_column='suojeluid', verbose_name=_('protection'))
    conservation_programme = models.ForeignKey(ConservationProgramme, models.CASCADE, db_column='sohjelmaid',
                                               verbose_name=_('conservation programme'))

    class Meta:
        db_table = 'suojelu_sohjelma'
        unique_together = (('protection', 'conservation_programme'),)
        verbose_name = _('protection conservation programme')
        verbose_name_plural = _('protection conservation programmes')


class Criterion(models.Model):
    criterion = models.CharField(_('criterion'), max_length=50, blank=True, null=True, db_column='peruste')
    specific_criterion = models.CharField(_('specific criterion'), max_length=50, blank=True, null=True,
                                          db_column='tarkperuste')
    subcriterion = models.CharField(_('subscriterion'), max_length=50, blank=True, null=True, db_column='alaperuste')

    class Meta:
        ordering = ['id']
        db_table = 'suoperuste'
        verbose_name = _('criterion')
        verbose_name_plural = _('criteria')

    def __str__(self):
        values = [self.criterion, self.specific_criterion, self.subcriterion]
        return ', '.join([value for value in values if value is not None])


class TransactionRegulation(models.Model):
    """Through model for Transaction & Regulation m2m relation"""
    transaction = models.ForeignKey('Transaction', models.CASCADE, db_column='tapid', verbose_name=_('transaction'))
    regulation = models.ForeignKey(Regulation, models.CASCADE, db_column='saaid', verbose_name=_('regulation'))

    class Meta:
        db_table = 'tap_saados'
        unique_together = (('transaction', 'regulation'),)
        verbose_name = _('transaction regulation')
        verbose_name_plural = _('transaction regulations')


class Transaction(ProtectionLevelMixin, models.Model):
    register_id = models.CharField(_('register id'), max_length=20, blank=True, null=True, db_column='diaarinro')
    description = models.CharField(_('description'), max_length=255, blank=True, null=True, db_column='kuvaus')
    transaction_type = models.ForeignKey('TransactionType', models.PROTECT, db_column='tapahtumatyyppiid',
                                         verbose_name=_('transaction type'), related_name='transactions')
    last_modified_by = models.CharField(_('last modified by'), max_length=150, blank=True, null=True,
                                        db_column='paivittaja')
    date = models.DateField(_('date'), blank=True, null=True, db_column='pvm')
    person = models.ForeignKey(Person, models.PROTECT, db_column='hloid', blank=True, null=True,
                               verbose_name=_('person'))
    link = models.CharField(_('link'), max_length=4000, blank=True, null=True, db_column='linkki')
    features = models.ManyToManyField(Feature, through='TransactionFeature', related_name='transactions',
                                      verbose_name=_('features'))
    regulations = models.ManyToManyField(Regulation, through='TransactionRegulation', related_name='transactions',
                                         verbose_name=_('regulations'))

    class Meta:
        ordering = ['id']
        db_table = 'tapahtuma'
        verbose_name = _('transaction')
        verbose_name_plural = _('transactions')

    def __str__(self):
        return self.description or _('Transaction #{0}').format(self.id)


class TransactionFeature(models.Model):
    """Through model for Transaction & Feature m2m relation"""
    feature = models.ForeignKey(Feature, models.CASCADE, db_column='kohdeid', verbose_name=_('feature'))
    transaction = models.ForeignKey(Transaction, models.CASCADE, db_column='tapid', verbose_name=_('transaction'))

    objects = ProtectedQuerySet.as_manager()

    class Meta:
        db_table = 'tapahtuma_kohde'
        unique_together = (('feature', 'transaction'),)
        verbose_name = _('transaction feature')
        verbose_name_plural = _('transaction features')

    def __str__(self):
        return '{0} - {1}'.format(self.feature, self.transaction)


class TransactionType(models.Model):
    name = models.CharField(_('name'), max_length=20, blank=True, null=True, db_column='nimi')

    class Meta:
        ordering = ['id']
        db_table = 'tapahtumatyyppi'
        verbose_name = _('transaction type')
        verbose_name_plural = _('transaction types')

    def __str__(self):
        return str(self.name)


class Frequency(models.Model):
    explanation = models.CharField(_('explanation'), max_length=50, blank=True, null=True, db_column='selitys')
    source = models.CharField(_('source'), max_length=50, blank=True, null=True, db_column='lahde')
    value = models.CharField(_('value'), max_length=5, blank=True, null=True, db_column='arvo')

    class Meta:
        ordering = ['id']
        db_table = 'yleisyys'
        verbose_name = _('frequency')
        verbose_name_plural = _('frequencies')

    def __str__(self):
        return str(self.explanation)
