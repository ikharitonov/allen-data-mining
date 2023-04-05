from allensdk.api.queries.rma_api import RmaApi
from allensdk.api.queries.ontologies_api import OntologiesApi
import pandas as pd

rma = RmaApi()

class RMAStructure:
    """
    A class to represent Allen Atlas structures accessed with RMA queries.
    More info: http://help.brain-map.org/display/api/RESTful+Model+Access+(RMA)

    Attributes
    ----------
    id : int
        ID of the structure.
    acronym : str
        Acronym of the structure.
    full_name : str
        Complete name of the structure.
    full_query : dict
        Full length query RMA output.
    structure_path : str
        Specifies hierarchical organisation of parent structures. Available after 'get_structure_path()' method is called.
        
    Methods
    -------
    get_structure_path():
        Queries acronyms for all parent structures according to the hierarchy in the 'structure_id_path'
    """
    def __init__(self, id=None, acronym=None):
        """
        Queries structure ID or acronym based on the parameter provided.

        Parameters
        ----------
        id : int
            Structure ID.
        acronym : str
            Structure acronym.
        """
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
    """
    A class to represent Allen Structure Sets. They are usually project-specific partitions of the brain with unique definitions.
    More info: http://help.brain-map.org/display/api/Atlas+Drawings+and+Ontologies

    Attributes
    ----------
    structure_sets : pandas.DataFrame
        Table with all available structure sets.
    structure_set : pandas.DataFrame
        Table with all structures in a given structre set. Available after 'get_structure_set()' method is called.
    
    Methods
    -------
    get_all_structure_sets():
        Returns a table with all available structure sets.
    get_structure_set(id=None, select_structure_id=None, start_row=0, num_rows='all'):
        Queries a structure set with a given ID.
    
    """
    def __init__(self):
        oapi = OntologiesApi()
        self.structure_sets = pd.DataFrame(oapi.get_structure_sets())
        self.structure_set = None

    def get_all_structure_sets(self):
        return self.structure_sets
    
    def get_structure_set(self, id=None, select_structure_id=None, start_row=0, num_rows='all'):
        if id:
            if select_structure_id:
                self.structure_set = pd.DataFrame(rma.model_query('Structure', criteria=f"structure_sets[id$eq{id}]", include=f"structure[id$eq{select_structure_id}]", start_row=start_row, num_rows=num_rows))
                return self.structure_set
            else:
                self.structure_set = pd.DataFrame(rma.model_query('Structure', criteria=f"structure_sets[id$eq{id}]", start_row=start_row, num_rows=num_rows))
                return self.structure_set
        else:
            print('ID of structure set not provided.')
            return None

class RMAUnionizedData:
    """
    A class for querying unionized data from Allen database.
    More info: https://allensdk.readthedocs.io/en/latest/unionizes.html

    Attributes
    ----------
    data : pandas.DataFrame
        Unionized data queried with RMA.
    """
    def __init__(self, experiment_id=None, is_injection=False, select_structure_id=None, start_row=0, num_rows='all'):
        """
        Constructs an RMA query and retrives unionized data.

        Parameters
        ----------
        experiment_id : int
            The ID of an experiment to query.
        is_injection : bool
            Specify 'True' for unionized data uniquely from the injection structures to be returned.
        select_structure_id : int
            Specify the ID of the structure which the unionized data is to be returned for.
        start_row : int
            Starting row in the returned query. Default = 0.
        num_rows : int or str
            Specify the number of rows of the query to return. Default = 'all'.
        """
        if not experiment_id:
            print('Experiment ID was not provided.')
        else:
            if is_injection: is_injection='true'
            else: is_injection='false'

            criteria_query = f'[is_injection$eq{is_injection}][section_data_set_id$eq{experiment_id}]'

            if select_structure_id:
                include_query = f'structure[id$eq{select_structure_id}]'
                self.data = pd.DataFrame(rma.model_query("ProjectionStructureUnionize", criteria=criteria_query, start_row=start_row,num_rows=num_rows, include=include_query))
            else:
                self.data = pd.DataFrame(rma.model_query("ProjectionStructureUnionize", criteria=criteria_query, start_row=start_row,num_rows=num_rows))
        
class RMAExpressionData:
    """
    A class for querying expression (ISH) data from Allen database.
    More info: https://mouse.brain-map.org/

    Attributes
    ----------
    data : pandas.DataFrame
        Expression data queried with RMA.
    """
    def __init__(self, gene=None, failed=False, probe_orientation=2):
        """
        Constructs an RMA query and retrives expression data.

        Parameters
        ----------
        gene : str
            The abbreviated name of an gene to query.
        failed : bool
            Specify 'False' to filter out failed experiments.
        probe_orientation : int
            Specify the orientation of the probe (1 for 'Sense', 2 for 'Antisense'). Default = 2.
            More info: http://help.brain-map.org/display/mousebrain/Documentation
        """
        if not gene:
            print('Gene abbreviation was not provided.')
        else:
            if failed: failed='true'
            else: failed='false'

            self.data = pd.DataFrame(rma.model_query('SectionDataSet', criteria=f"products[abbreviation$eq'Mouse'],[failed$eq{failed}],genes[acronym$eq'{gene}'],probes[orientation_id$eq{probe_orientation}]", include="probes(orientation),structure_unionizes"))