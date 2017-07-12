class ProjectDescendantMixin(object):
    """
    Mixin for a Django model that's meant to be a conceptual descendant of
    the Tina Project model. Provides functions common to all descendants. Assumes
    the descendant model defines at least two fields, name and parent_model:

        - name: CharField identifying the entity
        - parent_model: ForeignKey pointing to whatever model is the conceptual
                        parent to this model, thus defining the hierarchy
    """
    name = None
    parent_model = None

    def project(self, root=False):
        return self.parent_model.project(root)

    def lineage(self, strings=False, return_tuple=True):
        lineage_as_list = self.parent_model.lineage(strings=strings, return_tuple=False) + [self.name if strings else self]
        return tuple(lineage_as_list) if return_tuple else lineage_as_list

    def __unicode__(self):
        return '__'.join((str(self.parent_model), self.name))

    def __str__(self):
        return self.__unicode__()
