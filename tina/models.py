import os
import couchdb
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth.models import AbstractUser

from util import TinaCouchDB
from tina.mixins import TopLevelEntityMixin, InteriorEntityMixin


class UserProfile(models.Model):
    defaults_doc_id = models.CharField('Defaults Doc ID', max_length=128, editable=False)


class Project(TopLevelEntityMixin, models.Model):
    """
    Represents a project, such as PsychENCODE or Chicago Pancreatic Cancer Initiative

    Projects can have subprojects below them, which have all properties of top level projects. Subprojects
    are only for organizational purposes. If a project is a top level project, that is, it has no parent
    project, its parent_project field will be None.

    Projects contain a document key that maps to a document in the NoSQL database. In that document are any
    bits of metadata that the creator of the project may wish to document that aren't available as part of
    the structured model.
        TODO Maybe this doesn't need to be a full NoSQL database? I could probably get away with a JSON file
        if I'm careful

    TODO Projects also store default values for various Library parameters
    """
    _child_model_class = 'Biospecimen'
    _initial_entity = True

    name = models.CharField('Project Name', max_length=1024, unique=True)
    description = models.TextField('Project Description', blank=True)
    pi = models.ForeignKey('PrincipalInvestigator', null=True, blank=True)

    public = models.BooleanField('Is Public Project', default=False)
    cloud = models.ForeignKey('Cloud', null=True, blank=True)
    organism = models.ForeignKey('Organism', null=True, blank=True)
    platform = models.ForeignKey('Platform', null=True, blank=True)

    parent_project = models.ForeignKey('Project', null=True, blank=True)

    details_doc_id = models.CharField('Details Doc Key', max_length=128, editable=False)

    project_cover_image = models.ImageField(upload_to='project_covers', blank=True, null=True)

    @staticmethod
    def all_toplevel_projects():
        """
        Return all top level Projects
        """
        return Project.objects.filter(parent_project=None)

    def is_subproject(self):
        """
        Return whether this Project is a subproject
        """
        return self.parent_project is not None

    def subprojects(self):
        """
        Get all of this Projects subprojects
        """
        return Project.objects.filter(parent_project=self.pk)

    def libraries(self, include_subprojects=False):
        """
        Returns all libraries associated with this Project
        """
        pass

    def __unicode__(self):
        if not self.is_subproject():
            return self.name
        return '::'.join((str(self.parent_project), self.name))

    def __str__(self):
        return self.__unicode__()


@receiver(models.signals.post_delete, sender=Project)
def project_cleanup(sender, **kwargs):
    """
    Adapted from http://stackoverflow.com/a/16041527/1539628
    
    Cleans up after a Project delete by deleting the thumbnail image off 
    the server and removing any couchdb documents that were created
    """
    project = kwargs['instance']

    # Remove thumbnail cover image
    cover_image = project.project_cover_image
    if cover_image and os.path.isfile(cover_image.path):
        os.remove(cover_image.path)

    # Remove couchdb metadata document
    try:
        TinaCouchDB.delete_tina_doc(project.details_doc_id)
    except couchdb.ResourceConflict:
        pass


class LibraryDocumentDefaultKey(models.Model):
    project = models.ForeignKey('Project')
    key = models.CharField(max_length=1024)


class Biospecimen(InteriorEntityMixin, models.Model):
    """
    Represents an individual biological organism from which a sample was derived, such as a patient.
    """
    _parent_model_class = 'Project'
    _child_model_class = 'Sample'

    name = models.CharField('Biospecimen Name', max_length=1024)
    parent_model = models.ForeignKey('Project', verbose_name='Project', related_name='children')


class Sample(InteriorEntityMixin, models.Model):
    """
    Represents a biological sample which was taken from a biospecimen.
    """
    _parent_model_class = 'Biospecimen'
    _child_model_class = 'Library'

    name = models.CharField('Sample Name', max_length=1024)
    parent_model = models.ForeignKey('Biospecimen', verbose_name='Biospecimen', related_name='children')


class ProjectPerLibraryDetail(models.Model):
    key = models.CharField('Detail Key', max_length=1024)
    project = models.ForeignKey('Project')


class Library(InteriorEntityMixin, models.Model):
    """
    Represents a library of reads which were generated from a sample.

    Libraries are the model of primary interest when looking at a Project, but the relationship must
    go through a Sample which must go through a Biospecimen.
    """
    _parent_model_class = 'Sample'
    _terminal_entity = True

    class Meta:
        verbose_name_plural = 'Libraries'

    class State:
        """
        Represents the current state of a library, mostly related to its sequencing and data
        availability. New states should be added to the ALL variable as a space separated
        string.
        """
        ALL = 'submitted sequencing available'.split()
        STATE_CHOICES = [(choice, choice.capitalize()) for choice in ALL]

    name = models.CharField('Library BID', max_length=1024, unique=True)
    assay = models.CharField('Library Assay', max_length=1024)  # TODO How to set default to library default?
    barcode = models.ForeignKey('LibraryBarcode')
    sequencing_protocol = models.CharField('Library Sequencing Protocol', max_length=2, choices=(
        ('SE', 'Single-end'),
        ('PE', 'Paired-end')
    ))
    read_length = models.CharField('Library Read Length', max_length=1024)
    platform = models.ForeignKey('Platform')  # TODO How to set default to library default?
    """
    TODO For the above todo, I'll allow it to be blank and null, then if it comes across
    as None I can actually use the library default when it becomes important. But then how to I set
    the actual form field default showing to the library default. Hmm.
    """



    # Programmatic entry fields
    # bionimbus_id = models.CharField('Library BID', max_length=16)
    state = models.CharField('Library State', max_length=128, default='submitted', choices=State.STATE_CHOICES)

    details_doc_id = models.CharField('Detail Doc Key', max_length=128, editable=False)  # TODO Should this be JSON?

    parent_model = models.ForeignKey('Sample', verbose_name='Sample', blank=True, null=True, related_name='children')


class LibraryData(models.Model):
    """
    Represents an individual data file of a Library, most commonly in fastq format
    """
    class Meta:
        verbose_name_plural = 'Library Data'

    class Phred:
        SANGER_33 = 0
        SOLEXA_64 = 1
        ILLUMINA_1POINT3_64 = 2
        ILLUMINA_1POINT5_64 = 3
        ILLUMINA_1POINT8_33 = 4
        OTHER = 5

        PHRED_CHOICES = (
            (SANGER_33, 'Sanger +33'),
            (SOLEXA_64, 'Solexa +64'),
            (ILLUMINA_1POINT3_64, 'Illumina 1.3 +64'),
            (ILLUMINA_1POINT5_64, 'Illumina 1.5 +64'),
            (ILLUMINA_1POINT8_33, 'Illumina 1.8 +33'),
            (OTHER, 'Other')
        )

    class DataFormat:
        FASTQ = 0
        FASTA = 1
        SAM = 2
        BAM = 3
        GFF_GTF = 4
        BED = 5
        VCF = 6
        OTHER = 7

        FORMAT_CHOICES = (
            (FASTQ, 'Fastq'),
            (FASTA, 'Fasta'),
            (SAM, 'SAM'),
            (BAM, 'BAM'),
            (GFF_GTF, 'GFF/GTF'),
            (BED, 'BED'),
            (VCF, 'VCF'),
            (OTHER, 'Other'),
        )

    library = models.ForeignKey('Library')
    path = models.FilePathField('Library Data Path', path=settings.LIBRARY_DATA_ROOT, recursive=True, max_length=512)
    format = models.IntegerField('Library Data Format', choices=DataFormat.FORMAT_CHOICES,
                                 default=DataFormat.FASTQ, blank=True, null=True)
    paired_end_mate = models.OneToOneField('LibraryData', on_delete=models.SET_NULL, blank=True, null=True)
    number_of_reads = models.BigIntegerField('Library Data Number of Reads', blank=True, null=True)
    phred_scale = models.IntegerField('Library Data Phred Quality Scale', choices=Phred.PHRED_CHOICES,
                                      default=Phred.ILLUMINA_1POINT8_33, blank=True, null=True)
    read_length = models.IntegerField('Library Data Read Length', blank=True, null=True)

    def save(self, *args, **kwargs):
        """
        Override of the save() method to allow a symmetric OneToOneField for paired
        end mates. When one LibraryData sets another as its paired end mate, the other
        LibraryData's paired end mate is also set in a symmetric fashion.
        """
        super(LibraryData, self).save()

        if self.paired_end_mate and self.paired_end_mate.paired_end_mate is not self:
            self.paired_end_mate.paired_end_mate = self
            self.paired_end_mate.save()

    def __unicode__(self):
        return '__'.join((self.library.name, self.path.replace(settings.LIBRARY_DATA_ROOT + '/', '')))

    def __str__(self):
        return self.__unicode__()


class Organism(models.Model):
    pass


class Platform(models.Model):
    pass


class PrincipalInvestigator(models.Model):
    first_name = models.CharField('PI First Name', max_length=256)
    last_name = models.CharField('PI Last Name', max_length=512)
    email = models.EmailField('PI Email')
    user = models.ForeignKey(User, null=True, blank=True)

    def __unicode__(self):
        return ' '.join((self.first_name, self.last_name))


class Cloud(models.Model):
    pass


class LibraryType(models.Model):
    pass


class Stage(models.Model):
    pass


class LibraryBarcode(models.Model):
    pass


class SequencingFacility(models.Model):
    """
    This model will, I think, be the most important for library submission.
    """
    class Meta:
        verbose_name = 'Sequencing Facility'
        verbose_name_plural = 'Sequencing Facilities'

    name = models.CharField('Sequencing Facility Name', max_length=1024,
                            help_text='Name of the sequencing facility.')
    description = models.TextField('Sequencing Facility Description',
                                   help_text='Longer description of the sequecing facility.')
    # TODO Description might be superfluous
    import_name = models.CharField('Sequencing Core Import Name', max_length=256,
                                   help_text='Filename of the core blueprint Python file to import.')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__()


class Downloader(models.Model):
    name = models.CharField('Downloader Readable Name', max_length=256)
    full_classpath = models.CharField('Downloader Full Classpath', max_length=256)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__()


class BidKeyGenerator(models.Model):
    year = models.IntegerField('Year', unique=True, default=int(datetime.now().strftime('%Y')))
    increment = models.IntegerField('Increment', default=0)

    class Meta:
        verbose_name = verbose_name_plural = 'BID Key Generator'

    def get_new_bid(self):
        current_year = int(datetime.now().strftime('%Y'))
        if current_year != self.year:
            self.year = current_year
            self.increment = 0

        self.increment += 1
        self.save()
        return '{year}-{increment}'.format(year=self.year, increment=self.increment)
