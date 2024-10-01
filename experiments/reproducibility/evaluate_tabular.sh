#!/bin/bash

# Arrays to store datasets and their corresponding methods
DATASETS=(
    airbnb-simplified_subsampled
    rossmann_subsampled
    walmart_subsampled_12
    Biodegradability_v1
    imdb_MovieLens_v1
    CORA_v1
)

METHODS_LIST=(
"bayesian_network ctgan ddpm nflow tvae"
"bayesian_network ctgan ddpm nflow tvae"
"bayesian_network ctgan ddpm nflow tvae"
"bayesian_network ctgan ddpm nflow tvae"
"ddpm"
"bayesian_network ctgan ddpm nflow tvae"
)

# List of run IDs
RUN_IDS=(
    1 
    2 
    3
)

# Loop over each dataset and run ID
for i in "${!DATASETS[@]}"
do
    DATASET=${DATASETS[$i]}
    METHODS=${METHODS_LIST[$i]}
    
    for RUN_ID in "${RUN_IDS[@]}"
    do
        # Build the method arguments
        METHOD_ARGS=""
        for METHOD in $METHODS
        do
            METHOD_ARGS+="-m $METHOD "
        done
        echo Evaluating dataset $DATASET, run-id $RUN_ID methods $METHOD_ARGS
        # Run the Python script with the dataset, run ID, and methods
        python experiments/evaluation/benchmark_single_table.py --dataset-name $DATASET --run-id $RUN_ID $METHOD_ARGS
    done
done