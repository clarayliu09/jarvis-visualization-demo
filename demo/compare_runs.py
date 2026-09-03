import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import json
import time

st.set_page_config(
  page_title="Demo",
  layout="wide"
)

ETAS = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]
PROMPTS = []
NUM_PROMPTS = 7
COLORS = ("#4285F4", "#34A853", "#F9AB00")

# loading prompts 
def strip_prompt(text): # took this from combined_demo.py
  t = text.split("user", 1)[1] if "user" in text else text
  return t.split("<end_of_turn>")[0].replace("\\n", " ").strip()

for i in range(1,NUM_PROMPTS+1):
  path = f"results/eta_1.0/prompt_{i}.txt"
  with open(path, "r") as file:
    prompt = strip_prompt(file.read())
  PROMPTS.append(prompt)

# CSS STYLING 
st.markdown(
"""
<style>

  /* hide top default header */
  [data-testid="stHeader"] {
    background: transparent;
    display: none;
  }

  .block-container {
    max-width: 100%;
    padding-left: 1rem;
    padding-right: 1rem;
    padding-top: 0.1rem;
    padding-bottom:1rem;
  }

  .st-key-top_bar{
    padding-top: 7px;
    padding-bottom:7px;
    background-color: #f5f5f5;
  }

  .st-key-top_bar label p{
    font-size 15px;
    color:#555555;
  }

  .st-key-run_summary{
    padding-top:5px;
    background-color: #f5f5f5
  }

  .st-key-live_replay_0{
    padding-top:5px;
    background-color: #f5f5f5;
  }
  .st-key-live_replay_1{
    padding-top:5px;
    background-color: #f5f5f5;
  }
  .st-key-live_replay_2{
    padding-top:5px;
    background-color: #f5f5f5;
  }

  .st-key-run_eta_0{
    margin-top: -40px;
  }

  .st-key-run_eta_1{
    margin-top: -40px;
  }

  .st-key-run_eta_2{
    margin-top: -40px;
  }

  .st-key-add_run_button{
    font-size: 10px;
    margin-top: -12px;
  }


  .st-key-live_metrics{
    padding-top:5px;
    background-color: #f5f5f5
  }     

  .metrics-cell{
    font-size:14px;
    padding-bottom: 10px;
  }

  /* styling for metric cards */
  .metric-card{
    padding-bottom: 15px;
    text-align: center;
  }

  .metric-title{
    font-size:15px;
    line-height: 16px;
  }

  .metric-unit{
    font-size:10px;
    margin-top: -5px;
  }
  
  /* styling for comparison cards */
  .comparison-card{
    padding: 0px;
    text-align: center;
    margin-top: -12px;
    font-size:15px;
  }

  .comparison-value{
    font-size:20px;
    font-weight:600;
  }

  .comparison-text{
    margin-top: -5px;
    line-height: 1;
    font-size:10px;
  }

  .st-key-container_0 {
    padding: 20px;
    border-radius: 10px;
    border-color: #4285F4;
  }

  .st-key-container_1 {
    padding: 20px;
    border-radius: 10px;
    border-color: #34A853;
  }

  .st-key-container_2 {
    padding: 20px;
    border-radius: 10px;
    border-color: #F9AB00;
  }

</style>
""", unsafe_allow_html=True)


# Session states (are not redefined every rerun)
if "playing" not in st.session_state:
  st.session_state.playing = False

if "start_time" not in st.session_state:
  st.session_state.start_time = None

if "elapsed_sim" not in st.session_state:
  st.session_state.elapsed_sim = 0.0

if "all_complete" not in st.session_state:
  st.session_state.all_complete = False

if "speedo" not in st.session_state:
  st.session_state.speedo = 1

# Remember which prompt/etas belongs to the current loaded runs
if "run_etas" not in st.session_state:
  st.session_state.run_etas = [0.1]

if "run_prompt_id" not in st.session_state:
  st.session_state.run_prompt_id = None

# Loaded data
if "timed_data" not in st.session_state:
  st.session_state.timed_data = []

if "run_summary_data" not in st.session_state:
  st.session_state.run_summary_data = []

if "total_toks" not in st.session_state:
  st.session_state.total_toks = []

# per-run details
if "tok_inds" not in st.session_state:
  st.session_state.tok_inds = []

if "replay_texts" not in st.session_state:
  st.session_state.replay_texts = []

if "run_complete" not in st.session_state:
  st.session_state.run_complete = []

if "completion_times" not in st.session_state:
  st.session_state.completion_times=[]

def clear_loaded_run():
  """Clears the currently displayed run data and playback state but keeps the user's prompt and etas."""

  st.session_state.playing = False
  st.session_state.start_time = None
  st.session_state.elapsed_sim = 0.0

  st.session_state.timed_data = []
  st.session_state.run_summary_data = []
  st.session_state.total_toks = []

  st.session_state.tok_inds = []
  st.session_state.replay_texts = []
  st.session_state.run_complete = []
  st.session_state.completion_times=[]

  st.session_state.run_prompt_id = None
  st.session_state.all_complete = False

# HELPER FUNCTIONS 
def reset_replay():
  """Clears loaded data and resets the run configuration back to one run"""
  clear_loaded_run()

  st.session_state.run_etas = [0.1]

def load_runs():
  """Loads the selected runs and stores their data in lists"""
  prompt = st.session_state.prompt_selector
  etas = st.session_state.run_etas

  prompt_id = PROMPTS.index(prompt)+1
  st.session_state.run_prompt_id = prompt_id

  # clear any previously loaded runs
  st.session_state.timed_data = []
  st.session_state.run_summary_data = []
  st.session_state.total_toks = []

  st.session_state.tok_inds = []
  st.session_state.replay_texts=[]
  st.session_state.run_complete = []
  st.session_state.completion_times=[]

  # Load all selected eta
  for eta in etas:
    path = f"demo_metrics/eta_{eta}/metrics_{prompt_id}.json"

    with open(path, "r") as file:
      metrics = json.load(file)
      
    st.session_state.timed_data.append(metrics["timed_data"])
    st.session_state.run_summary_data.append(metrics["run_summary"])
    st.session_state.total_toks.append(len(metrics["timed_data"]))

    st.session_state.tok_inds.append(0)
    st.session_state.replay_texts.append("")
    st.session_state.run_complete.append(False)
    st.session_state.completion_times.append(None)

def toggle_play():
  """Controls pause/play behvavior. Is called when play button is pressed"""
  if st.session_state.playing: 
    # Pausing a run
    secs_passed = time.time()-st.session_state.start_time #elapsed time of this stretch of the run
    st.session_state.elapsed_sim += st.session_state.speedo * secs_passed
    #st.session_state.elapsed_sim += secs_passed
    st.session_state.playing = False
    return
  
  # if play is pressed after the demo is complete - starts the comparison again with the same etas and prompt
  if st.session_state.all_complete:
    clear_loaded_run()

  # If no runs have been loaded yet, load them now
  if len(st.session_state.timed_data) == 0:
    load_runs()

  # Play/resume
  st.session_state.start_time = time.time()
  st.session_state.playing = True

def update_metric(placeholder, value, unit, color="#31333f"):
  """Updates a live metric card"""
  placeholder.markdown(
    f"""
    <div class="metric-card">
      <div class="metric-value" style="font-size:24px; font-weight:600; color:{color};">{value}</div>
      <div class="metric-unit">{unit}</div>
    </div>
    """,
    unsafe_allow_html=True
  )

def update_elapsed(placeholder, title, value, unit):
  """Updates the elapsed time card"""
  placeholder.markdown(
    f"""
    <div class="metric-card">
      <div class="metric-title">{title}</div>
      <div class="metric-value" style="font-size:24px; font-weight:600; color:#31333f";">{value}</div>
      <div class="metric-unit">{unit}</div>
    </div>
    """,
    unsafe_allow_html=True
  )

def update_comparison_card(placeholder, value, text):
  value_style = ''

  if (not value == "N/A"):
    if (value<1):
      is_less_than_1 = True
    else:
      is_less_than_1 = False

    # apply different colors depending on what the text is
    if text == "Faster generation":
      value = f"{value}x"

      if is_less_than_1:
        value_style = 'style="color: red;"'
      else:
        value_style = 'style="color: green;"'

    elif text == "Quality difference":

      #Apply red if both conditions are met
      if is_less_than_1:
        value_style = 'style="color: red;"'
      else:
        value_style = 'style="color: green;"'

    elif text == "Completion seconds":
      if (value<0):
        green = True
      else:
        green = False

      if green:
        value_style = 'style="color: green;"'
      else:
        value_style = 'style="color: red;"'

  placeholder.markdown(
    f"""
    <div class="comparison-card">
      <div class="comparison-value" {value_style}>{value}</div>
      <div class="comparison-text">{text}</div>
    </div>
    """,
    unsafe_allow_html=True
  )

def format_time(seconds):
  """formats time in seconds to readable format minutes:seconds:milliseconds"""
  mins = int(seconds/60)
  secs = int(seconds%60)
  ms = int((seconds%1) * 1000)

  return f"{mins:02}:{secs:02}:{ms:03}"


def top_bar():

  # disable changing configuration after a run has been loaded
  config_locked = st.session_state.playing or len(st.session_state.timed_data) > 0

  # prevents user from changing speed if a run is unfinished
  speedo_locked = st.session_state.playing or (st.session_state.elapsed_sim != 0.0 and not st.session_state.all_complete)

  with st.container(border=True, height="stretch", key="top_bar"):

    prompt_col, compression_col, speedo_col, button_col = st.columns(
      [2.5,1.5,0.8,1.2], # sizes of columns
      gap="medium",
      vertical_alignment="center"
    )

    with prompt_col:
      prompt = st.selectbox(
        label="Select prompt",
        options = PROMPTS,
        key="prompt_selector",
        disabled = config_locked
      )

    with compression_col:
      st.markdown(
        f"""<p style='
          font-size:14px; 
        '>
          Add runs (max 3)
        </p>""",
        unsafe_allow_html=True
      ) 

      cols = st.columns(3)

      # Allow user to manually select runs
      for i, eta in enumerate(st.session_state.run_etas):

        with cols[i]:
          eta = st.selectbox(
            label = "eta",
            options = ETAS,
            index=ETAS.index(eta),
            key=f"run_eta_{i}",
            label_visibility = "hidden",
            disabled = config_locked #disables the button if config_locked is true
          )
          st.session_state.run_etas[i] = eta

      # "Add Run" button appears after existing runs
      if len(st.session_state.run_etas) < 3 and not config_locked:
        with cols[len(st.session_state.run_etas)]: #eg: if len = 0, first column is filled
          if st.button(
            label= "Add run", 
            type="secondary", 
            key="add_run_button"
          ):
            # Preserve the current speed before changing the layout
            curr_speed = st.session_state.speedo 
            
            # add a new run
            st.session_state.run_etas.append(0.1) 

            # set speedup to the current speed indicated before run was added
            st.session_state.speedo = curr_speed

            st.rerun()

    with speedo_col:

      st.select_slider(
        label="Select speed",
        options=[1,2,3,4,5,6,7,8,9,10],
        key="speedo",
        label_visibility="hidden",
        disabled=speedo_locked
      )

      st.markdown(
        f"""<p style='
          text-align:center; 
          font-size:12px; 
          color: #4285F4; 
          font-weight: 600;
          margin-top:-40px;
        '>
          {st.session_state.speedo}x speed
        </p>""",
        unsafe_allow_html=True
      )

    with button_col:

      with st.container(horizontal=True):
        
        button_label = "Pause" if st.session_state.playing else "Play"

        st.button(
          label = button_label,
          on_click=toggle_play,
          type = "primary",
          width=90
        )
        
        st.button(
          label="Reset",
          on_click=reset_replay,
          type="primary",
          width=90
        )

  return prompt

prompt = top_bar()
prompt_id = PROMPTS.index(prompt)+1
num_runs = len(st.session_state.run_etas)

# initializing lists to store metric values
tok_nums = [0] * num_runs
instant_tps = [0.0] * num_runs
avg_tps = [0.0] * num_runs

# only access timed data if all selected runs have been loaded
if len(st.session_state.timed_data) == num_runs:

  # display the metrics from the most recently generated token
  for i in range(num_runs):

    timed_data_i = st.session_state.timed_data[i]

    # If at least one token has already been generated, display the previous token's metrics
    if len(timed_data_i)>0 and st.session_state.tok_inds[i]>0:

      prev_tok = timed_data_i[st.session_state.tok_inds[i]-1]
      tok_nums[i] = prev_tok["token_num"]
      instant_tps[i] = round(prev_tok["instant_tps"], 2)
      avg_tps[i] = round(prev_tok["avg_tps"], 2)



# DISPLAYED ELAPSED TIME
if st.session_state.playing:
  secs_passed = time.time() - st.session_state.start_time
  displayed_elapsed = st.session_state.elapsed_sim + st.session_state.speedo * secs_passed
else:
  # elapsed time when run hasn't started or has already ended
  displayed_elapsed = st.session_state.elapsed_sim


# main layout 
replay_col, metrics_col = st.columns([1.5,1], gap="small")

# stores replay texts and progress bars so they can be updated later
replay_text_placeholders = []
progress_bars = []

with replay_col:
  
  for i, eta in enumerate(st.session_state.run_etas):
    
    color = COLORS[i]

    percent_compressed = round(100 * (1.0 - eta))

    with st.container(
      border=True, 
      height="stretch", 
      key=f"live_replay_{i}"
    ):

      st.markdown(
        f"<h3>LIVE REPLAY: <span style='color:{color};'>η = {eta} ({percent_compressed}% compressed)</span></h3>", 
        unsafe_allow_html=True
      )

      with st.container(
        border=True, 
        height = "stretch", 
        key=f"replay_text_box_{i}"
      ):
        
        replay_text_placeholder = st.empty()

        # if this run has been loaded, display its current replay text
        if i < len(st.session_state.replay_texts):
          replay_text_placeholder.write(st.session_state.replay_texts[i])

        else:
          replay_text_placeholder.write("")

      # progress bar
      if i < len(st.session_state.total_toks):

        total = st.session_state.total_toks[i]
        
        progress = tok_nums[i] / total if total != 0 else 0
        progress_bar = st.progress(progress, text=f"Tokens generated: {tok_nums[i]}/{total}")

      else:
        progress_bar = st.progress(0, text=f"Tokens generated: 0/0")

      # save the placeholders
      replay_text_placeholders.append(replay_text_placeholder) 
      progress_bars.append(progress_bar)



# LIVE METRICS

# 4 metric placeholders per run: 
# (current tps, avg tps, generated tokens, completion time)
metric_placeholders = []

with metrics_col:
  with st.container(border=True, height="stretch", key="live_metrics"):
    st.subheader("PROMPT:")
    st.write(prompt)

    st.subheader("LIVE METRICS")


    # ELAPSED TIME CONTAINER
    with st.container(border = True):
      elapsed_placeholder = st.empty()

      update_elapsed(
        elapsed_placeholder,
        "Elapsed time",
        format_time(displayed_elapsed),
        "mm:ss:ms"
      )

    # header columns
    header = st.columns([1, 1.3, 1.3, 1, 1.3], vertical_alignment="center")

    # table headers
    headers = [
      "η",
      "Current tokens/s",
      "Average tokens/s",
      "Generated tokens",
      "Completion time"
    ]

    for col, title in zip(header, headers):
      with col:
        st.markdown(
          f'<div class="metrics-cell"><p style="text-align: center; margin-bottom:0px; line-height: 18px;"><b>{title}</b></p></div>',
          unsafe_allow_html=True
        )

    # PER RUN METRICS
    for i, eta in enumerate(st.session_state.run_etas):
      
      run_complete = False
      if len(st.session_state.run_complete) == len(st.session_state.run_etas):
        run_complete = st.session_state.run_complete[i]

      color = COLORS[i] #color associated with this run

      row = st.columns([0.9, 1.3, 1.3, 1, 1.3], border=True)
      
      with row[0]:
        st.markdown(f'<p style="text-align: center; margin-top: 10px;"><b>{eta}</b></p>', unsafe_allow_html=True)

      with row[1]:
        instant_tps_placeholder = st.empty() 
        # freezes the instant_tps at 0.0 if the run is complete, otherwise shows the current instant_tps
        update_metric(instant_tps_placeholder,instant_tps[i] if not run_complete else 0.0,"tokens/s", color)

      with row[2]:
        avg_tps_placeholder = st.empty()
        update_metric(avg_tps_placeholder,avg_tps[i],"tokens/s", color)

      with row[3]:
        token_num_placeholder = st.empty()
        update_metric(token_num_placeholder,tok_nums[i],"tokens", color)

      with row[4]:
        completion_time_placeholder = st.empty()

        completion_time = st.session_state.completion_times[i] if i<len(st.session_state.completion_times) else None

        update_metric(completion_time_placeholder, f"{completion_time:.2f}" if completion_time is not None else "--", "seconds", color)

      # adds a list of metrics for each run that can be updated later
      metric_placeholders.append((instant_tps_placeholder, avg_tps_placeholder, token_num_placeholder, completion_time_placeholder))




# REPLAY LOGIC
if st.session_state.playing: 

  # shared clock
  real_elapsed = time.time() - st.session_state.start_time #how many actual seconds have passed since run was started/resumed
  sim_time = st.session_state.elapsed_sim + st.session_state.speedo * (real_elapsed)
  
  # update shared elapsed time
  update_elapsed(
    elapsed_placeholder,
    "Elapsed time",
    format_time(sim_time),
    "mm:ss:ms"
  ) 

  #loop through all etas and make sure each run is caught up to the simulation time
  for i in range(num_runs):

    color = COLORS[i]

    timed_data_i = st.session_state.timed_data[i]
    tok_ind = st.session_state.tok_inds[i]
    total_toks_i = st.session_state.total_toks[i]

    # catch up on "overdue" tokens up to the current simulation time
    while(tok_ind < total_toks_i and timed_data_i[tok_ind]["time"] <= sim_time): 

      tok_data = timed_data_i[tok_ind]
      tok_num = tok_data["token_num"]
      token = tok_data["token"]

      # UPDATE REPLAY TEXT
      st.session_state.replay_texts[i]+=token
      replay_text_placeholders[i].write(st.session_state.replay_texts[i])

      # UPDATE METRICS
      (instant_tps_placeholder, avg_tps_placeholder, token_num_placeholder, completion_time_placeholder) = metric_placeholders[i]

      update_metric(instant_tps_placeholder, round(tok_data["instant_tps"],2),"tokens/s", color)
      update_metric(avg_tps_placeholder, round(tok_data["avg_tps"],2),"tokens/s", color)
      update_metric(token_num_placeholder, tok_num,"tokens", color)

      # UPDATE PROGRESS BAR
      percent_complete = tok_num/total_toks_i if total_toks_i != 0 else 0
      progress_bars[i].progress(percent_complete, text=f"Tokens generated: {tok_num}/{total_toks_i}")
      
      # move to next token
      tok_ind += 1 

    # save updated token index
    st.session_state.tok_inds[i] = tok_ind
      
    # check if this run is complete - freezes instant tps at zero if so
    if tok_ind >= total_toks_i:
      st.session_state.run_complete[i] = True

      # store completion time for this run
      if st.session_state.completion_times[i] is None:
        st.session_state.completion_times[i] = timed_data_i[tok_ind-1]["time"]

      (instant_tps_placeholder, avg_tps_placeholder, token_num_placeholder, completion_time_placeholder) = metric_placeholders[i]
      update_metric(instant_tps_placeholder,0.0,"tokens/s", color)
      update_metric(completion_time_placeholder, f"{st.session_state.completion_times[i]:.2f}","seconds", color)

  # check of all runs are complete 
  if all(st.session_state.run_complete):

    st.session_state.playing=False
    st.session_state.all_complete = True
    st.session_state.elapsed_sim = sim_time #note: simulation time is not exactly equal to the time that the last run finishes at
    st.rerun()

  else:
    time.sleep(0.01)

    #keep the replay moving - goes to top of script 
    st.rerun()



# RUN SUMMARY
with st.container(border=True, height="stretch", key="run_summary"):
  st.subheader("RUN SUMMARY")

  # check of the run is complete and summaries are loaded
  summaries_ready = (st.session_state.all_complete and len(st.session_state.run_summary_data) == num_runs)

  # calculate summaries
  if summaries_ready:
    
    # load metrics for eta1.0
    summary1_0 = json.load(open(f"demo_metrics/eta_1.0/metrics_{prompt_id}.json"))["run_summary"] 

    stats_col, graph_col = st.columns([1.5,1], gap="small")

    with stats_col:

      # one for each eta
      for i in range(num_runs):

        summary_data = st.session_state.run_summary_data[i]

        eta = summary_data["eta"]
        avg_tps = round(summary_data["avg_tps"],2)
        completion_time = round(summary_data["completion_time"],2)
        quality_score = summary_data["quality_score"]

        # Compare against eta=1.0
        speed_factor = round(avg_tps/summary1_0["avg_tps"], 2) 
        time_diff = round(completion_time-summary1_0["completion_time"],1)
        quality_diff = round(quality_score - summary1_0["quality_score"],2)

        with st.container(border=True, height="stretch", horizontal=False, vertical_alignment = "center", key=f"container_{i}"):
          
          with st.container(horizontal=True, horizontal_alignment = "center"):

            with st.container():
              placeholder1 = st.empty()
              update_metric(placeholder1, eta, "Compression (η)", COLORS[i])

              if eta != 1.0:
                st.markdown('<p style="font-size:12px; text-align:center; line-height:12px;"><b>Compared to no compression (η=1.0):</b></p>', unsafe_allow_html=True)

            with st.container():
              placeholder2 = st.empty()
              update_metric(placeholder2,f"{avg_tps} toks/s", "Average tokens/s", COLORS[i])

              if eta != 1.0:
                placeholder5 = st.empty()
                update_comparison_card(placeholder5, speed_factor, "Faster generation")
            
            with st.container():
              placeholder3 = st.empty()
              update_metric(placeholder3, f"{completion_time} s", "Completion time", COLORS[i])

              if eta != 1.0:
                placeholder6 = st.empty()
                update_comparison_card(placeholder6, time_diff, "Completion seconds")
            
            with st.container():
              placeholder4 = st.empty()
              update_metric(placeholder4, f"{quality_score}", "Quality score", COLORS[i])

              if eta != 1.0:
                placeholder7 = st.empty()
                update_comparison_card(placeholder7, quality_diff, "Quality difference")


      # Position for graph
      with graph_col:
        with st.container(border=False, height="stretch"):

          fig, ax = plt.subplots(figsize=(7,6))
          yticks = None
          max_toks = 0
          
          # loop through all etas and add their values to the graph
          for i,eta in enumerate(st.session_state.run_etas):
            timed_data_i = st.session_state.timed_data[i]  
            color_i = COLORS[i]

            # x-axis: time
            # y-axis: token #
            x = [tok["time"] for tok in timed_data_i]
            y = [tok["token_num"] for tok in timed_data_i]

            #ax.plot(x,y,label=f"η = {eta}", color=color_i)
            plt.plot(x, y, marker='o', markersize=3, linestyle='-', label=f"η = {eta}", color=color_i)

            yticks = np.arange(max(max_toks, len(timed_data_i)+1))
          

          ax.set_xlabel("time (s)")
          ax.set_ylabel("token number")
          ax.set_title("total tokens generated vs time")

          ax.set_yticks(yticks)

          ax.legend()
          st.pyplot(fig)
  
  else:
    # The runs haven't been completed yet
    st.write("Run replay to generate summary.")
    with st.container(height = 125, border = False):
      st.empty()


