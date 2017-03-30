"""
This module exists for a programmer to code up specific instructions for how to handle submissions to a specific
sequencing facility. The options and the way each facility works was too different to generalize.

The module handles somethings, like presenting a common interface by which Django gets forms for specific
facilities, gets the user input data, then runs a function using that input data.

New sequencing facilities are created by:
    - Create a new model (tina.models.SequencingFacility) for the facility. The model only serves to identify
      facilities for initial selection, and the only field of consequence is import_name, which must
      correspond exactly with the name of the Python file in this module for the respective facility
      ex. The file for the Faber Core is faber.py, and there's a model with name='Faber Core' and
          import_name='faber'
    - Create a Python file that will give specific instructions on how to submit to this facility. This file
      must have the following functions:
          - def render_form(request)
              - returns the html for the form that will be injected via an AJAX call into the submit page. The
                request object is provided so django.shortcuts.render can be used with a template. This is made
                much easier with the aid of the Django Form API, but it's not required.
          - def process_submission(post_data)
              - receives request.POST in its argument post_data. This function should do whatever is necessary
                for submission to the facility, such as filling in PDF forms or sending emails. It should also
                instantiate models appropriately for Library, Sample, etc. Returns True if everything was successful,
                False otherwise.
"""
import importlib

from django.http import HttpResponse


def get_facility_module(facility):
    return importlib.import_module('.' + facility, package=__name__)


def get_submit_form(request, facility):
    try:
        return get_facility_module(facility).render_form(request)
    except ImportError:
        return HttpResponse('<div>Facility {} not found</div>'.format(facility))


def handle_submission(facility, post_data):
    try:
        get_facility_module(facility).process_submission(post_data)
    except ImportError:
        return False
    return True



# class SeqFacilityBase(object):
#     """
#     Base class for a SequencingFacility blueprint
#     """
#     def render_form(self, request):
#         """
#         Send everything necessary for django to render forms specific
#         to this facility
#         TODO Should this send back Django objects in some form, or full HTML?
#         """
#         pass
#
#     def process_submission(self, post_data):
#         """
#         Process input received from a submission to this core
#         :return:
#         """
#         pass
