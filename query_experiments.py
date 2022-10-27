import pandas as pd
from allensdk.core.mouse_connectivity_cache import MouseConnectivityCache
from allensdk.api.queries.ontologies_api import OntologiesApi

def run():
    mcc = MouseConnectivityCache()

    print("List of available brain areas:")
    onto_api = OntologiesApi()
    structure_tree = mcc.get_structure_tree()
    # structure_set_ids = list(structure_tree.get_structure_sets())
    # for s in structure_set_ids:
    #     print("Area:",)
    # print(type(list(structure_set_ids)))
    # print(onto_api.get_structure_graphs())

    summary_structures = structure_tree.get_structures_by_set_id([167587189])
    print(pd.DataFrame(summary_structures)[['name','id']])

    coarse_set_list = structure_tree.get_structures_by_set_id([2])
    coarse_set = []
    for area in coarse_set_list: coarse_set.append({'name': area['name'], 'id': area['id']})
    print(coarse_set)
    # structure_names = [structure_tree.get_structures_by_id({x}) for x in structure_tree.get_structure_sets()]
    # structure_names = []
    # for id in structure_tree.get_structure_sets():
    #     structure_names.append(structure_tree.get_structures_by_id(id))
    # print(structure_names)

if __name__ == '__main__':
    run()
