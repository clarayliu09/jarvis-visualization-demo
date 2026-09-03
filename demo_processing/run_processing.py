import json
import os
from demo_processing.process_data import process_trace

etas = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]
prompts = [1,2,3,4,5,6,7]

for eta in etas:
  for prompt in prompts:
    output = process_trace(eta, prompt)

    path = f"../demo_metrics/eta_{eta}/metrics_{prompt}.json"

    # ensure that path exists
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, 'w') as file:
      json.dump(output, file, indent=2)


"""
eventual file structure:

demo_metrics
    eta_0.1
        metrics_1   #metrics for prompt 1
        metrics_2
        ...
    eta_0.2
        metrics_1
        metrics_2
        ...
    ...

"""