from allensdk.api.queries.rma_api import RmaApi
import pandas as pd
from tqdm.notebook import tqdm
from math import isnan

rma = RmaApi()

def query_id_path(s_id):
    query = rma.model_query('StructureLookup', criteria="structure[id$eq"+str(s_id)+"]",include="structure",
        options="[only$eq'structure_lookups.termtype,structure_lookups.structure_id_path']")[0]
    return query['structure']['structure_id_path']

def select_structures_from_rma_query_with_given_parent_id(union_df, parent_id):
    df = []
    for s_id in union_df['structure_id']:
        hasParentInPath = str(parent_id) in query_id_path(s_id)
        if hasParentInPath: df.append(union_df[union_df['structure_id']==s_id].to_dict('records')[0])
    df = pd.DataFrame(df)
    return df

def select_target_structures_from_df(union_df,target_structure_list):
    df = union_df[union_df['structure_id'].isin(target_structure_list)]
    return df

def save_df_to_csv(df, filename):
    df.to_csv(filename, index=False)
    print(filename,'saved.')
    
def update_info():
    pass

def add_exp_intensity_column(df):
    pass

def run_data_mining():

    path = "/home/ikharitonov/Desktop/KR1/list_of_receptors.xlsx"
    df = pd.read_excel(path)

    VISam5 = 433
    VISpm5 = 565
    RSPagl = 894
    VISp5 = 778
    QUERY_AREA_ID = [VISam5, VISpm5, RSPagl, VISp5]

    receptors = [x.lower()[0].upper()+x.lower()[1:] for x in list(df['Receptor'])]
    print("Receptors Loaded:")
    print(receptors)

    info_df = []
    for receptor in receptors,'Downloading receptor data':
        data = rma.model_query('SectionDataSet', criteria="[failed$eqfalse],products[abbreviation$eq'Mouse'],genes[acronym$eq'"+receptor+"']", include="structure_unionizes")
        data_df = pd.DataFrame(data)
        print('Receptor:',receptor)
        if len(data_df)==0:
            info_df.append({'receptor': receptor,'experiment_id': 'null','plane': 'null','query_area_id': QUERY_AREA_ID,'filename': 'null','has_data': 'false'})
            print('Receptor',receptor,'does\'t exist or doesn\'t have any experiments. Continuing.')
            print('=== === ===')
            continue
        for exp_id in data_df['id']:
            exp_union_data = pd.DataFrame(data_df[data_df['id']==exp_id]['structure_unionizes'].item())
            if len(data_df[data_df['id']==exp_id]['structure_unionizes'].item()) == 0:
                print('Experiment',exp_id,'contains no unionized data. Continuing.')
                info_df.append({'receptor': receptor,'experiment_id': exp_id,'plane': data_df[data_df['id']==exp_id]['plane_of_section_id'].item(),
                                'query_area_id': QUERY_AREA_ID,'filename': 'null','has_data': 'false'})
                continue
            print('Experiment',exp_id,'data downloaded.')
    #         filtered_df = select_structures_from_rma_query_with_given_parent_id(exp_union_data, QUERY_AREA_ID)
            filtered_df = select_target_structures_from_df(exp_union_data,QUERY_AREA_ID)
            print('Data from target areas filtered.')
            filtered_df['expression_intensity'] = filtered_df.sum_expressing_pixel_intensity / filtered_df.sum_expressing_pixels
            print('Expression intensity values added to data.')
            # filename = 'gene_'+receptor+'_exp_'+str(exp_id)+'_query_id_'+str(QUERY_AREA_ID)+'.csv'
            filename = 'gene_'+receptor+'_exp_'+str(exp_id)+'_query_area_id_'+str(QUERY_AREA_ID)+'.csv'
            save_df_to_csv(filtered_df, filename)
            print('= = =')
            info_df.append({'receptor': receptor,'experiment_id': exp_id,'plane': data_df[data_df['id']==exp_id]['plane_of_section_id'].item(),
                            'query_area_id': QUERY_AREA_ID,'filename': filename,'has_data': 'true'})
        print('=== === ===')
    pd.DataFrame(info_df).to_csv('info.csv',index=False)

def save_to_excel(variable):
    structures = {
        'VISam5': 433,
        'VISpm5': 565,
        'RSPagl': 894,
        'VISp5': 778
    }

    info_df = pd.read_csv('data/info.csv')

    # plane_of_section_id = 1 for coronal
    # plane_of_section_id = 2 for saggital
    plane_dict = {1: 'coronal', 2: 'saggital'}

    data_df = []
    for receptor in info_df['receptor'].unique():
        for exp_id in info_df[info_df['receptor']==receptor]['experiment_id']:
            exp_df = info_df[(info_df['receptor']==receptor) & (info_df['experiment_id']==exp_id)]
            if isnan(exp_id):
                data_df.append({'receptor': receptor,'experiment_id': 'N/A','plane': 'N/A','structure': 'N/A','structure_id': 'N/A',variable: 'N/A'})
            elif exp_df['has_data'].item()==False:
                data_df.append({'receptor': receptor,'experiment_id': int(exp_id),'plane': plane_dict[int(exp_df['plane'].item())],
                                'structure': 'N/A','structure_id': 'N/A',variable: 'N/A'})
            else:
                for s in structures.keys():
                    union_data_df = pd.read_csv('data/'+exp_df['filename'].item())
                    exp_var_df = union_data_df[union_data_df['structure_id']==structures[s]][variable]
                    if len(exp_var_df)==0: exp_variable = 'N/A'
                    else: exp_variable = exp_var_df.item()
                    data_df.append({'receptor': receptor,'experiment_id': int(exp_id),'plane': plane_dict[int(exp_df['plane'].item())],
                            'structure': s,'structure_id': structures[s],variable: exp_variable})
            
    sheet3_df = pd.DataFrame(data_df)

    df = pd.read_excel("/home/ikharitonov/Desktop/KR1/list_of_receptors.xlsx")
    receptors = [x.lower()[0].upper()+x.lower()[1:] for x in list(df['Receptor'])]

    sheet2_df = []
    for R in receptors:
        for S in structures:
            df = sheet3_df[(sheet3_df['receptor']==R) & (sheet3_df['structure']==S)]
            if len(df)==0:
                sheet2_df.append({'receptor': R,'structure': 'N/A','structure_id': 'N/A','average_'+variable: 'N/A'})
                continue
            exp_var = df[df[variable].apply(lambda x: isinstance(x, float))][variable].mean()
            sheet2_df.append({'receptor': R,'structure': S,'structure_id': structures[S],'average_'+variable: exp_var})
    sheet2_df = pd.DataFrame(sheet2_df)

    sheet1_df = []
    for R in receptors:
        v2m_df = sheet2_df[(sheet2_df['receptor']==R) & (sheet2_df['structure_id']!=778)]
        v1_df = sheet2_df[(sheet2_df['receptor']==R) & (sheet2_df['structure_id']==778)]
        if len(v2m_df[v2m_df['average_'+variable].apply(lambda x: isinstance(x, float))])==0: v2m_exp_var = 'N/A'
        else: v2m_exp_var = v2m_df['average_'+variable].mean()
        if len(v1_df[v1_df['average_'+variable].apply(lambda x: isinstance(x, float))])==0: v1_exp_var = 'N/A'
        else: v1_exp_var = v1_df['average_'+variable].item()
            
        sheet1_df.append({'receptor': R,'structure': 'V2m','average_'+variable: v2m_exp_var})
        sheet1_df.append({'receptor': R,'structure': 'VISp5','average_'+variable: v1_exp_var})
    sheet1_df = pd.DataFrame(sheet1_df)

    with pd.ExcelWriter(variable+'_data.xlsx') as writer:  
        sheet1_df.to_excel(writer, sheet_name='Averaged Structures')
        sheet2_df.to_excel(writer, sheet_name='Averaged Experiments')
        sheet3_df.to_excel(writer, sheet_name='Full Data')

    print("Saving data to Excel completed.")

if __name__ == '__main__':
    # run_data_mining()
    save_to_excel('expression_intensity')