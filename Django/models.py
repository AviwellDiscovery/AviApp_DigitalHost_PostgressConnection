# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Abundancefacttable(models.Model):
    sample_idsample = models.ForeignKey('Sample', models.DO_NOTHING, db_column='Sample_idSample')  # Field name made lowercase.
    item_iditem = models.ForeignKey('Item', models.DO_NOTHING, db_column='Item_idItem')  # Field name made lowercase.
    omics_idomics = models.ForeignKey('Omics', models.DO_NOTHING, db_column='Omics_idOMICS')  # Field name made lowercase.
    abundance = models.CharField(db_column='Abundance', max_length=45, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'AbundanceFactTable'


class Analysis(models.Model):
    idanalysis = models.AutoField(db_column='IdAnalysis', primary_key=True)  # Field name made lowercase.
    analysisname = models.CharField(db_column='AnalysisName', max_length=45, blank=True, null=True)  # Field name made lowercase.
    set_idset = models.ForeignKey('Set', models.DO_NOTHING, db_column='Set_IdSet', blank=True, null=True)  # Field name made lowercase.
    parameter = models.CharField(db_column='Parameter', max_length=2000, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Analysis'


class AvappAppuser(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(db_column='Name', max_length=64)  # Field name made lowercase.
    surname = models.CharField(db_column='Surname', max_length=64)  # Field name made lowercase.
    creationdate = models.DateTimeField(db_column='CreationDate')  # Field name made lowercase.
    type_user = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'Avapp_appuser'


class Feature(models.Model):
    idfeature = models.AutoField(db_column='IdFeature', primary_key=True)  # Field name made lowercase.
    featurename = models.CharField(db_column='FeatureName', max_length=45, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Feature'


class Featurefacttable(models.Model):
    host_idhost = models.OneToOneField('Host', models.DO_NOTHING, db_column='Host_idHost', primary_key=True)  # Field name made lowercase.
    feature_idfeature = models.ForeignKey(Feature, models.DO_NOTHING, db_column='Feature_idFeature')  # Field name made lowercase.
    value = models.CharField(db_column='Value', max_length=45, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'FeatureFactTable'
        unique_together = (('host_idhost', 'feature_idfeature'),)


class Gene(models.Model):
    idgene = models.AutoField(db_column='IdGene', primary_key=True)  # Field name made lowercase.
    genename = models.CharField(db_column='GeneName', max_length=45, blank=True, null=True)  # Field name made lowercase.
    length = models.IntegerField(db_column='Length', blank=True, null=True)  # Field name made lowercase.
    genome_idgenome = models.ForeignKey('Genome', models.DO_NOTHING, db_column='Genome_idGenome')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Gene'


class Genome(models.Model):
    idgenome = models.AutoField(db_column='IdGenome', primary_key=True)  # Field name made lowercase.
    genomecategory = models.CharField(db_column='GenomeCategory', max_length=45, blank=True, null=True)  # Field name made lowercase.
    domain = models.CharField(db_column='Domain', max_length=45, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Genome'


class Host(models.Model):
    idhost = models.AutoField(db_column='IdHost', primary_key=True)  # Field name made lowercase.
    tag = models.IntegerField(db_column='Tag', blank=True, null=True)  # Field name made lowercase.
    sex = models.CharField(db_column='Sex', max_length=45, blank=True, null=True)  # Field name made lowercase.
    growthroom = models.CharField(db_column='GrowthRoom', max_length=45, blank=True, null=True)  # Field name made lowercase.
    study_idstudy = models.ForeignKey('Study', models.DO_NOTHING, db_column='Study_idStudy')  # Field name made lowercase.
    weight = models.TextField(db_column='Weight', blank=True, null=True)  # Field name made lowercase. This field type is a guess.

    class Meta:
        managed = False
        db_table = 'Host'


class HostHasPen(models.Model):
    pen_idpen = models.ForeignKey('Pen', models.DO_NOTHING, db_column='Pen_IdPen')  # Field name made lowercase.
    host_idhost = models.ForeignKey(Host, models.DO_NOTHING, db_column='Host_IdHost')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Host_has_Pen'


class Item(models.Model):
    iditem = models.AutoField(db_column='IdItem', primary_key=True)  # Field name made lowercase.
    itemname = models.CharField(db_column='ItemName', max_length=45)  # Field name made lowercase.
    analysis_idanalysis = models.ForeignKey(Analysis, models.DO_NOTHING, db_column='Analysis_IdAnalysis')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Item'
        unique_together = (('itemname', 'analysis_idanalysis'),)


class Omics(models.Model):
    idomics = models.AutoField(db_column='IdOmics', primary_key=True)  # Field name made lowercase.
    path = models.CharField(db_column='Path', max_length=250, blank=True, null=True)  # Field name made lowercase.
    technology = models.CharField(db_column='Technology', max_length=45, blank=True, null=True)  # Field name made lowercase.
    platform = models.CharField(db_column='Platform', max_length=45, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Omics'


class OmicsHasQuality(models.Model):
    omics_idomics = models.OneToOneField(Omics, models.DO_NOTHING, db_column='Omics_idOmics', primary_key=True)  # Field name made lowercase.
    quality_idquality = models.ForeignKey('Quality', models.DO_NOTHING, db_column='Quality_idQuality')  # Field name made lowercase.
    values = models.CharField(db_column='Values', max_length=45, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Omics_has_Quality'
        unique_together = (('omics_idomics', 'quality_idquality'),)


class Pen(models.Model):
    idpen = models.AutoField(db_column='IdPen', primary_key=True)  # Field name made lowercase.
    trt = models.IntegerField(db_column='Trt', blank=True, null=True)  # Field name made lowercase.
    donorhen = models.CharField(db_column='DonorHen', max_length=45, blank=True, null=True)  # Field name made lowercase.
    dietstarter = models.CharField(db_column='DietStarter', max_length=45, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Pen'


class PenHasFeature(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)  # Field name made lowercase.
    feature_idfeature = models.ForeignKey(Feature, models.DO_NOTHING, db_column='Feature_IdFeature')  # Field name made lowercase.
    pen_idpen = models.ForeignKey(Pen, models.DO_NOTHING, db_column='Pen_IdPen')  # Field name made lowercase.
    value = models.CharField(db_column='Value', max_length=45, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Pen_has_Feature'


class Quality(models.Model):
    idquality = models.AutoField(db_column='IdQuality', primary_key=True)  # Field name made lowercase.
    qualityname = models.CharField(db_column='QualityName', max_length=45, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Quality'


class Sample(models.Model):
    idsample = models.AutoField(db_column='IdSample', primary_key=True)  # Field name made lowercase.
    collectiondate = models.DateField(db_column='CollectionDate', blank=True, null=True)  # Field name made lowercase.
    samplename = models.CharField(db_column='SampleName', max_length=45, blank=True, null=True)  # Field name made lowercase.
    host_idhost = models.ForeignKey(Host, models.DO_NOTHING, db_column='Host_idHost')  # Field name made lowercase.
    sampletype = models.CharField(db_column='SampleType', max_length=45, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Sample'


class Set(models.Model):
    idset = models.AutoField(db_column='IdSet', primary_key=True)  # Field name made lowercase.
    settype = models.CharField(db_column='SetType', max_length=45, blank=True, null=True)  # Field name made lowercase.
    setname = models.CharField(db_column='SetName', max_length=45, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Set'


class SetHasGene(models.Model):
    gene_idgene = models.OneToOneField(Gene, models.DO_NOTHING, db_column='Gene_IdGene', primary_key=True)  # Field name made lowercase.
    set_idset = models.ForeignKey(Set, models.DO_NOTHING, db_column='Set_IdSet')  # Field name made lowercase.
    info = models.CharField(db_column='Info', max_length=2000, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Set_has_Gene'
        unique_together = (('gene_idgene', 'set_idset'),)


class SetHasGenome(models.Model):
    set_idset = models.ForeignKey(Set, models.DO_NOTHING, db_column='Set_IdSet', blank=True, null=True)  # Field name made lowercase.
    genome_idgenome = models.ForeignKey(Genome, models.DO_NOTHING, db_column='Genome_IdGenome', blank=True, null=True)  # Field name made lowercase.
    infos = models.CharField(db_column='Infos', max_length=2000, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Set_has_Genome'


class Study(models.Model):
    idstudy = models.AutoField(db_column='idStudy', primary_key=True)  # Field name made lowercase.
    studyname = models.CharField(db_column='StudyName', unique=True, max_length=45, blank=True, null=True)  # Field name made lowercase.
    studydate = models.DateField(db_column='StudyDate', blank=True, null=True)  # Field name made lowercase.
    summary = models.TextField(db_column='Summary', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Study'


class Taxons(models.Model):
    idtaxons = models.AutoField(db_column='IdTaxons', primary_key=True)  # Field name made lowercase.
    item_iditem = models.ForeignKey(Item, models.DO_NOTHING, db_column='Item_idItem')  # Field name made lowercase.
    taxonomy = models.CharField(db_column='Taxonomy', max_length=2000, blank=True, null=True)  # Field name made lowercase.
    size = models.IntegerField(db_column='Size', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Taxons'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'