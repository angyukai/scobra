import re
import cobra
from ..classes.model import model
from .Excel import ReadExcel, WriteExcel
from .ScrumPy import ReadScrumPyModel, WriteScrumPyModel

def ReadModel(model_file=None, model_format=None, excel_parse="cobra_string",
          old_sbml=False, legacy_metabolite=False, use_hyphens=False,
          variable_name=None, Print=False, compartment_dic={}, bounds=1000.0, **kwargs):
    """ model_format = "sbml" | "excel" | "matlab" | "json" | "scrumpy"
        excel_parse = "cobra_string" | "cobra_position" """
    if not model_file:
        pass
    elif model_format == "sbml" or model_format == "xml" or (
        model_format == None and model_file.endswith(".sbml")) or (
        model_format == None and model_file.endswith(".xml")):
        model_file = cobra.io.read_sbml_model(model_file,
            old_sbml=old_sbml, legacy_metabolite=legacy_metabolite,
            print_time=False, use_hyphens=use_hyphens)
    elif model_format == "matlab" or (model_format == None and
        model_file.endswith(".mat")):
        model_file = cobra.io.load_matlab_model(model_file,
                                                variable_name=variable_name)
    elif model_format == "json" or (model_format == None and
                                            model_file.endswith(".json")):
        model_file = cobra.io.load_json_model(model_file)
    elif model_format == "excel" or model_format == "xls" or \
        model_format == "cobra" or (model_format == None and
        model_file.endswith(".xls")) or (model_format == None
                                    and model_file.endswith(".xlsx")):
        model_file = ReadExcel(model_file,
                                       parse=excel_parse, Print=Print, **kwargs)
    elif model_format == "scrumpy" or model_format == "spy" or (
        model_format == None and model_file.endswith(".spy")):
        model_file = ReadScrumPyModel(model_file,
                    compartment_dic=compartment_dic, Print=Print, **kwargs)
    m = model(model_file)
    if isinstance(model_file, basestring):
        m.description = m.id = model_file.rsplit(".",1)[0]
    m.SetBounds(bounds=bounds)
    return m

def WriteModel(model, filename, model_format=None, excel_format="cobra",
               fbc=False, ExtReacs=[], **kwargs):
    """ model_format = "sbml" | "excel" | "matlab" | "json" | "cobra" | "cobra_old" | "scrumpy" """
    if model_format == "sbml" or model_format == "xml"or (
        model_format == None and filename.endswith(".sbml")) or (
        model_format == None and filename.endswith(".xml")):
        description = model.description
        model.description = str(description)
        m_id = model.id
        model.id = str(m_id)
        compartments = model.compartments
        if not model.compartments:
            model.compartments = {'':''}
        original_met_id = {}
        original_met_compartment = {}
        for met in model.metabolites:    # changes metabolites in the model
            original_met_id[met] = met.id
            original_met_compartment[met] = met.compartment
            met.id = re.sub('[-/().,\[\]+]','_',met.id)
            if not met.compartment:
                met.compartment = ''
        original_reac_id = {}
        for reac in model.reactions:
            original_reac_id[reac] = reac.id
            reac.id = re.sub('[-/().,\[\]+]','_',reac.id)
        # cobra.io.write_sbml_model(model, filename=filename,
        #     sbml_level=sbml_level, sbml_version=sbml_version,
        #     print_time=False, use_fbc_package=fbc)
        cobra.io.write_sbml_model(model, filename=filename,
                                  use_fbc_package=fbc, **kwargs)
        model.description = description
        model.id = m_id
        model.compartments = compartments
        for met in model.metabolites:    # revert changes to metabolites
            met.id = original_met_id[met]
            met.compartment = original_met_compartment[met]
        for reac in model.reactions:
            reac.id = original_reac_id[reac]
    elif model_format == "matlab" or (
                model_format == None and filename.endswith(".mat")):
        cobra.io.save_matlab_model(model, filename)
    elif model_format == "json" or (
                model_format == None and filename.endswith(".json")):
        cobra.io.save_json_model(model, filename)
    elif model_format == "excel" or model_format == "xls" or (
        model_format == None and filename.endswith(".xls")) or (
        model_format == None and filename.endswith(".xlsx")):
        WriteExcel(model, filename, excel_format=excel_format)
    elif model_format == "cobra":
        WriteExcel(model, filename, excel_format="cobra")
    elif model_format == "cobra_old":
        WriteExcel(model, filename, excel_format="cobra_old")
    elif model_format == "scrumpy" or model_format == "spy" or (
                model_format == None and filename.endswith(".spy")):
        WriteScrumPyModel(model, filename, ExtReacs=ExtReacs)
