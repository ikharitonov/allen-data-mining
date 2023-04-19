# __Mining data from Allen connectivity and In Situ Hybridization (ISH) databases__

## Table of Contents
1. [Connectivity](#connectivity)
2. [In Situ Hybridization](#ish)
3. [Allen Atlas: brain structure divisions and hierarchical sets](#atlases)
4. [Data mining examples](#data-mining)
5. [Visualisation examples](#visualisation)

## 1. <a name=connectivity></a>Connectivity
### 1.1. Allen web portal overview

The main Allen resource used for data mining in this repository is http://connectivity.brain-map.org/. It allows to specify source structure/s, see the experiments injected there and where they project. There also is a 'Target Search', which is replicated in this repository.

### 1.2. Areas of interest and motivation

The idea behind this project is looking for brain-wide inputs to secondary visual cortex, V2M. In Allen Atlas it is composed of: anteromedial visual (VISam), posteromedial visual (VISpm) and retrosplenial lateral agranular (RSPagl) areas. One can specify a target area in the web interface and visualise experiments which project there, but there is no direct access to the raw data for further analysis. This pipeline was built to allow such access and additional processing.

### 1.3. Experiment metadata and Allen brain structure set

VISam, VISpm and RSPagl were specified as Target structures in the web portal and CSV files with metadata for experiments projecting to each of them were downloaded (in 'connectivity_target_experiment_lists').

To match experiments to a consistent list of brain areas, the structure set #167587189, titled "Curated list of non-overlapping substructures at a mid-ontology level" was chosen. It consists of 316 areas and represents an appropriate level of detail.

### 1.4. Pipeline for mining connectivity data, quality checking, filtering and thresholding

Pipeline is composed of the following steps (shown in 'connectivity_pipeline.ipynb'):
- Checking if all experiments have an area reference
- Collecting experiments into a dictionary
- Removing experiments where injection and target structures overlap (e.g., injection area includes RSPagl)
- Downloading or reading unionized data from files
- Only selecting experiments injected into one of the hemispheres at a time
- Removing experiments with zero-valued projections in the Target area
- Thresholding by injection volume
- Separating experiments into ipsilaterally and contralaterally projecting
- Thresholding by projection volume
- Calculating and saving weighted centroids

Experiment IDs are collected into a Python dictionary of the form {area_id_1: [experiment_id_1, experiment_id_2, ...], ...}.

Some experiments projecting to the areas of interest actually contain one of the V2M areas in their injection zone. Such experiments are filtered out.

Unionized data is a structure-wise summary of different projection metrics (density, intensity, energy, volume) calculated from raw signal. More on it here https://allensdk.readthedocs.io/en/latest/unionizes.html. Downloading this data for 2000+ experiments can take several hours on slow internet.

Experiments are considered one hemisphere at a time. To obtain results for the other hemisphere, the pipeline should be rerun (but the unionized data does not need to be redownloaded, it already includes both hemispheres).

Other processing steps include quality checks for zero-valued experiments and thresholding. Even if experiments were selected to have been injected into a particular hemisphere, where they project may differ. That's why they are separated into ipsilateral and contralateral groups. Specified projection metrics accessed through unionized data of these two groups is used to compute centroids as described next.

### 1.5. Weighted centroids

Several projecting experiments characterise the connectivity between Source and Target structures. In order to calculate the average projection per area, weighted centroids were used. Unionized data of each experiment contains xyz coordinates of injection in the Source structure. A mean of those was taken, weighted by the amount of projection into the Target area (can be specified, typically 'projection_energy' or 'normalized_projection_volume').

## 2. <a name=ish></a>In Situ Hybridization

### 2.1. ISH web portal overview

The main web portal to access gene expression data, injection and target structures, experiments, expression summaries, expression visualisations (through online or offline version of 3D BrainExplorer tool), etc is https://mouse.brain-map.org/

[This page](http://help.brain-map.org/display/mousebrain/In+Situ+Hybridization+%28ISH%29+Data) provides explanation of different functions available with the search. It covers [the syntax for search queries](http://help.brain-map.org/display/mousebrain/In+Situ+Hybridization+%28ISH%29+Data#InSituHybridization(ISH)Data-BooleanSyntaxQuery), [starting search from brain structures (Differential Search)](http://help.brain-map.org/display/mousebrain/In+Situ+Hybridization+%28ISH%29+Data#InSituHybridization(ISH)Data-DifferentialSearch) to find what genes they express, comparison to [human microarray datasets (Human Differential Search)](http://help.brain-map.org/display/mousebrain/In+Situ+Hybridization+%28ISH%29+Data#InSituHybridization(ISH)Data-HumanDifferentialSearch).

Exploring genes with similar expression patterns to those queried is possible with [the Corrlative Search](http://help.brain-map.org/display/mousebrain/In+Situ+Hybridization+%28ISH%29+Data#InSituHybridization(ISH)Data-CorrelativeSearch). Once you click on an experiment, a panel to the right appears, which gives access to it.

Details on [experimental detail](http://help.brain-map.org/display/mousebrain/In+Situ+Hybridization+%28ISH%29+Data#InSituHybridization(ISH)Data-ExperimentalDetail) and [image viewer](http://help.brain-map.org/display/mousebrain/In+Situ+Hybridization+%28ISH%29+Data#InSituHybridization(ISH)Data-ExperimentalDetail) are also available.

### 2.2. Accessing the data through the API

The overview of ISH data available through API is given here: http://help.brain-map.org/display/mousebrain/API.

__RESTful Model Access (RMA)__

Gene expression, along with many other data types, are provided through [RMA queries](http://help.brain-map.org/pages/viewpage.action?pageId=5308449). Output provided as _JSON_, _XML_ or _CSV_, it can be parsed accordingly to the format. In essence, RMA queries are URL addresses that can be simply pasted into a browser.

For example, looking up metadata on a particular gene:

http://api.brain-map.org/api/v2/data/query.xml?include=model::Gene[id$eq15]

Other examples of queries can be found [here](http://help.brain-map.org/display/api/Example+Queries+for+Experiment+Metadata).

__Accessing RMA through Web App__

A very convenient way to contruct and test RMA queries (and recommended to understand how they work) is the web [RMA Query Builder Utility](http://api.brain-map.org/examples/rma_builder/rma_builder.html).

To use it:
- select output format
- add "Model" stage
- enter desired parameters
- press "Build Query"

Key parameter to choose is "Model", corresponding to the type of data/metadata/information queried (there are many). Options relevant to this project are "[SectionDataSet](http://api.brain-map.org/api/v2/data/query.xml?criteria=model::SectionDataSet,rma::criteria,products[abbreviation$eqMouse],genes[acronym$eqDrd1],rma::include,structure_unionizes)" (list of experiments for a gene + expression data in unionized format for each experiment) and "[StructureLookup](http://api.brain-map.org/api/v2/data/query.xml?criteria=model::StructureLookup,rma::criteria,structure[id$eq15566],rma::include,structure,rma::options[only$eq%27structure_lookups.structure_id_path,structure_lookups.termtype%27])" (retrieves metadata of brain structures, hierarchical relationships).

Then, there are "criteria" for selection of data. For example, to look up a particular structure, one will want to specify its id. This is done by selecting the category of criteria from drop down list and pressing "[]" to select criterion type (e.g. id) and what it should be equal to (or >, <, etc). Pressing "," allows to add more criteria.

In the "include" option, the overall kind of data to be queried is specificed. In "only" and "except" options, desired data fields to be included in _JSON/XML/CSV_ are further specified.

Hierarchical relationships between "Model" classes in RMA API are available [here](http://api.brain-map.org/class_hierarchy).

__Accessing RMA through Python__

A short guide to working with RMA API in Python is shown [here](https://alleninstitute.github.io/AllenSDK/data_api_client.html). First step after the [installation](https://allensdk.readthedocs.io/en/latest/install.html) is importing _RmaApi_:

```python
from allensdk.api.queries.rma_api import RmaApi
import pandas as pd
import numpy as np
```

Using the [model_query_ method](https://alleninstitute.github.io/AllenSDK/allensdk.api.queries.rma_api.html#allensdk.api.queries.rma_api.RmaApi.model_query) from _RmaApi_ and specifying the parameters, it is possible to extract list of experiments for a gene and display it as _Pandas_ data frame:

```python
rma = RmaApi()

gene = "Drd1"
        
data = rma.model_query('SectionDataSet', criteria="products[abbreviation$eq'Mouse'],genes[acronym$eq'"+gene+"'],probes[orientation_id$eq2]",
                      include="probes(orientation),structure_unionizes")

data_df = pd.DataFrame(data)

data_df.head()
```

| ... | id       | ... | structure_unionizes                               |
| --- | -------- | --- | ------------------------------------------------- |
| ... | 71307280 | ... | [{'expression_density': 0.0159272, 'expression... |
| ... | 352      | ... | [{'expression_density': 0.0136562, 'expression... |
| ... | ...      | ... | ...                                               |

To look up the experiments with useful (Antisense) signal, relevant fields can be selected from the data frame:

```python
print(data_df[data_df['id']==352]['probes'].item()[0]['orientation'])

[Out]: 
{'id': 2, 'name': 'Antisense'}
```

Sense has orientation id = 1 and Antisense has orientation id = 2, which can be used to select appropriate experiments (as above).

*"probes[orientation_id$eq2]"* in "criteria" section of the RMA query specifies that.

__Unionized data format__

In the data frame above, experiment ids are in "id" column and the unionized data is in the "structure_unionizes". The content of "structure_unionizes" column are lists with dictionaries, which themselves can be turned into data frames:

```python
experiment_id = 353

exp_union_data = pd.DataFrame(data_df[data_df['id']==experiment_id]['structure_unionizes'].item())

exp_union_data.head()
```

| expression_density | expression_energy | id        | section_data_set_id | structure_id | ... |
| ------------------ | ----------------- | --------- | ------------------- | ------------ | --- |
| 0.008171           | 1.097120          | 398484594 | 353                 | 15564        | ... |
| 0.008171           | 1.097120          | 398484597 | 353                 | 15565        | ... |
| ...                | ...               | ...       | ...                 | ...          | ... |

As explained [here](http://help.brain-map.org/display/mousebrain/API#API-Expression3DGridsExpressionGridding), expression density, intensity and energy are related to each other in the following way:

```python
single_structure_df = exp_union_data[exp_union_data['structure_id']==15564]

expression_density = single_structure_df['expression_density'].item()
expression_energy = single_structure_df['expression_energy'].item()

sum_expressing_pixel_intensity = single_structure_df['sum_expressing_pixel_intensity'].item()
sum_pixel_intensity = single_structure_df['sum_pixel_intensity'].item()

sum_expressing_pixels = single_structure_df['sum_expressing_pixels'].item()
sum_pixels = single_structure_df['sum_pixels'].item()

expression_intensity = sum_expressing_pixel_intensity / sum_expressing_pixels

print(expression_intensity * expression_density)
print(expression_energy)

[Out]: 
1.0971190040733307
1.09712
```

One can easily obtain the data above (expression density/energy and manually calculate intensity) for a particular brain structure. Here is an example of using RMA query to look up the parent of the structure with id = 15568 and retrieving its expression density:

```python
# Function to make the RMA query

def query_id_path(s_id):
    query = rma.model_query('StructureLookup', criteria="structure[id$eq"+str(s_id)+"]",include="structure",
        options="[only$eq'structure_lookups.termtype,structure_lookups.structure_id_path']")[0]
    return query
```

```python
query = query_id_path(15568)

print("Query contents:")
print(query)

[Out]:
{'id': 4259, 'ontology_id': 12, 'structure_id': 15568, 'term': 'RSP', 'termtype': 'a', 'structure': {'acronym': 'RSP', 'atlas_id': None, 'color_hex_triplet': 'A84D10', 'depth': 4, 'failed': False, 'failed_facet': 734881840, 'graph_id': 17, 'graph_order': 4, 'hemisphere_id': 3, 'id': 15568, 'name': 'rostral secondary prosencephalon', 'neuro_name_structure_id': None, 'neuro_name_structure_id_path': None, 'ontology_id': 12, 'parent_structure_id': 15567, 'safe_name': 'rostral secondary prosencephalon', 'sphinx_id': 9921, 'st_level': 3, 'structure_id_path': '/15564/15565/15566/15567/15568/', 'structure_name_facet': 2675393843, 'weight': 8390}}
```

Its id path is "/15564/15565/15566/15567/15568/". It specifies the hierarchical sequence of structures, starting from its parent (15567) and above. These paths can be different depending on the structure set adopted.

```python
print("expression density =", exp_union_data[exp_union_data['structure_id']==15567]['expression_density'].item())

[Out]:
expression density = 0.0123361
```

__Alternative approach for accessing expression data__

It can be reached through [GridDataApi](https://allensdk.readthedocs.io/en/latest/allensdk.api.queries.grid_data_api.html). The type of data provided is explained [here](http://help.brain-map.org/display/api/Downloading+3-D+Expression+Grid+Data). This API allows downloading projection data as well.

```python
from allensdk.api.queries.grid_data_api import GridDataApi
gda = GridDataApi()

# This downloads to local computer
# gda.download_gene_expression_grid_data(352, GridDataApi.INTENSITY, '/local/path/')
```

### 2.3. Pipeline for querying gene expression data

ISH pipeline takes in a configuration file that specifies:
- Target structures of interest (which are selected from unionized data)
- File with the list of genes of interest for querying
- Parameters for the RMA query (Sense/Antisense, exclude failed experiments, etc)
- Expression metrics to save (density/intensity/energy)
- ...

For each of the receptors a RMA query is made, returning unionized data for all experiments available given the parameters specified. This is optionally saved into a CSV file.

Expression values corresponding to Target structures are selected from sets of unionized records for each experiment. They are also optionally saved in CSV files e.g., 'gene\_Adra1a\_exp\_71152437\_query\_area\_id\_[433, 565, 774, 778].csv' for gene name 'Adra1a', experiment #71152437 and Target structure IDs #433, #565, #774, #778.

Then, this data is saved into several Excel file for each expression metric. File has three sheets: full data, expression metric averaged over experiments, expression metric averaged over structures (defined in 'save_to_excel' function in 'ish_pipeline.py').

## 3. <a name=atlases></a>Allen Atlas: brain structure divisions and hierarchical sets

There are many structural sets used in Allen Atlases. Their levels of coarseness are different. This is the list of main structure sets:

```python
from allensdk.api.queries.ontologies_api import OntologiesApi
pd.set_option("display.max_rows", None, "display.max_columns", None)

oapi = OntologiesApi()
pd.DataFrame(oapi.get_structure_sets())
```

| description | id | name |
| ------------------ | ----------------- | --------- |
| List of structures in Isocortex layer 5	| 667481446 |	Isocortex layer 5 |
| List of structures in Isocortex layer 6b	| 667481450 |	Isocortex layer 6b |
| Summary structures of the cerebellum	| 688152368 |	Cerebellum |
| List of structures representing a coarse level...	| 8 |	NHP - Coarse |
| List of structures sampled for BrainSpan Trans...	| 7 |	Developing Human - Transcriptome |
| list of characteristic glioblastoma tumor elem...	| 306997241 |	GBM - Tumor Features |
| List of structures for ABA Differential Search	| 12 |	ABA - Differential Search |
| List of valid structures for projection target...	| 184527634 |	Mouse Connectivity - Target Search |
| Structures whose surfaces are represented by a...	| 691663206 |	Mouse Brain - Has Surface Mesh |
| Summary structures of the midbrain	| 688152365 |	Midbrain |
| Summary structures of the medulla	| 688152367 |	Medulla |
| Summary structures of the striatum	| 688152361 |	Striatum |
| List of structures representing a structural l...	| 5 |	Human - Structures |
| List of structures used for the HBA gene page	| 147814064 |	Human - Summary |
| Structures representing subdivisions of the mo...	| 687527945 |	Mouse Connectivity - Summary |
| Summary structures of the hippocampal formation	| 688152359 |	Hippocampal Formation |
| List of visual cortex structures targeted for ...	| 514166994 |	Allen Brain Observatory targeted structure set |
| List of NHP structures used for ISH Study	| 267411678 |	NHP - ISH Structures |
| Summary structures of the olfactory areas	| 688152358 |	Olfactory Areas |
| List of structures sampled for BrainSpan LCM s...	| 9 |	Developing Human - LCM |
| List of HBA structures with descendants sample...	| 14 |	Human - Differential Search |
| Curated list of non-overlapping substructures ...	| 167587189 |	Brain – Summary Structures |
| List of structures in Isocortex layer 4	| 667481445 |	Isocortex layer 4 |
| Structures representing the major divisions of...	| 687527670 |	Brain - Major Divisions |
| contains only tumor feature leaf nodes	| 310861484 |	GBM - Tumor Features - Direct Annotation |
| Summary structures of the pallidum	| 688152362 |	Pallidum |
| List of Primary injection structures for BDA/A...	| 114512892 |	Mouse Connectivity - BDA/AAV Primary Injection... |
| List of primary AND secondary injection struct...	| 112905813 |	Mouse Connectivity - BDA/AAV All Injection Str... |
| List of structures for ABA Fine Structure Search	| 10 |	ABA - Fine Structure Search |
| List of primary AND secondary injection struct...	| 112905828 |	Mouse Connectivity - Projection All Injection ... |
| List of structures used for the Developing Hum...	| 157025860 |	Developing Human - LCM Summary |
| List of structures sampled for NHP Macro Micro...	| 149187960 |	NHP Microarray Macro Dissection Structures |
| List of structures representing a coarse level...	| 11 |	Developing Human - Coarse |
| List of structures in Isocortex layer 6a	| 667481449 |	Isocortex layer 6a |
| List of structures representing a areal level ...	| 3 |	Mouse - Areas |
| List of structures sampled for HBA microarray ...	| 6 |	Human - Samples |
| List of structures used for the Developing Mou...	| 183237650 |	Developing Mouse - Coarse |
| List of structures in Isocortex layer 1	| 667481440 |	Isocortex layer 1 |
| Summary structures of the hypothalamus	| 688152364 |	Hypothalamus |
| List of structures in Isocortex layer 2/3	| 667481441 |	Isocortex layer 2/3 |
| List of structures representing a coarse level...	| 4 |	Human - Coarse |
| All mouse visual areas with layers	| 396673091 |	Mouse Cell Types - Structures |
| List of structures sampled in the Ivy Glioblas...	| 312192291 |	GBM - RNA-Seq sampled structures |
| Summary structures of the cortical subplate	| 688152360 |	Cortical Subplate |
| List of structures sampled for NHP LCM project	| 1 |	NHP LCM Structures |
| Summary structures of the thalamus	| 688152363	Thalamus |
| List of structures representing a coarse level...	| 2 |	Mouse - Coarse |
| Summary structures of the isocortex	| 688152357 |	Isocortex |
| List of Primary injection structures for Proje...	| 114512891 |	Mouse Connectivity - Projection Primary Inject... |
| Summary structures of the pons	| 688152366 |	Pons |

Structures within the set can be accessed through the [get_structures_by_set_id](https://allensdk.readthedocs.io/en/latest/allensdk.core.structure_tree.html#allensdk.core.structure_tree.StructureTree.get_structures_by_set_id) method from [StructureTree](https://allensdk.readthedocs.io/en/latest/allensdk.core.structure_tree.html) in [MouseConnectivityCache](https://allensdk.readthedocs.io/en/latest/allensdk.core.mouse_connectivity_cache.html) or using the "Structure" model in RMA query:

```python
def display_structure_set(structure_set_id):
    df = pd.DataFrame(rma.model_query('Structure', criteria="structure_sets[id$eq"+str(structure_set_id)+"]", start_row=0, num_rows='all')).sort_values("graph_order")
    print(len(df),"rows")
    # as in https://github.com/pandas-dev/pandas/issues/33606
    return df.style.set_table_styles([{'selector': 'thead th', 'props': 'position: sticky; top:0; background-color:lightgreen;'}])
```

Below are some of the relevant structure sets which include visual areas.

| description                                                             | id        | name                                           |
| ----------------------------------------------------------------------- | --------- | ---------------------------------------------- |
| All mouse visual areas with layers                                      | 396673091 | Mouse Cell Types - Structures                  |
| List of visual cortex structures targeted for visual coding experiments | 514166994 | Allen Brain Observatory targeted structure set |
| List of structures in Isocortex layer 5                                 | 667481446 | Isocortex layer 5                              |
| Curated list of non-overlapping substructures at a mid-ontology level   | 167587189 | Brain – Summary Structures                     |

## 4. <a name=data-mining></a> Data mining examples

__connectivity/connectivity_pipeline.ipynb___ : allows to specify areas, injection/projection thresholds and mine data (similar to Target search in http://connectivity.brain-map.org/)

__gene_expression/ish_pipeline.py___ : queries ISH data (https://mouse.brain-map.org/) for a list of receptors and a list of areas specified in config file, creates summary Excel files

__10x_genomics/pulling_data.py__ : extracts cell type cluster data from an Excel file provided (https://portal.brain-map.org/atlases-and-data/rnaseq/mouse-whole-cortex-and-hippocampus-10x)

__connectivity/exploring_projections.ipynb__ : downloads projection data for several visual areas and computes brain-wide mean difference per area

## 5. <a name=visualisation></a>Visualisation examples

__visualisers/2D_centroids.ipynb__ : interactive 2D plots of areas across the brain projecting into target area of interest (uses data from __connectivity_pipeline.ipynb__)

__visualisers/rendering.py__ : the same as above, but in 3D (needs [brainrender](https://docs.brainrender.info/) installed, see brainrender.yml)

__visualisers/proj_slice_viewer.py__ : scroll through slices of 3D volume of mean (absolute) difference data created in __connectivity/exploring_projections.ipynb__

__visualisers/slider_slice_viewer.py__ : has a slider and uses annotation information to display area names (needs data and _annotation.npy_ from __connectivity/exploring_projections.ipynb__)
```
# Run from console:
python slider_slice_viewer.py /example/data/path/VISpm_VISam_MD.npy
# annotation.npy is expected to be in the data directory
```
