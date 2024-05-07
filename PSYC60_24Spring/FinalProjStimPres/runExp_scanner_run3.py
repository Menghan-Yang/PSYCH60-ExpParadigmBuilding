from __future__ import division
from psychopy import prefs
from psychopy import sound, visual, event, core, gui, logging
import os
import sys
import csv
import pandas as pd
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)
import numpy as np
import random
from datetime import datetime
# from psychopy.visual.movie3 import MovieStim3


prefs.general["audioLib"] = ["pygame"]
prefs.general["audioDevice"] = ["Built-in Output"]


"""
Author: Menghan Yang
Last updated: 05.07.24
modified based on https://github.com/wasita/psyc60-final-proj-stim-pres/blob/main/f22/runExp.py 
"""

base_dir = "/Users/menghanyang/Documents/dartmouth/requirements/TA/PSYC60_24Spring/FinalProjStimPres/"  # Menghan's personal laptop
data_dir = os.path.join(base_dir, "data")  # Where onset data comes from (.txt file)


### DIALOGUE SCREENS AND DATA FILE ###
# Basic info
config_dialog = gui.Dlg(title="PSYC60 2024 Final Project Participant Setup")
config_dialog.addField("Subject ID: ")
config_dialog.addField("Run Number (RUN 3 only!): ")
config_dialog.addField("Scanner?\n(expect triggers?): ", choices=[True, False])
config_dialog.addField("Debug mode?\n ", choices=[True, False])
ok_data = config_dialog.show()  # show dialog and wait for OK or Cancel


if config_dialog.OK:
    print(config_dialog.data)
    sub_id = config_dialog.data["Subject ID: "]
    run_num = str(config_dialog.data["Run Number (RUN 3 only!): "])

else:
    print('user cancelled')
    core.quit()

scanner = True

# Define a cleanup function to handle device closures
def clean_up(scanner=scanner):
    """Because pyo audio backend tends to cause experiment crashes on close.
    add some print messages to assure we at least get to the end."""
    mouse.setVisible(1)
    print("CLOSING WINDOW...")
    print("Overall, %i frames were dropped." % window.nDroppedFrames)
    window.close()
    print("QUITTING...")
    core.quit()

stim_list = ['JimGaffigan.mp4']

# Generate datafile and check for overwrite
# Disable file buffering on open; instead write to it immediately
if int(sub_id) < 10:
    sub_id = "s0" + str(sub_id)
else:
    sub_id = "s" + str(sub_id)

### INITIALIZE DATAFILE TO WRITE INTO ###
onsetsFileName = "%s_run%s_onsets.csv" % (sub_id, run_num)
onsetsFilePath = os.path.join(data_dir, onsetsFileName)

with open(onsetsFilePath, mode='w', newline='') as onsets_data_file:

    # onset	duration	trial_type	response_time	stim_file	sid	run_num	offset	post_stim_jitter
    data_writer_onsets = csv.writer(onsets_data_file, delimiter=",", lineterminator="\n")
    data_writer_onsets.writerow(["sid","run_num","stim_file","video_onset","key_pressed","key_pressed_onset","key_pressed_RT","video_offset"])



### DEVICES AND EXP VARIABLES ###
# Exp specific variables
# Seconds to wait and beginning and end of study
init_wait = 10
n_runs = 3
tr = 2
response_rt = []  # initialize this way to have at least one row in response .csv
response_key_pressed = []
response_duration = 3
fixation_duration = 3

# Inputs
fmriTrigger = "5"
proceedTrigger = "space"

# Visuals
textColor = "white"
textFont = "Arial"
textHeight = 0.15
testWinSize = ((2460, 1600) if scanner else (1440, 900))
# testWinSize = (1440, 900)
  # 13" personal laptop: [1440, 900]
expWinSize = (2460, 1600) if scanner else (1440, 900)
# expWinSize = (1440, 900)
alignText = "center"
alignVert = "center"

# Auxilliary
logging.console.setLevel(logging.WARNING)

# Main experiment clock
clock = core.Clock()

# Apply settings based on testing or real experiment
# Need to be tested for the scan
winSize = testWinSize
fullScr = False
screen = 0
allowGUI = True

window = visual.Window(
    size=winSize, fullscr=fullScr, screen=screen, allowGUI=allowGUI, color="black"
)
mouse = event.Mouse(win=window)
event.globalKeys.add(key="escape", func=clean_up, name="shutdown")


### SCREENS AND STIMULI ###
# Pre-scan
wait_stim = visual.TextStim(
    win=window,
    name="waitText",
    text="Waiting for scanner",
    color=textColor,
    font=textFont,
    height=textHeight,
    alignHoriz=alignText,
)

def run_instruct(window, instruct_text, textColor, textFont, textHeight, alignText):
    run_instruct_stim = visual.TextStim(
        win=window,
        name="run_instruct",
        text=instruct_text,
        color=textColor,
        font=textFont,
        height=textHeight,
        alignHoriz=alignText,
    )
    run_instruct_stim.draw()
    window.flip()


# Fixation
fixation = visual.TextStim(
    win=window,
    name="fixation",
    text="+",
    color=textColor,
    font=textFont,
    height=textHeight,
    alignHoriz=alignText,
)


### EXPERIMENT START ###
mouse.setVisible(0)

def draw_fixation():
    fixation.draw()
    window.flip()

### RUN EXPERIMENT ###
# Run 1: fixation --> music --> ratings --> fixation
# Run 2: fixation --> music --> ratings --> fixation
# Run 3: fixation --> comedy --> ratings --> fixation ## seperate
### adding jitters bettwen music and ratings
time_data = [] ## all the reactions and video info

if int(run_num) <= n_runs:

    instruct_text = (
        f"You are about to complete Run {run_num} out of {n_runs} Total Runs.\n You will watch a video.\nDuring when you can press '1' when you think it is funny"
    )
    run_instruct(window, instruct_text, textColor, textFont, textHeight, alignText)

    # Wait for experimenter to proceed with trials for run
    trigger = ""
    while trigger != proceedTrigger:
        trigger = event.getKeys(keyList=["space"])
        if trigger:
            trigger = trigger[0]

    # Wait to receive trigger here
    # Borrowed & adapted from Michael Sun from Wager (CAN) Lab [Oct, 2021]

    start_msg = "Please wait. \nThe scan will begin shortly. \n Experimenter press [space] to continue."
    start = visual.TextStim(window, text=start_msg, height=textHeight, color=textColor)
    start.draw()  # Automatically draw every frame
    window.flip()

    continueRoutine = True
    event.clearEvents()
    trigger = ""

    while trigger != proceedTrigger:
        trigger = event.getKeys(keyList=[proceedTrigger])
        if trigger:
            trigger = trigger[0]

    while continueRoutine == True:
        if fmriTrigger in event.getKeys(
            keyList=fmriTrigger
        ):  # <-- GET YOUR FMRI trIGGER THIS WAY
            fmriStart = clock.getTime()  # Start the clock
            # [10.29.21] Currently comment out the wait time
            # as Terry said dummy scans are taken _before_ trigger is received
            # timer = core.CountdownTimer()  # Wait 6 trs, Dummy Scans
            # timer.add(tr * 6)

            # while timer.getTime() > 0:
            #     continue
            start_msg = "Please wait. \nThe scan will begin shortly."
            start = visual.TextStim(
                window, text=start_msg, height=0.05, color=textColor
            )
            start.draw()  # Automatically draw every frame
            window.flip()
            continueRoutine = False


    # Pre-movie fixation
    draw_fixation()
    core.wait(init_wait)    
    window.flip()

    timer = core.Clock()
    timer.add(init_wait)
    # continueRoutine = True


    # Play the video
    # for Jitter_num,audio_file in enumerate(stim_list):
    audio_file = stim_list[0]

    video_onset = clock.getTime() - fmriStart
    stim_vid_path = os.path.join(base_dir,"Psych60_comedy",audio_file)
    window.recordFrameIntervals = True
    mov = visual.MovieStim(window, stim_vid_path, size=winSize,
    flipVert=False, flipHoriz=False, loop=False)
    start_time = core.getTime()
    mov.play()
    while mov.isFinished != True:
        mov.draw()
        # audio.play()
        window.flip()

        if len(event.getKeys(["escape"])):
            clean_up(scanner)
        # button press whenever think of X person
        elif len(event.getKeys(keyList=["1"])):
            key_onset = clock.getTime()- fmriStart
            keyRT = clock.getTime() - video_onset
            response_key_pressed.append("1")
            response_rt.append(keyRT)
            time_data.append([sub_id,int(run_num),audio_file,video_onset,'1',key_onset,keyRT])
            print("response_key_pressed", response_key_pressed)
            print("response_rt", response_rt)

        # Check if 6 minutes 47s (length of video) have passed since the movie started
        # if core.getTime() - start_time >= 407:
        #     break
   
    #movie stop
    mov.stop()
    print(f"run {run_num} clips ended...")
    video_offset = clock.getTime() - fmriStart
    window.recordFrameIntervals = False
    draw_fixation()
    window.flip()
    core.wait(3)    

    [ele.append(video_offset) for ele in time_data]
    # write onsets file
    print("writing to onsets csv...")
    
    with open(onsetsFilePath, mode='a', newline='') as onsets_data_file:
        data_writer_onsets = csv.writer(onsets_data_file, delimiter=",", lineterminator="\n")
        data_writer_onsets.writerows(time_data)


    # Post-video fixation
    ending_text = (
        f"You complete Run {run_num} out of {n_runs} Total Runs"
    )
    ending = visual.TextStim(
            win=window,
            name="ending_text",
            text=ending_text,
            color=textColor,
            font=textFont,
            height=textHeight,
            alignHoriz=alignText,
        )
    ending.draw()
    core.wait(init_wait)
    window.flip()

    fmriEnd = clock.getTime()  # Start the clock
    scantime = fmriEnd-fmriStart
    print(f"Entire Scan Time: {scantime}")
    window.close()
    core.quit()


### CLOSE AND CLEANUP ###
print("cleaning up...")
clean_up(scanner)



