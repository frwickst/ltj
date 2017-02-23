# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class Origin(models.Model):
    id = models.IntegerField(primary_key=True)
    explanation = models.CharField(max_length=50, blank=True, null=True, db_column='selitys')
    source = models.CharField(max_length=50, blank=True, null=True, db_column='lahde')

    class Meta:
        managed = False
        db_table = 'alkupera'


class Value(models.Model):
    id = models.IntegerField(primary_key=True)
    type = models.CharField(max_length=10, blank=True, null=True, db_column='luokka')
    explanation = models.CharField(max_length=50, blank=True, null=True, db_column='selite')
    valuator = models.CharField(max_length=50, blank=True, null=True, db_column='arvottaja')
    date = models.DateField(blank=True, null=True, db_column='pvm')
    link = models.CharField(max_length=4000, blank=True, null=True, db_column='linkki')

    class Meta:
        managed = False
        db_table = 'arvo'


class ValueObject(models.Model):
    value_id = models.ForeignKey(Value, models.DO_NOTHING, db_column='arvoid')
    object_id = models.ForeignKey('Object', models.DO_NOTHING, db_column='kohdeid')

    class Meta:
        managed = False
        db_table = 'arvo_kohde'
        unique_together = (('value_id', 'object_id'),)


class Occurrence(models.Model):
    id = models.IntegerField(primary_key=True)
    explanation = models.CharField(max_length=50, blank=True, null=True, db_column='selitys')

    class Meta:
        managed = False
        db_table = 'esiintyma'


class ObservationSeries(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50, blank=True, null=True, db_column='nimi')
    person_id = models.ForeignKey('Person', models.DO_NOTHING, blank=True, null=True, db_column='hloid')
    description = models.CharField(max_length=255, blank=True, null=True, db_column='kuvaus')
    start_date = models.DateField(blank=True, null=True, db_column='alkupvm')
    end_date = models.DateField(blank=True, null=True, db_column='loppupvm')
    method = models.CharField(max_length=255, blank=True, null=True, db_column='menetelma')
    notes = models.CharField(max_length=255, blank=True, null=True, db_column='huomioitavaa')
    additional_info = models.CharField(max_length=255, blank=True, null=True, db_column='lisatieto')
    active = models.BooleanField(db_column='voimassa')

    class Meta:
        managed = False
        db_table = 'havaintosarja'


class Person(models.Model):
    id = models.IntegerField(primary_key=True)
    surname = models.CharField(max_length=25, blank=True, null=True, db_column='sukunimi')
    first_name = models.CharField(max_length=25, blank=True, null=True, db_column='etunimi')
    expertise = models.CharField(max_length=150, blank=True, null=True, db_column='asiantuntemus')
    notes = models.CharField(max_length=255, blank=True, null=True, db_column='huomioitavaa')
    company = models.CharField(max_length=100, blank=True, null=True, db_column='yritys')
    public_servant = models.BooleanField(db_column='viranomainen')
    telephone = models.CharField(max_length=50, blank=True, null=True, db_column='puhnro')
    email = models.CharField(max_length=100, blank=True, null=True, db_column='email')
    created_time = models.DateTimeField(blank=True, null=True, db_column='lisaysaika')

    class Meta:
        managed = False
        db_table = 'henkilo'


class Publication(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=150, blank=True, null=True, db_column='nimi')
    author = models.CharField(max_length=100, blank=True, null=True, db_column='tekija')
    series = models.CharField(max_length=100, blank=True, null=True, db_column='sarja')
    place_of_printing = models.CharField(max_length=50, blank=True, null=True, db_column='painopaikka')
    year = models.CharField(max_length=50, blank=True, null=True, db_column='vuosi')
    additional_info = models.CharField(max_length=255, blank=True, null=True, db_column='lisatieto')
    publication_type = models.ForeignKey('PublicationType', models.DO_NOTHING, db_column='julktyyppiid')
    link = models.CharField(max_length=4000, blank=True, null=True, db_column='linkki')

    class Meta:
        managed = False
        db_table = 'julkaisu'


class PublicationType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=20, blank=True, null=True, db_column='nimi')

    class Meta:
        managed = False
        db_table = 'julktyyppi'


class Object(models.Model):
    id = models.IntegerField(primary_key=True)
    type = models.CharField(max_length=10, blank=True, null=True, db_column='tunnus')
    object_class = models.ForeignKey('Luokka', models.DO_NOTHING, db_column='luokkatunnus')
    geometry1 = models.GeometryField()
    name = models.CharField(max_length=80, blank=True, null=True, db_column='nimi')
    description = models.CharField(max_length=255, blank=True, null=True, db_column='kuvaus')
    notes = models.CharField(max_length=255, blank=True, null=True, db_column='huom')
    active = models.BooleanField(db_column='voimassa')
    created_time = models.DateField(blank=True, null=True, db_column='digipvm')
    number = models.IntegerField(blank=True, null=True, db_column='numero')
    created_by = models.CharField(max_length=50, blank=True, null=True, db_column='digitoija')
    protection_level = models.ForeignKey('ProtectionLevel', models.DO_NOTHING, db_column='suojaustasoid')
    last_modified_time = models.DateTimeField(blank=True, null=True, db_column='pvm_editoitu')
    last_modified_by = models.CharField(max_length=10, blank=True, null=True, db_column='muokkaaja')
    area = models.FloatField(blank=True, null=True, db_column='pinta_ala')
    text = models.CharField(max_length=4000, blank=True, null=True, db_column='teksti')
    link = models.CharField(max_length=4000, blank=True, null=True, db_column='teksti_www')
    values = models.ManyToManyField(Value, through=ValueObject, related_name='objects')
    publications = models.ManyToManyField(Publication, through='ObjectPublication', related_name='objects')

    class Meta:
        managed = False
        db_table = 'kohde'


class HistoricalObject(Object):
    archived_time = models.DateTimeField(db_column='historia_pvm')
    object = models.ForeignKey(Object, models.DO_NOTHING, db_column='kohde_id')

    class Meta:
        managed = False
        db_table = 'kohde_historia'


class ObjectPublication(models.Model):
    object_id = models.ForeignKey(Object, models.DO_NOTHING, db_column='kohdeid')
    publication_id = models.ForeignKey(Publication, models.DO_NOTHING, db_column='julkid')

    class Meta:
        managed = False
        db_table = 'kohde_julk'
        unique_together = (('object_id', 'publication_id'),)


class ObjectLink(models.Model):
    id = models.IntegerField(primary_key=True)
    object = models.ForeignKey(Object, models.DO_NOTHING, db_column='tekstiid')
    link = models.CharField(max_length=4000, blank=True, null=True, db_column='link')
    text = models.CharField(max_length=4000, blank=True, null=True, db_column='linkkiteksti')
    type = models.ForeignKey('LinkType', models.DO_NOTHING, db_column='tyyppiid')
    ordering = models.IntegerField(blank=True, null=True, db_column='jarjestys')
    link_text = models.CharField(max_length=1000, blank=True, null=True, db_column='linkin_teksti ')
    protection_level = models.ForeignKey('ProtectionLevel', models.DO_NOTHING, db_column='suojaustasoid')

    class Meta:
        managed = False
        db_table = 'kohdelinkki'


class SpeciesRegulation(models.Model):
    species_id = models.ForeignKey('Species', models.DO_NOTHING, db_column='lajid')
    regulation_id = models.ForeignKey('Regulation', models.DO_NOTHING, db_column='saaid')

    class Meta:
        managed = False
        db_table = 'laj_saa'
        unique_together = (('species_id', 'regulation_id'),)


class Observation(models.Model):
    id = models.IntegerField(primary_key=True)
    location = models.ForeignKey(Object, models.DO_NOTHING, db_column='kohdeid')
    species = models.ForeignKey('Species', models.DO_NOTHING, db_column='lajid')
    series = models.ForeignKey(ObservationSeries, models.DO_NOTHING, db_column='hsaid', blank=True, null=True)
    abundance = models.ForeignKey('Abundance', models.DO_NOTHING, db_column='runsausid', blank=True, null=True)
    incidence = models.ForeignKey('Incidence', models.DO_NOTHING, db_column='yleisyysid', blank=True, null=True)
    observer = models.ForeignKey(Person, models.DO_NOTHING, db_column='hloid', blank=True, null=True)
    number = models.CharField(max_length=30, blank=True, null=True, db_column='lkm')
    mobility = models.ForeignKey('Mobility', models.DO_NOTHING, db_column='liikkumislkid', blank=True, null=True)
    origin = models.ForeignKey(Origin, models.DO_NOTHING, db_column='alkuperaid', blank=True, null=True)
    breeding_category = models.ForeignKey('BreedingCategory', models.DO_NOTHING, db_column='pesimisvarmuusid', blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True, db_column='kuvaus')
    notes = models.CharField(max_length=100, blank=True, null=True, db_column='huom')
    date = models.DateField(blank=True, null=True, db_column='pvm')
    occurrence = models.ForeignKey(Occurrence, models.DO_NOTHING, db_column='esiintymaid', blank=True, null=True)
    protection_level = models.ForeignKey('ProtectionLevel', models.DO_NOTHING, db_column='suojaustasoid')
    created_time = models.DateTimeField(db_column='pvm_luotu')
    last_modified_time = models.DateTimeField(blank=True, null=True, db_column='pvm_editoitu')

    class Meta:
        managed = False
        db_table = 'lajihavainto'


class Species(models.Model):
    id = models.IntegerField(primary_key=True)
    taxon = models.CharField(max_length=5, blank=True, null=True, db_column='ryhma')
    taxon_1 = models.CharField(max_length=50, blank=True, null=True, db_column='elioryhma1')
    taxon_2 = models.CharField(max_length=50, blank=True, null=True, db_column='elioryhma2')
    order_fi = models.CharField(max_length=150, blank=True, null=True, db_column='lahko_suomi')
    order_la = models.CharField(max_length=150, blank=True, null=True, db_column='lahko_tiet')
    family_fi = models.CharField(max_length=150, blank=True, null=True, db_column='heimo_suomi')
    family_la = models.CharField(max_length=150, blank=True, null=True, db_column='heimo_tiet')
    name_fi_1 = models.CharField(max_length=150, blank=True, null=True, db_column='nimi_suomi1')
    name_fi_2 = models.CharField(max_length=150, blank=True, null=True, db_column='nimi_suomi2')
    name_la_1 = models.CharField(max_length=150, blank=True, null=True, db_column='nimi_tiet1')
    name_la_2 = models.CharField(max_length=150, blank=True, null=True, db_column='nimi_tiet2')
    subspecies_1 = models.CharField(max_length=150, blank=True, null=True, db_column='alalaji1')
    subspecies_2 = models.CharField(max_length=150, blank=True, null=True, db_column='alalaji2')
    author_1 = models.CharField(max_length=150, blank=True, null=True, db_column='auktori1')
    author_2 = models.CharField(max_length=150, blank=True, null=True, db_column='auktori2')
    name_abbreviated_1 = models.CharField(max_length=10, blank=True, null=True, db_column='nimilyhenne1')
    name_abbreviated_2 = models.CharField(max_length=10, blank=True, null=True, db_column='nimilyhenne2')
    name_sv = models.CharField(max_length=150, blank=True, null=True, db_column='nimi_ruotsi')
    name_en = models.CharField(max_length=150, blank=True, null=True, db_column='nimi_englanti')
    registry_date = models.DateTimeField(blank=True, null=True, db_column='rekisteripvm')
    protection_level = models.ForeignKey('ProtectionLevel', models.DO_NOTHING, db_column='suojaustasoid')
    additional_info = models.CharField(max_length=255, blank=True, null=True, db_column='lisatieto')
    code = models.CharField(max_length=20, blank=True, null=True, db_column='koodi')
    link = models.CharField(max_length=4000, blank=True, null=True, db_column='linkki')
    regulations = models.ManyToManyField('Regulation', through=SpeciesRegulation, related_name='species')

    class Meta:
        managed = False
        db_table = 'lajirekisteri'


class Mobility(models.Model):
    id = models.IntegerField(primary_key=True)
    value = models.IntegerField(blank=True, null=True, db_column='arvo')
    explanation = models.CharField(max_length=50, blank=True, null=True, db_column='selitys')
    source = models.CharField(max_length=50, blank=True, null=True, db_column='lahde')

    class Meta:
        managed = False
        db_table = 'liikkumislk'


class LinkType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50, blank=True, null=True, db_column='nimi')

    class Meta:
        managed = False
        db_table = 'linkkityyppi'


class HabitatTypeRegulation(models.Model):
    habitat_type_id = models.ForeignKey('HabitatType', models.DO_NOTHING, db_column='ltyyppiid')
    regulation_id = models.ForeignKey('Regulation', models.DO_NOTHING, db_column='saadosid')

    class Meta:
        managed = False
        db_table = 'ltyyppi_saados'
        unique_together = (('habitat_type_id', 'regulation_id'),)


class HabitatTypeObservation(models.Model):
    id = models.IntegerField(primary_key=True)
    object = models.ForeignKey(Object, models.DO_NOTHING, db_column='kohdeid')
    habitat_type = models.ForeignKey('HabitatType', models.DO_NOTHING, db_column='ltyypid')
    group_fraction = models.IntegerField(blank=True, null=True, db_column='osuus_kuviosta')
    additional_info = models.CharField(max_length=255, blank=True, null=True, db_column='lisatieto')
    observation_series = models.ForeignKey(ObservationSeries, models.DO_NOTHING, db_column='hsaid')
    created_time = models.DateTimeField(db_column='pvm_luotu')
    last_modified_time = models.DateTimeField(blank=True, null=True, db_column='pvm_editoitu')

    class Meta:
        managed = False
        db_table = 'ltyyppihavainto'


class HabitatType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50, blank=True, null=True, db_column='nimi')
    code = models.CharField(max_length=10, blank=True, null=True, db_column='koodi')
    description = models.CharField(max_length=255, blank=True, null=True, db_column='kuvaus')
    additional_info = models.CharField(max_length=255, blank=True, null=True, db_column='lisatieto')
    group = models.CharField(max_length=50, blank=True, null=True, db_column='ltyyppiryhma')
    regulations = models.ManyToManyField(Regulation, through=HabitatTypeRegulation, related_name='habitat_types')

    class Meta:
        managed = False
        db_table = 'ltyyppirekisteri'


class Class(models.Model):
    id = models.CharField(primary_key=True, max_length=10, db_column='tunnus')
    name = models.CharField(max_length=50, blank=True, null=True, db_column='nimi')
    additional_info = models.CharField(max_length=255, blank=True, null=True, db_column='lisatieto')
    super_class = models.ForeignKey('Class', blank=True, null=True, db_column='paatunnus')
    reporting = models.BooleanField(db_column='raportointi')
    www = models.BooleanField()
    metadata = models.CharField(max_length=4000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'luokka'


class BreedingCategory(models.Model):
    id = models.IntegerField(primary_key=True)
    value = models.CharField(max_length=50, blank=True, null=True, db_column='arvo')
    explanation = models.CharField(max_length=50, blank=True, null=True, db_column='selitys')
    source = models.CharField(max_length=50, blank=True, null=True, db_column='lahde')

    class Meta:
        managed = False
        db_table = 'pesimisvarmuus'


class Abundance(models.Model):
    id = models.IntegerField(primary_key=True)
    value = models.CharField(max_length=5, blank=True, null=True, db_column='arvo')
    explanation = models.CharField(max_length=30, blank=True, null=True, db_column='selitys')
    source = models.CharField(max_length=50, blank=True, null=True, db_column='lahde')

    class Meta:
        managed = False
        db_table = 'runsaus'


class Tile(models.Model):
    id = models.ForeignKey(Object, models.DO_NOTHING, db_column='id', primary_key=True)
    number = models.CharField(max_length=10, blank=True, null=True, db_column='nro')
    degree_of_determination = models.IntegerField(blank=True, null=True, db_column='selvitysaste')
    additional_info = models.CharField(max_length=255, blank=True, null=True, db_column='lisatieto')

    class Meta:
        managed = False
        db_table = 'ruutu'


class Regulation(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True, db_column='nimi')
    paragraph = models.CharField(max_length=100, blank=True, null=True, db_column='pykala')
    additional_info = models.CharField(max_length=255, blank=True, null=True, db_column='lisatieto')
    value = models.CharField(max_length=10, blank=True, null=True, db_column='arvo')
    value_explanation = models.CharField(max_length=255, blank=True, null=True, db_column='arvon_selitys')
    valid = models.BooleanField(db_column='voimassa')
    date_of_entry = models.DateTimeField(blank=True, null=True, db_column='voimaantulo')
    link = models.CharField(max_length=4000, blank=True, null=True, db_column='linkki')

    class Meta:
        managed = False
        db_table = 'saados'


class ConservationProgramme(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50, blank=True, null=True, db_column='nimi')

    class Meta:
        managed = False
        db_table = 'sohjelma'


class ProtectionCriterion(models.Model):
    criterion_id = models.ForeignKey('Criterion', models.DO_NOTHING, db_column='perusteid')
    protection_id = models.ForeignKey('Protection', models.DO_NOTHING, db_column='suoid')

    class Meta:
        managed = False
        db_table = 'suo_peruste'
        unique_together = (('criterion_id', 'protection_id'),)


class ProtectionLevel(models.Model):
    id = models.IntegerField(primary_key=True)
    explanation = models.CharField(max_length=50, blank=True, null=True, db_column='selitys')

    class Meta:
        managed = False
        db_table = 'suojaustaso'


class Protection(models.Model):
    id = models.ForeignKey(Object, models.DO_NOTHING, db_column='id', primary_key=True)
    reported_area = models.CharField(max_length=50, blank=True, null=True, db_column='ilmoitettu_pinta_ala')
    land_area = models.CharField(max_length=50, blank=True, null=True, db_column='maapinta_ala')
    water_area = models.CharField(max_length=50, blank=True, null=True, db_column='vesipinta_ala')
    hiking = models.CharField(max_length=255, blank=True, null=True, db_column='liikkuminen')
    regulations = models.CharField(max_length=255, blank=True, null=True, db_column='maaraykset')
    additional_info = models.CharField(max_length=255, blank=True, null=True, db_column='lisatieto')
    criteria = models.ManyToManyField('Criterion', through=ProtectionCriterion, related_name='protections')
    conservation_programmes = models.ManyToManyField(ConservationProgramme,
                                                     through='ProtectionConservationProgramme',
                                                     related_name='protections')

    class Meta:
        managed = False
        db_table = 'suojelu'


class ProtectionConservationProgramme(models.Model):
    protection_id = models.ForeignKey(Protection, models.DO_NOTHING, db_column='suojeluid')
    conservation_programme_id = models.ForeignKey(ConservationProgramme, models.DO_NOTHING, db_column='sohjelmaid')

    class Meta:
        managed = False
        db_table = 'suojelu_sohjelma'
        unique_together = (('protection_id', 'conservation_programme_id'),)


class Criterion(models.Model):
    id = models.IntegerField(primary_key=True)
    criterion = models.CharField(max_length=50, blank=True, null=True, db_column='peruste')
    specific_criterion = models.CharField(max_length=50, blank=True, null=True, db_column='tarkperuste')
    subcriterion = models.CharField(max_length=50, blank=True, null=True, db_column='alaperuste')

    class Meta:
        managed = False
        db_table = 'suoperuste'


class EventRegulation(models.Model):
    event_id = models.ForeignKey('Event', models.DO_NOTHING, db_column='tapid')
    regulation_id = models.ForeignKey(Regulation, models.DO_NOTHING, db_column='saaid')

    class Meta:
        managed = False
        db_table = 'tap_saados'
        unique_together = (('event_id', 'regulation_id'),)


class Event(models.Model):
    id = models.IntegerField(primary_key=True)
    register_id = models.CharField(max_length=20, blank=True, null=True, db_column='diaarinro')
    description = models.CharField(max_length=255, blank=True, null=True, db_column='kuvaus')
    type = models.ForeignKey('EventType', models.DO_NOTHING, db_column='tapahtumatyyppiid')
    last_modified_by = models.CharField(max_length=20, blank=True, null=True, db_column='paivittaja')
    date = models.DateField(blank=True, null=True, db_column='pvm')
    person = models.ForeignKey(Person, models.DO_NOTHING, db_column='hloid', blank=True, null=True, db_column='')
    link = models.CharField(max_length=4000, blank=True, null=True, db_column='linkki')
    protection_level = models.ForeignKey(ProtectionLevel, models.DO_NOTHING, db_column='suojaustasoid')
    objects = models.ManyToManyField(Object, through='EventObject', related_name='events')
    regulations = models.ManyToManyField(Regulation, throuhg='EventRegulation', related_name='events')

    class Meta:
        managed = False
        db_table = 'tapahtuma'


class EventObject(models.Model):
    object_id = models.ForeignKey(Object, models.DO_NOTHING, db_column='kohdeid')
    event_id = models.ForeignKey(Event, models.DO_NOTHING, db_column='tapid')

    class Meta:
        managed = False
        db_table = 'tapahtuma_kohde'
        unique_together = (('object_id', 'event_id'),)


class EventType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50, blank=True, null=True, db_column='nimi')

    class Meta:
        managed = False
        db_table = 'tapahtumatyyppi'


class Incidence(models.Model):
    id = models.IntegerField(primary_key=True)
    value = models.CharField(max_length=5, blank=True, null=True, db_column='arvo')
    explanation = models.CharField(max_length=30, blank=True, null=True, db_column='selitys')
    source = models.CharField(max_length=50, blank=True, null=True, db_column='lahde')

    class Meta:
        managed = False
        db_table = 'yleisyys'