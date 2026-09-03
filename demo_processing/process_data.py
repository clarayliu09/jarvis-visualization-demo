import json

def process_trace(eta, prompt_id): 
  """Returns something like
  {
      "run_summary": {
          "eta": 
          "avg_tps": 
          "completion_time":
          "quality_score": 

      }
      "timed_data": [
          { 
              "time": 0.0,
              "token_num": 1,
              "token": "and",
              "tps": 0,
              "curr_avg_tps": 0
          }
          ...
      ]
  }
  """
  path = f"../results/eta_{eta}/timing_{prompt_id}.json"
  data = json.load(open(path))

  toks = data["token_times"] # toks is a list of dictionaries
  t0 = toks[0]["recv_time"] #set start time to receive time of first token
  t_prev = 0
  avg_tps = 0

  timed_data = []
  # loop through toks and put together timed_data containing time, token number, token, instantaneous toks/s, throughput
  for i,tk in enumerate(toks): # tk is a dictionary containing info abt token and timing
    time = tk["sent_time"] - t0
    token_num = i+1
    token = tk["token"]

    instant_tps = 1/(time - t_prev)
    avg_tps = token_num/time #aka the throughput

    timed_data.append({"time": time, "token_num": token_num, "token": token, "instant_tps": instant_tps, "avg_tps": avg_tps})

    t_prev = time


  quality_score = json.load(open(f"../results/eta_{eta}/ppl_results.json")).get("avg_utility")

  run_summary = {"eta": eta, "avg_tps": avg_tps, "completion_time": t_prev, "quality_score": quality_score}

  output = {"run_summary": run_summary, "timed_data": timed_data}

  return output


