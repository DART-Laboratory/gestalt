# Mirage

Welcome to the Mirage repository. Here, we offer the implementation details of the methods introduced in our ongoing research titled "_Seeing Without Seeing: A Privacy-Aware Approach to System Intrusion Detection_".

## Prerequisites
To run Mirage you need to install Jupyter environment. More detailed instructions on installing and running Jupyter Notebooks can be found at this [Link](https://jupyter.org/install).

## Installation
We have provided a requirements.txt file detailing the specific dependency versions. Use the following command to install the required libraries.
```bash
pip install -r requirements.txt
```

## Datasets
Mirage is evaluated on open-source datasets from Darpa and the research community. You can access these datasets using the following links.

### Darpa OpTC
```bash
https://github.com/FiveDirections/OpTC-data
```

### Darpa E3
```bash
https://drive.google.com/drive/folders/1fOCY3ERsEmXmvDekG-LUUSjfWs6TRdp
```

### Darpa E5
```bash
https://drive.google.com/drive/folders/1okt4AYElyBohW4XiOBqmsvjwXsnUjLVf
```

## Code Structure
The parsers for each dataset are integrated within their respective Jupyter Notebooks. Every dataset has a dedicated Notebook designed for evaluation in the _Evaluation_scripts/_ directory. These Notebooks handle the downloading, parsing, and executing evaluations on their respective datasets. We have provided pre-trained model weights to run evaluations. Each notebook has parameters to control different components of the system. More detailed instructions are given in the Notebooks. After running these Notebooks, the results will be displayed at the end of each execution. Morevoer, all essential components for conducting ablation studies are provided in the `Ablation_studies_modules.ipynb`. It consists of multiple plug and play components whuch can be easily combined with any of the base script components under _Evaluation_scripts/_ to observe the effects across different datasets.

## Contributing
We welcome all feedback and contributions. If you wish to file a bug or enhancement proposal or have other questions, please use the Github Issue. If you'd like to contribute code, please open a Pull Request.

