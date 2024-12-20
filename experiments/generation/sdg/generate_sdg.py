import os
import sys
import logging
import argparse
from pathlib import Path
import pandas as pd

# from sdv.multi_table import HMASynthesizer
from syntherela.metadata import Metadata
from syntherela.data import load_tables, save_tables, remove_sdv_columns

MODEL_NAME = "SDG"

args = argparse.ArgumentParser()
args.add_argument("--dataset-name", type=str, default="airbnb-simplified_subsampled")
args.add_argument("--real-data-path", type=str, default="data/original")
args.add_argument("--synthetic-data-path", type=str, default="data/synthetic")
args.add_argument("--model-save-path", type=str, default="checkpoints")
args.add_argument("--run-id", type=str, default="1")
args = args.parse_args()

dataset_name = args.dataset_name

# TODO Biodegradability_v1 的bond有数据为空(因为训练的时候outerjoin，自然就有)，但不应该有。

# dataset_name = 'imdb_MovieLens_v1'
# dataset_name = '''    airbnb-simplified_subsampled
#     Biodegradability_v1
#     CORA_v1
#     imdb_MovieLens_v1
#     rossmann_subsampled
#     walmart_subsampled'''.split("\n")[5].strip()

real_data_path = args.real_data_path
synthetic_data_path = args.synthetic_data_path
model_save_path = args.model_save_path
run_id = args.run_id

logger = logging.getLogger(f"{MODEL_NAME}_logger")

logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.info(f"START LOGGING DATASET {dataset_name} RUN {run_id}...")


logger.debug("Loading real data...")
metadata = Metadata().load_from_json(
    Path(real_data_path) / f"{dataset_name}/metadata.json"
)

if dataset_name == "Biodegradability_v1":
    metadata.update_column(
        "bond", "type", sdtype="numerical", computer_representation="Int64"
    )

real_data = load_tables(Path(real_data_path) / f"{dataset_name}", metadata)
real_data, metadata = remove_sdv_columns(real_data, metadata)
metadata.validate_data(real_data)
logger.debug("Real data loaded")


synthetic_data = {}

# GENERATE SYNTHETIC DATA ---------------------------------
from multi_pca_rfe_ctgan import MultiTable_PCA_CTGAN
from testcode.Xargs import XMetaBuilder
from generate_join_keys import generate_xargs
total_length = max([len(item) for item in real_data.values()])
tables = real_data

table_names_mapper, x_args = generate_xargs(metadata=metadata, dataset_name=dataset_name, logger=logger)

for tbn in table_names_mapper.keys():
    tables[tbn] = pd.DataFrame(tables[tbn]).rename(
        columns=table_names_mapper[tbn]
    )

logger.info(f"X_args for {dataset_name}: {x_args}")

model = MultiTable_PCA_CTGAN(db_path=None, x_args=x_args, exclude_processor=['specificcombinationtransformer', 'fixedcombinationtransformer'], tables=tables)
model.init(meta_builder=XMetaBuilder(x_args), add_cols_num=0)
model.fit()


# SAVE MODEL CHECKPOINT -----------------------------------
# logger.debug("Saving model checkpoint...")
# model_path = os.path.join(model_save_path, MODEL_NAME, dataset_name)
# os.makedirs(model_path, exist_ok=True)
# model_path = os.path.join(model_path, f"model_{run_id}.pkl")
# model.save(model_path)

# SAMPLE AND SAVE DATA ------------------------------------
logger.info("Sampling and saving synthetic data...")

reverse_mapper = {
    tbn: {
        v: k for k, v in va.items()
    } for tbn,va in table_names_mapper.items()
}

for i in range(1, 4):
    logger.debug(f"Sampling sample {i}")
    # model.seed = i
    synthetic_data = model.sample(total_length)
    save_data_path = (
        Path(synthetic_data_path) / dataset_name / MODEL_NAME / run_id / f"sample{i}"
    )
    
    for tbn in reverse_mapper.keys():
        synthetic_data[tbn] = pd.DataFrame(synthetic_data[tbn]).rename(
            columns=reverse_mapper[tbn]
        )
    
    save_tables(synthetic_data, save_data_path)
    logger.debug(f"Done! Sample {i} saved!")


logger.info(f"{dataset_name} COMPLETE GENERATION DONE.")
