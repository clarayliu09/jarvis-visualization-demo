# JARVIS Visualization Demo
An interactive visualization and replay dashboard for analyzing token generation performance.

This project was developed during my internship at Northeastern University under the supervision of Professor Stratis Ioannidis. The demo uses data processed from the results provided by the research team.

## Features
The project has two Streamlit applications:

### Single-run Replay
`demo/run_replay.py`

Replays a single run. This was the first replay version I coded

### Multi-run Comparison (recommended)
`demo/compare_runs.py`

Allows up to three runs to be displayed and replayed simultaneously.

## Requirements
The demo requires the following Python packages:
* `streamlit`
* `matplotlib`
* `numpy`

### Installation
```bash
pip install streamlit matplotlib numpy
```

Python's `json`, `time`, and `os` libraries are also used

## Data organization
The code assumes that the data is stored in the following structure:
```bash
demo_metrics/
├── eta_0.1/
│   ├── metrics_1.json
│   ├── metrics_2.json
│   └── ...
├── eta_0.2/
├── ...
└── eta_1.0/
results/
├── eta_0.1/
│   ├── ppl.results.json
│   ├── prompt_1.txt
│   ├── response_1.txt
│   ├── timing_1.json
│   ├── ...
│   ├── prompt_7.txt
│   ├── response_7.txt
│   ├── timing_7.json
├── eta_0.2/
├── ...
└── eta_1.0/
```
Each eta folder in `demo_metrics/` contains the processed metrics for that eta. Each metrics_N file corresponds to the metrics for prompt N

## Running the Demo
From the project root directory:

### Single-run replay
```bash
streamlit run demo/run_replay.py
```

### Multi-run comparison
```bash
streamlit run demo/compare_runs.py
```
## Run processing code

The `demo_processing/` folder contains the code used to process the collected traces in `results/` into the files in `demo_metrics/`

To generate the demo metrics, run:
```bash
python demo_processing/run_processing.py
```

### Adding more prompts
To process additional prompts, add the prompt number to the prompts list in `demo_processing/run_processing.py` and update the NUM_PROMPTS variable in the demo code

Make sure the corresponding timing, prompt, and response files exist in each `results/eta_<eta>/` directory


## Acknowledgements
We gratefully acknowledge support from the National Science Foundation (grant 2112471).