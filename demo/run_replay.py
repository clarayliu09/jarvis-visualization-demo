"""
Demo for one-run replays

"""


import streamlit as st
import json
import time

st.set_page_config(
  page_title="JARVIS Demo",
  layout="wide"
)

ETAS = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]
PROMPTS = []

def strip_prompt(text): # took this from combined_demo.py
  t = text.split("user", 1)[1] if "user" in text else text
  return t.split("<end_of_turn>")[0].replace("\\n", " ").strip()

for i in range(1,8):
  path = f"results/eta_1.0/prompt_{i}.txt"
  with open(path, "r") as file:
    prompt = strip_prompt(file.read())
  PROMPTS.append(prompt)

st.markdown(
"""
<style>

  /* hide top default header */
  [data-testid="stHeader"] {
    background: transparent;
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

  .st-key-compression_slider label p{
    margin-bottom:-12px;
  }

  .st-key-run_summary{
    padding-top:5px;
    background-color: #f5f5f5
  }

  .st-key-live_replay{
    padding-top:5px;
    background-color: #f5f5f5;
  }

  .st-key-live_metrics{
    padding-top:5px;
    background-color: #f5f5f5
  }     

  /* styling for metric cards */
  .metric-card{
    padding: 4px 8px;
    text-align: center;
    min-height: 110px;
  }

  .metric-value{
    font-size:24px;
    font-weight:600;
    color:#4285F4;
  }

  .metric-unit{
    font-size:12px;
  }
  
   /* styling for summary cards */
  .summary-card{
    padding: 0px;
    text-align: center;
    margin-top: -10px;
    font-size:15px;
  }

  .summary-text{
    font-size:20px;
    font-weight:600;
    color:black;
    margin-top: -5px
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
    margin-top: -7px;
    line-height: 1;
  }

</style>
""", unsafe_allow_html=True)

if "playing" not in st.session_state:
  st.session_state.playing = False

if "start_time" not in st.session_state:
  st.session_state.start_time = None

if "elapsed" not in st.session_state:
  st.session_state.elapsed = 0.0

if "tok_ind" not in st.session_state:
  st.session_state.tok_ind = 0

if "replay_text" not in st.session_state:
  st.session_state.replay_text = ""

if "run_complete" not in st.session_state:
  st.session_state.run_complete = False

# Data for loaded run
if "timed_data" not in st.session_state:
  st.session_state.timed_data = None

if "run_summary_data" not in st.session_state:
  st.session_state.run_summary_data = None

if "total_toks" not in st.session_state:
  st.session_state.total_toks = 0
  
# Remember which prompt/eta belongs to the current loaded run
if "run_eta" not in st.session_state:
  st.session_state.run_eta = None

if "run_prompt_id" not in st.session_state:
  st.session_state.run_prompt_id = None

def reset_replay():
  """Clears the current loaded run"""
  st.session_state.playing = False
  st.session_state.start_time = None
  st.session_state.elapsed = 0.0
  st.session_state.tok_ind = 0
  st.session_state.replay_text=""
  st.session_state.run_complete = False
  st.session_state.timed_data = None
  st.session_state.run_summary_data = None
  st.session_state.total_toks = 0
  st.session_state.run_eta = None
  st.session_state.run_prompt_id = None

def toggle_play():
  if st.session_state.playing: 
    # Pausing a run
    st.session_state.elapsed += time.time()-st.session_state.start_time 
    st.session_state.playing = False
  else: 
    # if play is pressed after a run is complete - resets the run
    if st.session_state.run_complete:
      reset_replay()

    # If no run has been loaded yet, load it now
    if st.session_state.timed_data is None:
      prompt = st.session_state.prompt_selector
      eta = st.session_state.compression_slider

      prompt_id = PROMPTS.index(prompt)+1

      metrics = json.load(open(f"demo_metrics/eta_{eta}/metrics_{prompt_id}.json"))

      st.session_state.timed_data = metrics["timed_data"]
      st.session_state.run_summary_data = metrics["run_summary"]

      st.session_state.total_toks = len(st.session_state.timed_data)

      st.session_state.run_eta = eta
      st.session_state.run_prompt_id = prompt_id
    
    # Play/resume
    st.session_state.start_time = time.time()
    st.session_state.playing = True

def update_metric(placeholder, title, value, unit):
  """Updates a live metric card"""
  placeholder.markdown(
    f"""
    <div class="metric-card">
      <div class="metric-title">{title}</div>
      <div class="metric-value">{value}</div>
      <div class="metric-unit">{unit}</div>
    </div>
    """,
    unsafe_allow_html=True
  )

def update_summary_card(placeholder, title, text):
  """run summary card"""
  placeholder.markdown(
    f"""
    <div class="summary-card">
      <div class="summary-title">{title}</div>
      <div class="summary-text">{text}</div>
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

def format_percent_text(value):
  """takes in a percentage and makes it relative"""
  if (value >= 100):
    text = f"+{value-100}%"
  else:
    text = f"-{100-value}%"

  return text

def top_bar():
  with st.container(border=True, key="top_bar"):

    prompt_col, compression_col, button_col = st.columns(
      [2.4,1.3,1], # sizes of columns
      gap="medium",
      vertical_alignment="center"
    )

    # TODO: fix prompt visibility in dropdown
    with prompt_col:
      prompt = st.selectbox(
        label="Select prompt",
        options = PROMPTS,
        key="prompt_selector"
      )

    with compression_col:
      eta = st.select_slider(
        label="Select compression",
        options = ETAS,
        value = 0.7,
        key="compression_slider"
      )

      st.markdown( # Adding css styling to the text
        f"""<p style='
          text-align:center; 
          font-size:12px; 
          color: #4285F4; 
          font-weight: 600;
          margin-top:-20px;
        '>
          {eta} ({int(eta*100)}% transmitted)
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
          type="secondary",
          width=90
        )

  return prompt, eta

prompt, eta = top_bar()
prompt_id = PROMPTS.index(prompt)+1

timed_data = st.session_state.timed_data
total_toks = st.session_state.total_toks

# Previous token's metrics (because the script has been rerun from the top so metrics will be displayed as zero unless i write this code)
if (timed_data is not None and st.session_state.tok_ind>0):
  # if a run has been loaded and already started

  prev_tok = timed_data[st.session_state.tok_ind-1]
  tok_num = prev_tok["token_num"]
  instant_tps = round(prev_tok["instant_tps"], 3)
  avg_tps = round(prev_tok["avg_tps"], 3)

else:
  instant_tps = 0.0
  avg_tps = 0.0
  tok_num = 0

#elapsed time
if st.session_state.playing:
  displayed_elapsed = st.session_state.elapsed + time.time() - st.session_state.start_time
else:
  # displayed elapsed time when run hasn't started or has already ended
  displayed_elapsed = st.session_state.elapsed


replay_col, metrics_col = st.columns([1.8,1], gap="small")

with replay_col:
  with st.container(border=True, height="stretch", key="live_replay"):
    st.subheader("LIVE REPLAY")

    with st.container(border=True, height=200, key="replay_text_box"):
      replay_text_placeholder = st.empty()
      replay_text_placeholder.write(st.session_state.replay_text)
      # st.empty() is a container that allows me to replace/update content inside it without redrawing the whole page

    progress_bar = st.progress(tok_num/total_toks if (not total_toks == 0) else 0, text=f"Tokens generated: {tok_num}/{total_toks}")

with metrics_col:
  with st.container(border=True, height="stretch", key="live_metrics"):
    st.subheader("LIVE METRICS")

    r1_c1, r1_c2 = st.columns(2,border=True) # top two cards
    r2_c1, r2_c2 = st.columns(2,border=True) # bottom two cards

    with r1_c1:
      instant_tps_placeholder = st.empty() 
      update_metric(instant_tps_placeholder, "Current tokens/s",instant_tps,"tokens/s")

    with r1_c2:
      avg_tps_placeholder = st.empty()
      update_metric(avg_tps_placeholder, "Average tokens/s",avg_tps,"tokens/s")

    with r2_c1:
      elapsed_placeholder = st.empty()
      update_metric(elapsed_placeholder,"Elapsed time",format_time(displayed_elapsed),"mm:ss:ms")

    with r2_c2:
      token_num_placeholder = st.empty()
      update_metric(token_num_placeholder, "Generated tokens",tok_num,"tokens")


#if start: 
if st.session_state.playing: 
  timed_data = st.session_state.timed_data
  total_toks = st.session_state.total_toks

  secs_passed = st.session_state.elapsed + time.time() - st.session_state.start_time #taking the elapsed time before pause was hit and adding the current "elapsed time" of this session
  
  update_metric(
    elapsed_placeholder,
    "Elapsed time",
    format_time(secs_passed),
    "mm:ss:ms"
  ) 

  tok_ind = st.session_state.tok_ind #the next token to be displayed

  #make sure there are still tokens remaining
  if tok_ind < total_toks: 

    next_update = timed_data[tok_ind]["time"] # the target time that we'll check for

    # If elapsed = time for next token (next update): update metrics and add token to generated text
    if secs_passed >= next_update:
      tok_data = timed_data[tok_ind]
      tok_num = token = tok_data["token_num"]
      token = tok_data["token"]

      update_metric(instant_tps_placeholder, "Current tokens/s",round(tok_data["instant_tps"],3),"tokens/s")
      update_metric(avg_tps_placeholder, "Average tokens/s",round(tok_data["avg_tps"],3),"tokens/s")
      update_metric(token_num_placeholder, "Generated tokens",tok_num,"tokens")

      percent_complete = tok_num/total_toks
      progress_bar.progress(percent_complete, text=f"Tokens generated: {tok_num}/{total_toks}")

      st.session_state.replay_text+=token
      replay_text_placeholder.write(st.session_state.replay_text)

      st.session_state.tok_ind+=1 # Points index to next token

      #check if run is finished
      if (st.session_state.tok_ind >= total_toks):
        st.session_state.run_complete = True
        st.session_state.elapsed = secs_passed
        st.session_state.playing = False

  time.sleep(0.01)
  #keep the replay moving - goes to top of script 
  st.rerun()


# TODO: complete run summary 
with st.container(border=True, height=230, key="run_summary"):
  st.subheader("RUN SUMMARY")
  #st.write("run replay to generate summary")
  stats_col, graph_col = st.columns([1.8,1], gap="small")

  #will update if run is complete
  if st.session_state.run_complete and st.session_state.run_summary_data is not None:
    summary_data = st.session_state.run_summary_data
    avg_tps = round(summary_data["avg_tps"],3)
    eta = summary_data["eta"]
    completion_time = round(summary_data["completion_time"],2)
    quality_score = summary_data["quality_score"]

    # statistics compared to eta1.0 for the same prompt
    summary1_0 = json.load(open(f"demo_metrics/eta_1.0/metrics_{prompt_id}.json"))["run_summary"] #metrics for eta1.0
    #speed_percent = round(100*avg_tps/summary1_0["avg_tps"])
    speed_factor = round(avg_tps/summary1_0["avg_tps"], 2)
    time_diff = round(completion_time-summary1_0["completion_time"],1)
    quality_diff = quality_score - summary1_0["quality_score"]

  with stats_col:
    with st.container(border=True, height=60, horizontal=True):

      placeholder1 = st.empty()
      placeholder2 = st.empty()
      placeholder3 = st.empty()
      placeholder4 = st.empty()

      update_summary_card(placeholder1,"Compression (η)", eta if st.session_state.run_complete else "N/A")
      update_summary_card(placeholder2, "Average tokens/s", f"{avg_tps} toks/s" if st.session_state.run_complete else "N/A")
      update_summary_card(placeholder3,"Completion time", f"{completion_time} s" if st.session_state.run_complete else "N/A")
      update_summary_card(placeholder4,"Quality score", f"{quality_score} s" if st.session_state.run_complete else "N/A")

    with st.container(border=True, height=60, vertical_alignment="top", horizontal=True):
      st.write("Compared to no compression (η=1.0):")

      c1,c2,c3 =st.columns([1,1,1], gap="xxsmall", vertical_alignment="center")
      with c1:
        placeholder5 = st.empty()
        #update_comparison_card(placeholder5, format_percent_text(speed_percent) if st.session_state.run_complete else "N/A", "Faster generation")
        update_comparison_card(placeholder5, speed_factor if st.session_state.run_complete else "N/A", "Faster generation")

      with c2:
        placeholder6 = st.empty()
        update_comparison_card(placeholder6, time_diff if st.session_state.run_complete else "N/A", "Completion seconds")

      with c3:
        placeholder7 = st.empty()
        update_comparison_card(placeholder7, quality_diff if st.session_state.run_complete else "N/A", "Quality difference")



  with graph_col:
    with st.container(border=True, height="stretch"):
      st.empty()

