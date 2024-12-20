# imdb_MovieLens_v1
DATASETS=(
    airbnb-simplified_subsampled
    Biodegradability_v1
    CORA_v1
    rossmann_subsampled
    walmart_subsampled
)

RUN_IDS=(
    1 
    2 
    3
)

for DATASET in ${DATASETS[@]}
do
    echo "" > SDG_$DATASET.log
    for RUN_ID in ${RUN_IDS[@]}
    do
        python experiments/generation/sdg/generate_sdg.py --dataset-name $DATASET --run-id $RUN_ID 2>&1 | tee -a SDG_$DATASET.log
    done
done