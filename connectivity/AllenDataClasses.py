import os
import json
from tqdm import tqdm
import pickle
import pandas as pd
from RMALoaders import *

class AllenConnectivity:
    """
    A class to handle loading of unionized data, filtering of experiments, quality checks, thresholding, separation of ipsilateral and contralateral projections.
    """
    def __init__(self, config_path, data_path, save_path):
        """
        Loads parameters from configuration file and metadata for experiments and brain areas.
        Experiment metadata is assumed to be contained in CSV files with target structure names (e.g., 'VISp.csv') in 'data_path' directory.

        Parameters
        ----------
        config_path : str
            Path to the JSON configuration file.
        data_path : str
            Path to the directory where experiment metadata is stored.
        save_path :
            Path to the directory where downloaded data is to be saved.
        """
        self.config_path = config_path
        self.data_path = data_path
        self.save_path = save_path

        self.parse_config()

        self.target_structure_object = RMAStructure(acronym=self.target_structure_name)
        self.target_structure_id = self.target_structure_object.id


        self.experiment_metadata = pd.read_csv(self.data_path / f'{self.target_structure_name}.csv')
        structure_sets = RMAStructureSet()
        self.structure_set = structure_sets.get_structure_set(id=167587189) # Curated list of non-overlapping substructures at a mid-ontology level

        # Collect experiments in {area_id_1: [experiment_id_1, experiment_id_2, ...]} dictionary
        self.experiment_list = {area_id: list(self.experiment_metadata[self.experiment_metadata['structure-id']==area_id]['id']) for area_id in self.structure_set['id']}
        total_num_collected_exps = sum(len(self.experiment_list[area_id]) for area_id in self.experiment_list.keys())

        print(len(self.experiment_list.keys()),"number of areas collected in the dictionary.")
        print(total_num_collected_exps,"experiments collected in the dictionary.")
    
    def parse_config(self):
        """
        Loads parameters from the configuration file.
        """
        with open(self.config_path, 'r') as file: self.config = json.loads(file.read())
        self.target_structure_name = self.config["target_structure"]
        self.projection_metric = self.config["projection_metric"]
        self.hemisphere_id_to_select = self.config["hemisphere_id_to_select"]
        self.injection_volume_threshold = self.config["injection_volume_threshold"]
        self.projection_volume_threshold = self.config["projection_volume_threshold"]
        self.metric_for_projection_thresholding = self.config["metric_for_projection_thresholding"]
        self.read_unionized_data = self.config["read_unionized_data"]
        self.read_experiment_list = self.config["read_experiment_list"]

    def areas_experiments_cross_check(self):
        # make a copy of experiment metadata
        unmatched_df = self.experiment_metadata.copy()
        num_collected_exps = 0

        # loop through brain areas, removing experiments successfully matching with an area
        for area_id in self.structure_set['id']:
            indexes_to_drop = self.experiment_metadata.index[self.experiment_metadata['structure-id']==area_id]
            num_collected_exps += len(indexes_to_drop)
            unmatched_df = unmatched_df.drop(indexes_to_drop)

        print(f'Number of experiments from metadata ({len(self.experiment_metadata)}) corresponds to the number of experiments matched with Allen structure set ({num_collected_exps}) ==> {len(self.experiment_metadata) == num_collected_exps}.')
    
    def remove_injection_target_overlap_areas(self):
        """
        Filtering out experiments with overlapping injection and target structures.
        """
        experiment_list_inj_structs_removed = {}
        exps_removed = []

        for area_id, exps in self.experiment_list.items():
            # if a V2m structure id is contained in injection-structures of an experiment, drop that experiment (id) from experiment_list
            exps_ids_to_retain = []
            for exp_id in exps:
                # Loading and formatting dictionary with experiment's injection structures from Allen metadata
                inj_structs_dict = json.loads(self.experiment_metadata[self.experiment_metadata['id']==exp_id]['injection-structures'].item().replace("=>",":"))
                # Getting ids of experiment's injection structures
                inj_structs_id_list = [x['id'] for x in inj_structs_dict]
                if self.target_structure_id in inj_structs_id_list: exps_removed.append(exp_id)
                else: exps_ids_to_retain.append(exp_id)
            experiment_list_inj_structs_removed[area_id] = exps_ids_to_retain
        print(f'{len(exps_removed)} experiments removed:')
        print(exps_removed)

        del self.experiment_list
        self.experiment_list = experiment_list_inj_structs_removed

    def mkdir(path):
        if not os.path.exists(path): os.makedirs(path)
        return path
    
    def load_unionized_data(self):
        """
        Each csv file with unionized data is read into memory.
        """
        area_experiment_unionized_data = {}
        foldername = f'{self.target_structure_name}_unionized_data'
        for area, experiments in tqdm(self.experiment_list.items(),'Loading'):
            area_experiment_unionized_data[area] = {}
            for e in experiments:
                filename = f'area_{area}_experiment_{e}.csv'
                temp_df = pd.read_csv(self.save_path / foldername / filename)
                area_experiment_unionized_data[area][e] = temp_df
        self.unionized_data = area_experiment_unionized_data

    def download_unionized_data(self):
        """
        For each area, each experiment, download unionized data.
        """
        if not self.read_unionized_data:
            foldername = f'{self.target_structure_name}_unionized_data'
            path = self.mkdir(self.save_path / foldername)
            for area, experiments in tqdm(self.experiment_list.items(),'Downloading'):
                for e in experiments:
                    filename = f'area_{area}_experiment_{e}.csv'
                    # Skip if it already was downloaded
                    if os.path.isfile(self.save_path / foldername / filename):
                        continue
                    else:
                        temp_data = RMAUnionizedData(experiment_id=e).data
                        temp_data.to_csv(self.save_path / foldername / filename)
        else: print('Unionized data already downloaded.')

    # def load_unionized_data(self):
    #     if self.read_unionized_data: 
    #         self.unionized_data = self.unionized_data_from_csv_files()
    #     else: 
    #         self.unionized_data_RMA_query()
    #         self.read_unionized_data = True

    def get_hemisphere_from_z_coordinate(unionized_data):
        """
        Returns the hemisphere_id of the row in passed unionized data with the biggest volume.
        
            Parameters:
                unionized_data (pandas.DataFrame): unionized data with a single structure selected
                
            Returns:
                hemisphere_id (int): 1 for left hemisphere and 2 for right hemisphere. If there is no injection structure with specified structure_id, 0 is returned.
        """
        z_coord = unionized_data['max_voxel_z'].unique()
        # if there is data in both hemispheres, choose the one with higher volume
        if len(z_coord) > 1:
            z_coord = [unionized_data.iloc[unionized_data['volume'].idxmax()]['max_voxel_z']]

        if len(z_coord)==0: return 0
        elif z_coord[0] < 5700: return 1
        elif z_coord[0] >= 5700: return 2

    def check_hemisphere(self, experiment_id, structure_id):
        """
        Returns the hemisphere_id for a given injection structure and experiment id. If the injection spans both hemispheres, the one with higher volume is chosen.
        
            Parameters:
                experiment_id (int): id of the experiment (section_data_set_id).
                structure_id (int): id of the injection structure.
                
            Returns:
                hemisphere_id (int): 1 for left hemisphere and 2 for right hemisphere. If there is no injection structure with specified structure_id, 0 is returned.
        """
        temp_data = RMAUnionizedData(experiment_id=experiment_id, is_injection=True, select_structure_id=structure_id).data.reset_index(drop=True)

        return self.get_hemisphere_from_z_coordinate(temp_data)
    
    def select_by_hemisphere(self):
        """
        Removing all experiments that were not injected in the specified hemisphere.
        """
        
        if self.read_experiment_list:
            # Reading from a file
            filename = f'{self.target_structure_name}_experiment_list_filtered_by_hemisphere_{self.hemisphere_id_to_select}.pkl'
            with open(self.save_path / filename, 'rb') as f: experiment_list_filtered_by_hemisphere = pickle.load(f)
        else:
            # Copy the dictionary
            experiment_list_filtered_by_hemisphere = {k:v.copy() for k,v in self.experiment_list.items()}
            exps_removed = []
            for area, exps in tqdm(experiment_list_filtered_by_hemisphere.items()):
                for e in exps:
                    ind = exps.index(e)
                    hem = self.check_hemisphere(e, area)
                    if hem != self.hemisphere_id_to_select: exps_removed.append(experiment_list_filtered_by_hemisphere[area].pop(ind))
            print(len(exps_removed),"experiments removed:")
            print(exps_removed)
            # Saving to a file
            filename = f'{self.target_structure_name}_experiment_list_filtered_by_hemisphere_{self.hemisphere_id_to_select}.pkl'
            with open(self.save_path / filename, 'wb') as f: pickle.dump(experiment_list_filtered_by_hemisphere, f)

        del self.experiment_list
        self.experiment_list = experiment_list_filtered_by_hemisphere

    def zero_projection_QC(self):
        # Load the data because it is needed now to check projection values
        self.load_unionized_data()

        print(f'number of experiments BEFORE zero-valued projection QC = {sum(len(self.unionized_data[area]) for area in self.unionized_data.keys())}')

        temp_dict = {}
        for area in self.unionized_data:
            temp_dict[area] = {}
            for exp, exp_df in self.unionized_data[area].items():
                if (exp_df[exp_df['structure_id']==self.target_structure_id][self.projection_metric] == 0).any():
                    continue
                else:
                    temp_dict[area][exp] = exp_df

        del self.unionized_data
        self.unionized_data = temp_dict

        print(f'number of experiments AFTER zero-valued projection QC = {sum(len(self.unionized_data[area]) for area in self.unionized_data.keys())}')

    def get_vol_from_downloaded_unionized_data(self, area, experiment):        
        # Query data for injection structure and return volume of injection hemisphere
        temp_data = RMAUnionizedData(experiment_id=experiment,is_injection=True,select_structure_id=area).data.reset_index(drop=True)
        temp_data = temp_data[temp_data['hemisphere_id']==self.get_hemisphere_from_z_coordinate(temp_data)]
        return temp_data['volume'].item()

    def injection_volume_thresholding(self):
        print(f'number of experiments BEFORE injection volume thresholding = {sum(len(self.unionized_data[area]) for area in self.unionized_data.keys())}')

        temp_dict = {}

        for area in tqdm(self.unionized_data):
            temp_dict[area] = {}
            for exp, exp_df in self.unionized_data[area].items():
                temp_vol = self.get_vol_from_downloaded_unionized_data(area, exp)
                if temp_vol >= self.injection_volume_threshold:
                    temp_dict[area][exp] = self.unionized_data[area][exp]
        del self.unionized_data
        self.unionized_data = temp_dict

        print(f'number of experiments AFTER injection volume thresholding = {sum(len(self.unionized_data[area]) for area in self.unionized_data.keys())}')

    def separate_by_projection_hemisphere(self):
        # And collect experiments into two dictionaries based on hemisphere where projection metric is higher

        self.ipsilateral_unionized_data = {}
        self.contralateral_unionized_data = {}

        hem_ids = [2,1] # for getting the index of contralateral hemisphere to the one specified in the config

        for area in self.unionized_data:
            self.ipsilateral_unionized_data[area] = {}
            self.contralateral_unionized_data[area] = {}
            for exp, exp_df in self.unionized_data[area].items():
                # Checking if unionized data of experiment has higher projection metric value in previosly selected hemisphere
                if exp_df[(exp_df['hemisphere_id']==self.hemisphere_id_to_select) & (exp_df['structure_id']==self.target_structure_id)][self.projection_metric].item() > exp_df[(exp_df['hemisphere_id']==hem_ids[self.hemisphere_id_to_select-1]) & (exp_df['structure_id']==self.target_structure_id)][self.projection_metric].item():
                    # Taking coordinates data from the Source structure and joining it with projection metric data from Target structure (for the convenience of access later) in one dataframe
                    temp_df1 = exp_df[exp_df['structure_id']==area][['hemisphere_id','max_voxel_x','max_voxel_y','max_voxel_z']]
                    temp_df2 = exp_df[exp_df['structure_id']==self.target_structure_id][['hemisphere_id',self.projection_metric]]
                    self.ipsilateral_unionized_data[area][exp] = temp_df1.merge(temp_df2, on='hemisphere_id')
                else: 
                    temp_df1 = exp_df[exp_df['structure_id']==area][['hemisphere_id','max_voxel_x','max_voxel_y','max_voxel_z']]
                    temp_df2 = exp_df[exp_df['structure_id']==self.target_structure_id][['hemisphere_id',self.projection_metric]]
                    self.contralateral_unionized_data[area][exp] = temp_df1.merge(temp_df2, on='hemisphere_id')

        print(f'{sum(len(self.ipsilateral_unionized_data[area]) for area in self.ipsilateral_unionized_data.keys())} ipsilaterally projecting experiments.')
        print(f'{sum(len(self.contralateral_unionized_data[area]) for area in self.contralateral_unionized_data.keys())} contralaterally projecting experiments.')

    def projection_volume_thresholding(self):
        # In ipsilateral experiments, thresholding is done on target structure in the same hemisphere as 'hemisphere_id_to_select'. In contralateral, the opposite.

        print(f'Number of ipsilateral experiments BEFORE projection volume thresholding = {sum(len(self.ipsilateral_unionized_data[area]) for area in self.ipsilateral_unionized_data.keys())}')
        print(f'Number of contralateral experiments BEFORE projection volume thresholding = {sum(len(self.contralateral_unionized_data[area]) for area in self.contralateral_unionized_data.keys())}')

        hem_ids = [2,1]

        temp_ipsilateral_dict = {}
        temp_contralateral_dict = {}

        for area in tqdm(self.ipsilateral_unionized_data.keys, 'ipsilateral'):
            temp_ipsilateral_dict[area] = {}
            for exp, exp_df in self.ipsilateral_unionized_data[area].items():
                proj_vol = exp_df[(exp_df['hemisphere_id']==self.hemisphere_id_to_select) & (exp_df['structure_id']==self.target_structure_id)][self.metric_for_projection_thresholding].item()
                if proj_vol >= self.projection_volume_threshold:
                    temp_ipsilateral_dict[area][exp] = exp_df

        for area in tqdm(self.contralateral_unionized_data.keys, 'contralateral'):
            temp_contralateral_dict[area] = {}
            for exp, exp_df in self.contralateral_unionized_data[area].items():
                proj_vol = exp_df[(exp_df['hemisphere_id']==hem_ids[self.hemisphere_id_to_select-1]) & (exp_df['structure_id']==self.target_structure_id)][self.metric_for_projection_thresholding].item()
                if proj_vol >= self.projection_volume_threshold:
                    temp_contralateral_dict[area][exp] = exp_df

        del self.ipsilateral_unionized_data
        del self.contralateral_unionized_data
        self.ipsilateral_unionized_data = temp_ipsilateral_dict
        self.contralateral_unionized_data = temp_contralateral_dict
        
        print(f'Number of ipsilateral experiments AFTER projection volume thresholding = {sum(len(self.ipsilateral_unionized_data[area]) for area in self.ipsilateral_unionized_data.keys())}')
        print(f'Number of contralateral experiments AFTER projection volume thresholding = {sum(len(self.contralateral_unionized_data[area]) for area in self.contralateral_unionized_data.keys())}')

    def xyz_weighted_centroid(coordinates):
        """
        Returns xyz coordinates of a centroid weighted by vertices and the associated average projection metric. Computed to determine central coordinate within a brain region, weighted by projection metric of each experiment injected in that region.
        
        cx = (v1x*m1 + v2x*m2 + ... vnx*mn) / (m1 + m2 .... mn) 
        cy = (v1y*m1 + v2y*m2 + ... vny*mn) / (m1 + m2 .... mn)
        cz = (v1z*m1 + v2z*m2 + ... vnz*mn) / (m1 + m2 .... mn)
        
        where v1x, v1y and v1z are xyz coordinates of vertex 1 and m1 is its weight.
        
            Parameters:
                coordinates (List): list of nested lists containing coordinates and weight of each vertex nested [[x1, y1, z3, w1], [x2, y2, z2, w2], ...].
            
            Returns:
                centroid_point (List): location of centroid and related average value of projection metric in the form of [x, y, z, avg_projection].
        """
        denom = sum(exp[3] for exp in coordinates)
        centroid_point = [int(sum(exp[0]*exp[3] for exp in coordinates) / denom), int(sum(exp[1]*exp[3] for exp in coordinates) / denom), int(sum(exp[2]*exp[3] for exp in coordinates) / denom), denom / len(coordinates)]
        
        return centroid_point

    def compute_weighted_centroids(self):
        hem_ids = [2,1] # for getting the index of contralateral hemisphere to the one specified before

        self.ipsilateral_centroids_dict = {}
        self.contralateral_centroids_dict = {}

        for area in self.ipsilateral_unionized_data:
            coordinates = [[exp[exp['hemisphere_id']==self.hemisphere_id_to_select]['max_voxel_x'].item(), exp[exp['hemisphere_id']==self.hemisphere_id_to_select]['max_voxel_y'].item(), exp[exp['hemisphere_id']==self.hemisphere_id_to_select]['max_voxel_z'].item(), exp[exp['hemisphere_id']==self.hemisphere_id_to_select][self.projection_metric].item()] for exp in self.ipsilateral_unionized_data[area].values()]
            if len(coordinates) == 0: centroid_xyz = None
            else: centroid_xyz = self.xyz_weighted_centroid(coordinates)
            if centroid_xyz: self.ipsilateral_centroids_dict[area] = centroid_xyz
        print(len(self.ipsilateral_centroids_dict.keys()),'ipsilateral centroids computed out of',str(len(self.ipsilateral_unionized_data.keys())),'regions')

        for area in self.contralateral_unionized_data:
            coordinates = [[exp[exp['hemisphere_id']==hem_ids[self.hemisphere_id_to_select-1]]['max_voxel_x'].item(), exp[exp['hemisphere_id']==hem_ids[self.hemisphere_id_to_select-1]]['max_voxel_y'].item(), exp[exp['hemisphere_id']==hem_ids[self.hemisphere_id_to_select-1]]['max_voxel_z'].item(), exp[exp['hemisphere_id']==hem_ids[self.hemisphere_id_to_select-1]][self.projection_metric].item()] for exp in self.contralateral_unionized_data[area].values()]
            if len(coordinates) == 0: centroid_xyz = None
            else: centroid_xyz = self.xyz_weighted_centroid(coordinates)
            if centroid_xyz: self.contralateral_centroids_dict[area] = centroid_xyz
        print(len(self.contralateral_centroids_dict.keys()),'contralateral centroids computed out of',str(len(self.contralateral_unionized_data.keys())),'regions')

    def save_centroids(self):
        foldername = f'centroids_{self.projection_metric}_hem_id_{self.hemisphere_id_to_select}_inj_vol_thresh_{self.injection_volume_threshold}_target_vol_thresh_{self.projection_volume_threshold}_{self.target_structure_name}'
        folderpath = self.save_path / foldername
        path = self.mkdir(folderpath)

        filename = f'ipsilateral_centroids_dict_hem_{self.hemisphere_id_to_select}_inj_vol_thresh_{self.injection_volume_threshold}_target_vol_thresh_{self.projection_volume_threshold}_{self.target_structure_name}.pkl'
        with open(folderpath / filename, 'wb') as f: pickle.dump(self.ipsilateral_unionized_data, f)
        filename = f'contralateral_centroids_dict_hem_{self.hemisphere_id_to_select}_inj_vol_thresh_{self.injection_volume_threshold}_target_vol_thresh_{self.projection_volume_threshold}_{self.target_structure_name}.pkl'
        with open(folderpath / filename, 'wb') as f: pickle.dump(self.contralateral_unionized_data, f)