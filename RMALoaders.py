from allensdk.api.queries.rma_api import RmaApi
from allensdk.api.queries.ontologies_api import OntologiesApi
import pandas as pd

rma = RmaApi()

class RMAStructure:
    def __init__(self, id=None, acronym=None):
        self.id = id
        self.acronym = acronym
        self.structure_path = None

        if self.id:
            self.full_query = rma.model_query('StructureLookup', criteria="structure[id$eq"+str(self.id)+"]",include="structure")[0]
            self.acronym = self.full_query['structure']['acronym']
        elif self.acronym:
            self.full_query = rma.model_query('StructureLookup', criteria="structure[acronym$eq"+self.acronym+"]",include="structure")[0]
            self.id = self.full_query['structure']['id']
        else:
            print('ID or acronym of structure not provided.')
        
        self.full_name = self.full_query['structure']['name']
        
    def get_structure_path(self):
        id_path = self.full_query['structure']['structure_id_path']
        path_acronyms = [RMAStructure(id=area_id).acronym for area_id in id_path.split('/')[1:-1]]
        self.structure_path = '/'.join(path_acronyms)
        return self.structure_path
    
class RMAStructureSet:
    def __init__(self):
        oapi = OntologiesApi()
        self.structure_sets = pd.DataFrame(oapi.get_structure_sets())

    def get_all_structure_sets(self):
        return self.structure_sets
    
    def get_structure_set(self, id=None):
        if id:
            self.structure_set = pd.DataFrame(rma.model_query('Structure', criteria="structure_sets[id$eq"+str(id)+"]", start_row=0, num_rows='all'))
            return self.structure_set
        else:
            print('ID of structure set not provided.')
            return None

class RMAUnionizedData:
    def __init__(self, experiment_id=None, is_injection=False, select_structure_id=None, start_row=0, num_rows='all'):
        if not experiment_id:
            print('Experiment ID was not provided.')
        else:
            if is_injection: is_injection='true'
            else: is_injection='false'

            criteria_query = f'[is_injection$eq{is_injection}][section_data_set_id$eq{experiment_id}]'

            if select_structure_id:
                include_query = f'structure[id$eq{select_structure_id}]'
                return pd.DataFrame(rma.model_query("ProjectionStructureUnionize", criteria=criteria_query, start_row=start_row,num_rows=num_rows, include=include_query))
            else:
                return pd.DataFrame(rma.model_query("ProjectionStructureUnionize", criteria=criteria_query, start_row=start_row,num_rows=num_rows, include=include_query))
        
class RMAExpressionData:
    def __init__(self, gene=None, failed=False, probe_orientation=2):
        if not gene:
            print('Gene abbreviation was not provided.')
        else:
            if failed: failed='true'
            else: failed='false'

            return pd.DataFrame(rma.model_query('SectionDataSet', criteria=f"products[abbreviation$eq'Mouse'],[failed$eq{failed}],genes[acronym$eq'{gene}'],probes[orientation_id$eq{probe_orientation}]", include="probes(orientation),structure_unionizes"))