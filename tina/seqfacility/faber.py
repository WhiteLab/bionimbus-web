import subprocess
import json
from datetime import datetime

from django import forms
from django.shortcuts import render
from django.utils.safestring import mark_safe
from fdfgen import forge_fdf

from tina.models import PrincipalInvestigator


class FacilityForm(forms.Form):
    po_number = forms.CharField(label=mark_safe('PO #<br/><small>(N/A for UChicago)</small>'))
    date = forms.DateField(widget=forms.DateInput(format='%m/%d/%Y'), input_formats=('%m/%d/%Y',))
    pi = forms.ModelChoiceField(queryset=PrincipalInvestigator.objects.all(),
                                label='Prinicpal Investigator')
    pi_email = forms.EmailField(label='PI Email')
    pi_phone = forms.CharField(label='PI Phone')
    department = forms.CharField(label='Department')
    is_cancer_center_member = forms.ChoiceField(label='Cancer Center Member', choices=(
        ('Off', 'No'),
        ('On', 'Yes')
    ), widget=forms.RadioSelect)

    experiment_contact = forms.CharField(label='Experiment Contact')
    experiment_contact_email = forms.EmailField(label='Experiment Contact Email')
    experiment_contact_phone = forms.CharField(label='Experiment Contact Phone')
    billing_administrator = forms.CharField(label='Billing Administrator')
    billing_administrator_email = forms.EmailField(label='Billing Administrator Email')
    billing_administrator_phone = forms.CharField(label='Billing Administrator Phone')

    sample_species = forms.CharField(label='Sample Species')
    sample_labels = forms.CharField(label='Sample Labels')
    number_of_tubes_submitted = forms.CharField(label='Number of Tubes Submitted')
    number_of_samples_per_tube = forms.CharField(label='Number of Samples per Tube')
    number_of_lanes_requested = forms.CharField(label='Number of Lanes Requested')
    library_type = forms.ChoiceField(label='Library Type', choices=(
        ('DNA', 'DNA'),
        ('EXOME', 'EXOME'),
        ('ChIP', 'ChIP'),
        ('RNA', 'RNA'),
        ('Other', 'Other'),
    ), widget=forms.RadioSelect)

    run_type_request = forms.ChoiceField(label='Run Type Request', choices=(
        ('SR 50 bp', 'SR 50 bp'),
        ('SR 100 bp', 'SR 100 bp'),
        ('PE 50 bp', 'PE 50 bp'),
        ('PE 100 bp', 'PE 100 bp'),
        ('Other', 'Other')
    ), widget=forms.RadioSelect)
    # TODO Still need to add "Other" text field, ideally as a hide/show field when Option is selected
    run_type_request_other_text = forms.CharField(label='Other', widget=forms.TextInput(
        attrs={
            'disabled': True
        }
    ))

    preferred_flow_cell = forms.ChoiceField(label='Preferred Flow Cell', choices=(
        ('2lane', '2 Lane'),
        ('8lane', '8 Lane'),
        ('None', 'None')
    ), widget=forms.RadioSelect)

    index_manufacturer = forms.CharField(label='Index Manufacturer')
    index_length = forms.ChoiceField(label='Index Length', choices=(
        ('6bases', '6 bases'),
        ('8bases', '8 bases'),
        ('dual88', 'Dual (8/8)'),
        ('Other', 'Other')
    ), widget=forms.RadioSelect)

    comments = forms.CharField(label='Comments', widget=forms.Textarea)


    @staticmethod
    def web_to_pdf_field_map():
        # PDF form names found by running: pdftk [pdf name] dump_data_fields 35
        return {
            'po_number': 'PO #',
            'date': 'Date mmddyyyy',
            'pi': 'Principal Investigator',
            'pi_email_phone': 'Principal Investigator Email  Phone',
            'department': 'Department',
            'is_cancer_center_member': 'undefined',
            'is_not_cancer_center_member': 'undefined_2',
            'experiment_contact': 'Experiment Contact',
            'experiment_contact_email_phone': 'Experiment Contact Email  Phone',
            'billing_administrator': 'Billing Administrator',
            'billing_administrator_email_phone': 'Billing Administrator Email  Phone',
            'sample_species': 'Sample Species',
            'number_of_tubes_submitted': 'Number of Tubes Submitted',
            'number_of_samples_per_tube': 'Number of Samples per Tube',
            'library_type_DNA': 'DNA',
            'library_type_EXOME': 'EXOME',
            'library_type_ChIP': 'ChIP',
            'library_type_RNA': 'RNA',
            'library_type_Other': 'Other',
            'sample_labels': 'Sample Labels',
            'run_type_request_SE50': 'SE 50 bp',
            'run_type_request_SE100': 'SE 100 bp',
            'run_type_request_PE50': 'PE 50 bp',
            'run_type_request_PE100': 'PE 100 bp',
            'run_type_request_Other': 'Other_2',
            'run_type_request_Other_text': 'Other Run Type',
            'number_of_lanes_requested': 'Number of Lanes Requested',
            'preferred_flow_cell_2lane': '2 lane flow cell Rapid Run',
            'preferred_flow_cell_8lane': '8 lane flow cell High Output',
            'preferred_flow_cell_None': 'None',
            'index_length_6bases': '6 bases',
            'index_length_8bases': '8 bases',
            'index_length_dual': 'Dual 88',
            'index_length_other': 'Other_3',
            'index_manufacturer': 'Index Manufacturer',
            'comments': 'Comments'
        }


def render_form(request):
    faber_submission_form = FacilityForm(initial={
        'date': datetime.now().strftime('%m/%d/%Y')
    })

    context = {
        'form': faber_submission_form
    }

    return render(request, 'tina/submit/facility/faber.html', context)


def process_submission(post_data):
    print 'beginning'
    samples_sheet = json.loads(post_data['samples_sheet'])
    print 'samples_sheet: {}'.format(str(samples_sheet))

    faber_form = FacilityForm(post_data)  # TODO initial=
    if not faber_form.is_valid():
        return False

    # Get cleaned form data, create FDF file to fill out Faber core PDF
    faber_form_data = faber_form.cleaned_data
    faber_form_data['date'] = faber_form_data['date'].strftime('%m/%d/%Y')

    # fdf_fields = [
    #     (pdf_key, faber_form_data.get(web_key, None))
    #     for web_key, pdf_key
    #     in FacilityForm.web_to_pdf_field_map().iteritems()
    # ]
    fdf_fields = [
        ('Sample Labels', 'sample labels test'),
        ('DNA', 'On'),
        ('Other Run Type', 'Running it!'),
        ('RNA', 'On'),
        ('SE 100 bp', ''),
        ('Index Manufacturer', 'Star Warts'),
        ('2 lane flow cell Rapid Run', 'Off'),
        ('SE 50 bp', ''),
        ('undefined_2', 'On'),
        ('None', 'On'),
        ('ChIP', 'Off'),
        ('8 lane flow cell High Output', ''),
        ('Other_2', ''),
        ('Billing Administrator', 'Heather'),
        ('Sample Species', 'Human Pig Hybrid'),
        ('Date mmddyyyy', '02/03/2017'),
        ('Dual 88', 'On'),
        ('Experiment Contact Email  Phone', '911'),
        ('Billing Administrator Email  Phone', 'email@server.com'),
        ('8 bases', ''),
        ('Number of Lanes Requested', '9000'),
        ('EXOME', ''),
        ('undefined', 'On'),
        ('6 bases', ''),
        ('PO #', '82'),
        ('Other', 'On'),
        ('Comments', 'This is the comment box'),
        ('PE 50 bp', 'On'),
        ('Experiment Contact', 'Dominic'),
        ('PE 100 bp', 'Off'),
        ('Number of Tubes Submitted', '71'),
        ('Principal Investigator Email  Phone', 'kpdubbs@uchicago.edu'),
        ('Department', 'Biological Sciences'),
        ('Other_3', 'On'),
        ('Principal Investigator', 'Kevin Dubbs'),
        ('Number of Samples per Tube', '34')
    ]

    with open('/tmp/data.fdf', 'wb') as fdf_file:
        fdf_file.write(forge_fdf(fdf_data_strings=fdf_fields))

    # Combine the form data with the PDF, output to a new file
    subprocess.call(['pdftk', '/home/dfitzgerald/faber_submission.pdf',
                     'fill_form', '/tmp/data.fdf',
                     'output', '/home/dfitzgerald/faber_output.pdf'])



    print 'returning true'

    return True



# def hello():
#     print 'hello'
#
#
# class Facility(SeqFacilityBase):
#     class FacilityForm(forms.Form):
#         po_number = forms.CharField(label=mark_safe('PO #<br/><small>(N/A for UChicago)</small>'))
#         date = forms.DateField(widget=forms.DateInput(format='%m/%d/%Y'), input_formats=('%m/%d/%Y',))
#         pi = forms.ModelChoiceField(queryset=PrincipalInvestigator.objects.all(),
#                                     label='Prinicpal Investigator:')
#
#         @staticmethod
#         def web_to_pdf_field_map():
#             return {
#                 'po_number': 'PO #',
#                 'date': 'Date mmddyyyy',
#                 'pi': 'Principal Investigator'
#                 # TODO Fill in the rest of the map, obviously
#             }
#
#     def form(self, request):
#         """
#         The Faber core needs the following data fields:
#             - PO #
#             - Date
#             - PI and email
#             - Department
#             - Cancer Center Member, yes or no boxes
#             - Experiment contact and email
#             - Billing administrator and email
#             - Sample species, enumerated?
#             - Number of tubes submitted
#             - Number of samples per tube
#             - Library Type, DNA EXOME ChIP RNA and Other Checkboxes, Other has text field
#             - Sample labels
#             - Run Type Request, SR 50bp; SR 100bp; PE 50bp; PE 100bp; Other has text field
#             - Number of lanes requested
#             - Preferred flow cell, 2 lane; 8 lane; none
#             - Index Length, 6 bases; 8 bases; dual; other
#             - Index Manufacturer
#             - Comments
#         """
#
#         context = {
#             'form': Facility.FacilityForm(initial={
#                 'date': datetime.now().strftime('%m/%d/%Y')
#             })
#         }
#
#         return render(request, 'tina/submit/facility/faber.html', context)
#
#     def process_submission(self, post_data):
#         faber_form = Facility.FacilityForm(post_data)  # TODO initial=
#         if not faber_form.is_valid():
#             return False
#
#         # Get cleaned form data, create FDF file to fill out Faber core PDF
#         faber_form_data = faber_form.cleaned_data
#         faber_form_data['date'] = faber_form_data['date'].strftime('%m/%d/%Y')
#
#         fdf_fields = [
#             (pdf_key, faber_form_data[web_key])
#             for web_key, pdf_key
#             in Facility.FacilityForm.web_to_pdf_field_map().iteritems()
#         ]
#         with open('/tmp/data.fdf', 'wb') as fdf_file:
#             fdf_file.write(forge_fdf(fdf_data_strings=fdf_fields))
#
#         # Combine the form data with the PDF, output to a new file
#         subprocess.call(['pdftk', '/home/dfitzgerald/faber_submission.pdf',
#                          'fill_form', '/tmp/data.fdf',
#                          'output', '/home/dfitzgerald/faber_output.pdf'])
#
#         return True
