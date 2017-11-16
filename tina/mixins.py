import tina.models


class _HierachyEntity(object):
    _parent_model_class = None
    _child_model_class = None
    _initial_entity = False
    _terminal_entity = False

    @classmethod
    def parent_class(cls):
        if isinstance(cls._parent_model_class, str):
            return getattr(tina.models, cls._parent_model_class)
        return cls._parent_model_class

    @classmethod
    def child_class(cls):
        if isinstance(cls._child_model_class, str):
            return getattr(tina.models, cls._child_model_class)
        return cls._child_model_class

    @classmethod
    def hierarchy_class(cls, relationship):
        if relationship not in ('parent', 'child'):
            raise ValueError('Relationship must be one of \'parent\' or \'child\'')
        directional_class = getattr(cls, '_{}_model_class'.format(relationship))
        if isinstance(directional_class, str):
            return getattr(tina.models, directional_class)
        return directional_class

    @classmethod
    def extended_family(cls):
        return cls.hierarchy_class('parent'), cls.hierarchy_class('child')


class TopLevelEntityMixin(_HierachyEntity):
    def project(self, root=False):
        if not root or not self.is_subproject():
            return self
        return self.parent_project.project(root)

    def lineage(self, strings=False, return_tuple=False, to_root=True, include_self=True):
        """
        Get all of this Project's parent projects
        """
        self_lineage = [self.name if strings else self] if include_self else list()
        if self.is_subproject() and to_root:
            return self.parent_project.lineage(
                strings=strings,
                include_self=include_self,
                return_tuple=False
            ) + self_lineage
        return tuple(self_lineage) if return_tuple else self_lineage


class InteriorEntityMixin(_HierachyEntity):
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

    def lineage(self, strings=False, return_tuple=True, to_root=True):
        lineage_as_list = self.parent_model.lineage(
            strings=strings,
            return_tuple=False,
            to_root=to_root
        ) + [self.name if strings else self]
        return tuple(lineage_as_list) if return_tuple else lineage_as_list

    def __unicode__(self):
        return '__'.join((str(self.parent_model), self.name))

    def __str__(self):
        return self.__unicode__()
