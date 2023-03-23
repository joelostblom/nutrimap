# Nutrimap

## Installation

1. Clone this repo to your computer using `git clone git@github.com:joelostblom/nutrimap.git`
2. Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
3. Create a new environment from the environment file via `conda env create -f environment.yaml`
4. Switch to the new environment with `conda activate nutrimap`
5. Run the app with `panel serve nutrimap.py --autoreload --show`
    - You can edit the script `nutrimap.py` in your favorite IDE (VS Code, JupyterLab etc)
      and every time you save it, panel we update the page.
    - It can still be useful to have a notebook open from time to time,
      where you play around with new code and can easily see the output of each step.
