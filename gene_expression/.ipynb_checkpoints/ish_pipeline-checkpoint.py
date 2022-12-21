import os
import json
from allensdk.api.queries.rma_api import RmaApi
import pandas as pd
from tqdm.notebook import tqdm
from math import isnan
pd.options.mode.chained_assignment = None

def mkdir(path):
    if not os.path.exists(path): os.makedirs(path)
    return path

def get_receptor_list(path):
    # Formatting receptor names and combining into a list
    return [x.lower()[0].upper()+x.lower()[1:] for x in list(pd.read_excel(path)['Receptor'])]

def select_target_structures_from_df(union_df,target_structure_list):
    df = union_df[union_df['structure_id'].isin(target_structure_list)]
    return df.copy()

def query_structure_name(structure_id):
    query = rma.model_query('StructureLookup', criteria="structure[id$eq"+str(structure_id)+"]",include="structure")[0]
    return query['structure']['acronym']

def save_df_to_csv(df, filename):
    df.to_csv(filename, index=False)
    # print(filename,'saved.')
    
def run_data_mining(cfg):
    
    # Getting structures and receptors from config
    QUERY_AREA_ID = cfg["structures"]  
    receptors = get_receptor_list(cfg["receptors_file_path"])
    
    # Dataframe which will contain metadata of queried experiments (experiment id, structures, filename, plane, availability of data)
    info_df = []
    
    # Main data query loop
    for receptor in tqdm(receptors,"Querying receptor expression data"):
        # Main RMA query
        query = rma.model_query('SectionDataSet', criteria=",".join(cfg["rma_query"]["criteria"])+",genes[acronym$eq'"+receptor+"']", include=",".join(cfg["rma_query"]["include"]))
        data_df = pd.DataFrame(query)
        # Save full uniniozed data into CSV file
        if cfg["save_full_unionized_data"]: save_df_to_csv(data_df, mkdir(mkdir(cfg["output_file_path"])+"full_unionized/")+receptor+".csv")
        # Add add empty metadata and skip if receptor has no associated experiments
        if len(data_df)==0:
            info_df.append({'receptor': receptor,'experiment_id': 'null','plane': 'null','query_area_id': QUERY_AREA_ID,'filename': 'null','has_data': 'false'})
            continue
        
        # Structure unionizes loop
        for exp_id in data_df['id']:
            exp_union_data = pd.DataFrame(data_df[data_df['id']==exp_id]['structure_unionizes'].item())
            # Add metadata and skip if the experiment has an empty structure unionize
            if len(data_df[data_df['id']==exp_id]['structure_unionizes'].item()) == 0:
                info_df.append({'receptor': receptor,'experiment_id': exp_id,'plane': data_df[data_df['id']==exp_id]['plane_of_section_id'].item(),'query_area_id': QUERY_AREA_ID,'filename': 'null','has_data': 'false'})
                continue
            
            # Only select the entries corresponding to the structures of interest
            filtered_df = select_target_structures_from_df(exp_union_data,QUERY_AREA_ID)
            
            # Calculate expression intensity and add to the experiment's structure unionize dataframe
            filtered_df['expression_intensity'] = filtered_df.sum_expressing_pixel_intensity / filtered_df.sum_expressing_pixels

            # Saving structure unionize data for each experiment within each receptor to a CSV file and adding metadata
            filename = 'gene_'+receptor+'_exp_'+str(exp_id)+'_query_area_id_'+str(QUERY_AREA_ID)+'.csv'
            if cfg["save_area_filtered_data"]: save_df_to_csv(filtered_df, mkdir(mkdir(cfg["output_file_path"])+"area_filtered/")+filename)
            info_df.append({'receptor': receptor,'experiment_id': exp_id,'plane': data_df[data_df['id']==exp_id]['plane_of_section_id'].item(),'query_area_id': QUERY_AREA_ID,'filename': filename,'has_data': 'true'})

    # Saving metatdata to CSV file
    if cfg["save_area_filtered_data"]: pd.DataFrame(info_df).to_csv(mkdir(cfg["output_file_path"])+"info.csv", index=False)

def save_to_excel(cfg):
    
    # Querying names corresponding to structure IDs from config
    structures = {query_structure_name(x): x for x in cfg['structures']}
    
    # Loading metadata
    info_df = pd.read_csv(cfg["output_file_path"]+"info.csv")

    # plane_of_section_id = 1 for coronal
    # plane_of_section_id = 2 for saggital
    plane_dict = {1: 'coronal', 2: 'saggital'}
    
    # Main loop for reading, averaging and saving all data types specified in config
    for variable in cfg["excel_data_to_save"]:
        # Dataframe to be saved as excel file
        data_df = []
        # Receptor loop
        for receptor in info_df['receptor'].unique():
            # Experiment loop
            for exp_id in info_df[info_df['receptor']==receptor]['experiment_id']:
                exp_df = info_df[(info_df['receptor']==receptor) & (info_df['experiment_id']==exp_id)]
                # Add 'null' values if receptor has no experiments
                if isnan(exp_id):
                    data_df.append({'receptor': receptor,'experiment_id': 'null','plane': 'null','structure': 'null','structure_id': 'null',variable: 'null'})
                # Add 'null' values if experiment has no unionized data
                elif exp_df['has_data'].item()==False:
                    data_df.append({'receptor': receptor,'experiment_id': int(exp_id),'plane': plane_dict[int(exp_df['plane'].item())],
                                    'structure': 'null','structure_id': 'null',variable: 'null'})
                else:
                    # Add queried value to the excel dataframe for each of the structures of interest
                    for s in structures.keys():
                        union_data_df = pd.read_csv(cfg["output_file_path"]+"area_filtered/"+exp_df['filename'].item())
                        exp_var_df = union_data_df[union_data_df['structure_id']==structures[s]][variable]
                        if len(exp_var_df)==0: exp_variable = 'null'
                        else: exp_variable = exp_var_df.item()
                        data_df.append({'receptor': receptor,'experiment_id': int(exp_id),'plane': plane_dict[int(exp_df['plane'].item())],
                                'structure': s,'structure_id': structures[s],variable: exp_variable})  
        sheet1_df = pd.DataFrame(data_df)

        # Taking an average over experiments
        sheet2_df = []
        for R in info_df['receptor'].unique():
            for S in structures:
                # Selecting all experiments for a particular receptor and structure
                df = sheet1_df[(sheet1_df['receptor']==R) & (sheet1_df['structure']==S)]
                if len(df)==0:
                    sheet2_df.append({'receptor': R,'structure': 'null','structure_id': 'null','average_'+variable: 'null'})
                    continue
                # Taking the mean variable (e.g. expression density) over all experiments in one structure
                exp_var = df[df[variable].apply(lambda x: isinstance(x, float))][variable].mean()
                sheet2_df.append({'receptor': R,'structure': S,'structure_id': structures[S],'average_'+variable: exp_var})
        sheet2_df = pd.DataFrame(sheet2_df)

        # Taking an average over V2m structures
        sheet3_df = []
        for R in info_df['receptor'].unique():
            # Selecting all experiment averages in three V2m structures
            v2m_df = sheet2_df[(sheet2_df['receptor']==R) & (sheet2_df['structure_id']!=778)]
            # Selecting all experiment averages in V1
            v1_df = sheet2_df[(sheet2_df['receptor']==R) & (sheet2_df['structure_id']==778)]
            # Set to temporary variable to 'null' if there are no averaged entries, else set to average
            if len(v2m_df[v2m_df['average_'+variable].apply(lambda x: isinstance(x, float))])==0: v2m_exp_var = 'null'
            else: v2m_exp_var = v2m_df['average_'+variable].mean()
            if len(v1_df[v1_df['average_'+variable].apply(lambda x: isinstance(x, float))])==0: v1_exp_var = 'null'
            else: v1_exp_var = v1_df['average_'+variable].item()

            sheet3_df.append({'receptor': R,'structure': 'V2m','average_'+variable: v2m_exp_var})
            sheet3_df.append({'receptor': R,'structure': 'VISp5','average_'+variable: v1_exp_var})
        sheet3_df = pd.DataFrame(sheet3_df)

        # Save dataframes as excel files
        with pd.ExcelWriter(cfg["output_file_path"]+variable+'_data.xlsx') as writer:
            sheet1_df.to_excel(writer, sheet_name='Full Data')
            sheet2_df.to_excel(writer, sheet_name='Averaged Experiments')
            sheet3_df.to_excel(writer, sheet_name='Averaged Structures')

        print("Saving data to Excel completed.")

if __name__ == '__main__':
    
    rma = RmaApi()
    
    # Reading config file and saving a copy of it in the output directory
    with open(os.path.realpath(os.path.dirname(__file__))+"/config.json", 'r') as file: config = json.loads(file.read())
    with open(mkdir(config["output_file_path"])+"config.json", 'w') as outfile: json.dump(config, outfile)
    
    run_data_mining(config)
    save_to_excel(config)