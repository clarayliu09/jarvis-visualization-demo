# JARVIS Visualization Demo
An interactive visualization and replay dashboard for analyzing token generation performance.

This project was developed during my internship at Northeastern University. The demo uses results provided by the research team. These results are not included in this repository.

## Features
The project has two Streamlit applications:

### Single-run Replay
`demo/run_replay.py`

Replays a single run. 

### Multi-run Comparison
`demo/compare_runs.py`

Allows up to three runs to be displayed and replayed simultaneously

## Requirements
The demo requires the following Python packages:
* `streamlit`
* `matplotlib`
* `numpy`

Python's `json` and `time` libraries are also used

## Data organization
The code assumes that the processed demo data is stored in the following structure:
```bash
demo_metrics/
├── eta_0.1/
│   ├── metrics_1.json
│   ├── metrics_2.json
│   └── ...
├── eta_0.2/
├── ...
└── eta_1.0/
```
Each eta folder contains the processed metrics for that eta. Each metrics_N file corresponds to the metrics for prompt N

The `data_processing/` folder contains the code used to process the collected inference results into the files in `demo_metrics/`

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
