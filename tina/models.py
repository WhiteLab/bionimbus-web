from datetime import datetime

from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):
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
        if self.parent_project is not None:
            return True
        return False

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
        return self.name


class LibraryDocumentDefaultKey(models.Model):
    project = models.ForeignKey('Project')
    key = models.CharField(max_length=1024)








class Biospecimen(models.Model):
    """
    Represents an individual biological organism from which a sample was derived, such as a patient.
    """
    name = models.CharField('Biospecimen Name', max_length=1024)
    project = models.ForeignKey('Project')


class Sample(models.Model):
    """
    Represents a biological sample which was taken from a biospecimen.
    """
    name = models.CharField('Sample Name', max_length=1024)
    biospecimen = models.ForeignKey('Biospecimen')

    def project(self):
        return self.biospecimen.project


class ProjectPerLibraryDetail(models.Model):
    key = models.CharField('Detail Key', max_length=1024)
    project = models.ForeignKey('Project')


class Library(models.Model):
    """
    Represents a library of reads which were generated from a sample.

    Libraries are the model of primary interest when looking at a Project, but the relationship must
    go through a Sample which must go through a Biospecimen.
    """
    class State:
        """
        Represents the current state of a library, mostly related to its sequencing and data
        availability. New states should be added to the ALL variable as a space separated
        string.
        """
        ALL = 'submitted sequencing available'.split()

        @classmethod
        def choices(cls):
            return [(choice, choice.capitalize()) for choice in cls.ALL]

    name = models.CharField('Library Name', max_length=1024)
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
    bionimbus_id = models.CharField('Library BID', max_length=16)
    state = models.CharField('Library State', max_length=128, default='submitted', choices=State.choices())

    details_doc_id = models.CharField('Detail Doc Key', max_length=128, editable=False)  # TODO Should this be JSON?

    sample = models.ForeignKey('Sample', blank=True, null=True)

    def project(self):
        return self.sample.biospecimen.project



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
