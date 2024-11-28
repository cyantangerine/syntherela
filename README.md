# SyntheRela - Synthetic Relational Data Generation Benchmark

<h2 align="center">
    <img src="https://raw.githubusercontent.com/martinjurkovic/syntherela/refs/heads/main/docs/SyntheRela.png" height="150px">
    <div align="center">
      <a href="https://pypi.org/project/syntherela/">
        <img src="https://img.shields.io/pypi/v/syntherela" alt="PyPI">
      </a>
      <a href="https://github.com/martinjurkovic/syntherela/blob/main/LICENSE">
        <img alt="MIT License" src="https://img.shields.io/badge/License-MIT-yellow.svg">
      </a>
      <a href="https://arxiv.org/abs/2410.03411">
        <img alt="Paper URL" src="https://img.shields.io/badge/cs.DB-2410.03411-B31B1B.svg">
      </a>
      <a href="https://pypi.org/pypi/syntherela/">
        <img src="https://img.shields.io/pypi/pyversions/syntherela" alt="PyPI pyversions">
      </a>
  </div>
</h2>

Our paper **Benchmarking the Fidelity and Utility of Synthetic Relational Data** is available on [arxiv](https://arxiv.org/abs/2410.03411).

## Installation
To install only the benchmark package, run the following command:

```bash
pip install syntherela
```

## Replicating the paper's results
We divide the reproducibility of the experiments into two parts: the generation of synthetic data and the evaluation of the generated data. The following sections describe how to reproduce the experiments for each part.
> To reproduce some of the figures the synthetic data needs to be downloaded first. The tables can be reproduced with the results provided in the repository or by re-running the benchmark.

First, create a .env file in the root of the project with the path to the root of the project. Copy `.env.example`, rename it to `.env` and update the path.

### Download synthetic data and results

The data and results can be downloaded and extracted with the below script, or are available on [google drive here](https://drive.google.com/drive/folders/1L9KarR20JqzU0p8b3G_KU--h2b8sz6ky).

```bash
conda activate reproduce_benchmark
./experiments/reproducibility/download_data_and_results.sh
```

### Evaluation of synthetic data
To run the benchmark and get the results of the metrics, run:

```bash
conda activate reproduce_benchmark
./experiments/reproducibility/evaluate_relational.sh

./experiments/reproducibility/evaluate_tabular.sh

./experiments/reproducibility/evaluate_utility.sh
```

### Generation of synthetic data
Depending on the synthetic data generation method a separate pythone environment is needed. The instruction for installing the required environment for each method is provided in [docs/INSTALLATION.md](/docs/INSTALLATION.md).

After installing the required environment, the synthetic data can be generated by running the following commands:

```bash
conda activate reproduce_benchmark
./experiments/reproducibility/generation/generate_sdv.sh

conda activate rctgan
./experiments/reproducibility/generation/generate_rctgan.sh

conda activate realtabformer
./experiments/reproducibility/generation/generate_realtabformer.sh

conda activate tabular
./experiments/reproducibility/generation/generate_tabular.sh

conda activate gretel
# The method requires a separate connection-uid for each dataset see the README for more information
python experiments/generation/gretel/generate_gretel.py --connection-uid  <connection-uid> --model lstm
python experiments/generation/gretel/generate_gretel.py --connection-uid  <connection-uid> --model actgan

conda activate mostlyai
./experiments/reproducibility/generation/generate_mostlyai.sh <api-key>

cd experiments/generation/clavaddpm
./generate_clavaddpm.sh <dataset-name> <real-data-path> <synthetic-data-path>  
```

To generate data with MOSTLYAI, insructions are provided in [experiments/generation/mostlyai/README.md](experiments/generation/mostlyai/README.md). <br>
Further instructions for GRETELAI are provided in [experiments/generation/gretel/README.md](experiments/generation/gretel/README.md).

### Visualising Results
To visualize results, after running the benchmark you can run the below script. The figures will be saved to `results/figures/`:
```bash
conda activate reproduce_benchmark
./experiments/reproducibility/generate_figures.sh
```
### Reproducing Tables
To reproduce the tables you can run the below script. The tables will be saved as .tex files in `results/tables/`:
```bash
conda activate reproduce_benchmark
./experiments/reproducibility/generate_tables.sh
```

## Adding a new metric
The documentation for adding a new metric can be found in [docs/ADDING_A_METRIC.md](/docs/ADDING_A_METRIC.md).

## Synthetic Data Methods
### Open Source Methods
- SDV: [The Synthetic Data Vault](https://ieeexplore.ieee.org/document/7796926)
- RCTGAN: [Row Conditional-TGAN for Generating Synthetic Relational Databases](https://ieeexplore.ieee.org/abstract/document/10096001)
- REaLTabFormer: [Generating Realistic Relational and Tabular Data using Transformers](https://arxiv.org/abs/2302.02041)
- ClavaDDPM: [Multi-relational Data Synthesis with Cluster-guided Diffusion Models](https://arxiv.org/html/2405.17724v1)
- IRG: [Generating Synthetic Relational Databases using GANs](https://arxiv.org/abs/2312.15187)
- [Generating Realistic Synthetic Relational Data through Graph Variational Autoencoders](https://arxiv.org/abs/2211.16889)*
- [Generative Modeling of Complex Data](https://arxiv.org/abs/2202.02145)*
- BayesM2M & NeuralM2M: [Synthetic Data Generation of Many-to-Many Datasets via Random Graph Generation](https://iclr.cc/virtual/2023/poster/10982)*


\* Denotes the method does not have a public implementation available.

### Commercial Providers
A list of commercial synthetic relational data providers is available in [docs/SYNTHETIC_DATA_TOOLS.md](/docs/SYNTHETIC_DATA_TOOLS.md).

## Conflicts of Interest
The authors declare no conflict of interest and are not associated with any of the evaluated commercial synthetic data providers.

## Citation
If you use SyntheRela in your work, please cite our paper:
```
@misc{hudovernik2024benchmarkingsyntheticrelationaldata,
      title={Benchmarking the Fidelity and Utility of Synthetic Relational Data}, 
      author={Valter Hudovernik and Martin Jurkovič and Erik Štrumbelj},
      year={2024},
      eprint={2410.03411},
      archivePrefix={arXiv},
      primaryClass={cs.DB},
      url={https://arxiv.org/abs/2410.03411}, 
}
```
