# __Summary: mining data from Allen connectivity and In Situ Hybridization (ISH) databases__

## 1. Connectivity
### 1.1. Allen web portal overview

The main Allen resource used for data mining in this repository is http://connectivity.brain-map.org/. It allows to specify source structure/s, see the experiments injected there and where they project. There also is a 'Target Search', which is replicated in this repository.

### 1.2. Areas of interest and motivation

The idea behind this project is looking for brain-wide inputs to secondary visual cortex, V2M. In Allen Atlas it is composed of: anteromedial visual (VISam), posteromedial visual (VISpm) and retrosplenial lateral agranular (RSPagl) areas. One can specify a target area in the web interface and visualise experiments which project there, but there is no direct access to the raw data for further analysis. This pipeline was built to allow such access and additional processing.

### 1.3. Experiment metadata and Allen brain structure set

VISam, VISpm and RSPagl were specified as Target structures in the web portal and CSV files with metadata for experiments projecting to each of them were downloaded (in 'connectivity_target_experiment_lists').

To match experiments to a consistent list of brain areas, the structure set #167587189, titled "Curated list of non-overlapping substructures at a mid-ontology level" was chosen. It consists of 316 areas and represents an appropriate level of detail.

### 1.4. Pipeline for mining connectivity data, quality checking, filtering and thresholding

Pipeline is composed of the following steps:
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

## 2. In Situ Hybridization

### 2.1. ISH web portal overview

The main web portal to access gene expression data, injection and target structures, experiments, expression summaries, expression visualisations (through online or offline version of 3D BrainExplorer tool), etc is https://mouse.brain-map.org/

[This page](http://help.brain-map.org/display/mousebrain/In+Situ+Hybridization+%28ISH%29+Data) provides explanation of different functions available with the search. It covers [the syntax for search queries](http://help.brain-map.org/display/mousebrain/In+Situ+Hybridization+%28ISH%29+Data#InSituHybridization(ISH)Data-BooleanSyntaxQuery), [starting search from brain structures (Differential Search)](http://help.brain-map.org/display/mousebrain/In+Situ+Hybridization+%28ISH%29+Data#InSituHybridization(ISH)Data-DifferentialSearch) to find what genes they express, comparison to [human microarray datasets (Human Differential Search)](http://help.brain-map.org/display/mousebrain/In+Situ+Hybridization+%28ISH%29+Data#InSituHybridization(ISH)Data-HumanDifferentialSearch).

Exploring genes with similar expression patterns to those queried is possible with [the Corrlative Search](http://help.brain-map.org/display/mousebrain/In+Situ+Hybridization+%28ISH%29+Data#InSituHybridization(ISH)Data-CorrelativeSearch). Once you click on an experiment, a panel to the right appears, which gives access to it.

Details on [experimental detail](http://help.brain-map.org/display/mousebrain/In+Situ+Hybridization+%28ISH%29+Data#InSituHybridization(ISH)Data-ExperimentalDetail) and [image viewer](http://help.brain-map.org/display/mousebrain/In+Situ+Hybridization+%28ISH%29+Data#InSituHybridization(ISH)Data-ExperimentalDetail) are also available.
