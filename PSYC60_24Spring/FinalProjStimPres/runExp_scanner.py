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
config_dialog.addField("Run Number: ")
config_dialog.addField("Scanner?\n(expect triggers?): ", choices=[True, False])
config_dialog.addField("Debug mode?\n ", choices=[True, False])
ok_data = config_dialog.show()  # show dialog and wait for OK or Cancel


if config_dialog.OK:
    print(config_dialog.data)
    sub_id = config_dialog.data["Subject ID: "]
    run_num = str(config_dialog.data["Run Number: "])

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

# stim_list = ['America.wav','Beatles.wav','CurtisHarding.wav']
random.seed(datetime.now().timestamp())
file_run1_name = ['FlatlandCavalry.wav',
 'America.wav',
 'Carpenters.wav',
 'BobMarley.wav',
 'WendyRene.wav',
 'TownesVanZandt.wav',
 'Beatles.wav',
 'Strokes_YouOnlyLiveOnce.wav',
 'Florence+TheMachine.wav',
 'PennyPenny.wav',
 'SaintMotel.wav',
 'ArcadeFire.wav']

file_run2_name = ['CurtisHarding.wav',
 'Muse.wav',
 'EltonJohn.wav',
 'Strokes.wav',
 'Paramore.wav',
 'MaxRichter.wav',
 'KateBush.wav',
 'NeilYoung.wav',
 'Donnie&JoeEmerson.wav',
 'Dilla.wav',
 'Chainsmokers.wav',
 'TaylorSwift.wav']
random.shuffle(file_run1_name)
random.shuffle(file_run2_name)

file_all_name = [file_run1_name,file_run2_name]

Jitter_all = [3,3,3,3,5,5,5,5,7,7,7,7]
random.shuffle(Jitter_all)
Jitter_video = Jitter_all
print(Jitter_video)
random.shuffle(Jitter_all)
Jitter_rating = Jitter_all
print(Jitter_rating)

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
    data_writer_onsets.writerow(["sid","run_num","stim_file","onset","offset","ratings","ratings_onset","ratings_offset","response_time","jitter_after_video","jitter_after_rating"])



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

# Load up music depending on run_name
# mySound = sound.Sound(value=stim_vid_path)

### EXPERIMENT START ###
mouse.setVisible(0)

def draw_fixation():
    fixation.draw()
    window.flip()

# def present_ITI(window, jitter):
#     mouse.setPos([0, 0])
#     fixation.pos = mouse.getPos()

#     fixation.draw()
#     window.flip()
#     core.wait(jitter)
#     window.flip()


### RUN EXPERIMENT ###
# Run 1: fixation --> music --> ratings --> fixation
# Run 2: fixation --> music --> ratings --> fixation
# Run 3: fixation --> comedy --> ratings --> fixation ## seperate
### adding jitters bettwen music and ratings
fixation_sound = visual.TextStim(win=window, text="Playing the clip", color=textColor, font=textFont, pos=(0, 0), height=textHeight, alignHoriz=alignText)


if int(run_num) <= n_runs:

    instruct_text = (
        f"You are about to complete Run {run_num} out of {n_runs} Total Runs. \n You will listen to music clips and then rate after each clip"
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


    # Play the music
    stim_list = file_all_name[int(run_num)-1]
    for Jitter_num,audio_file in enumerate(stim_list):
        time_data = []

        music_onset = clock.getTime() - fmriStart
        stim_vid_path = os.path.join(base_dir,"Psych60_Songs",audio_file)
        fixation_sound.draw()
        window.flip()
        sound_clip = sound.Sound(stim_vid_path)
        sound_clip.play()
        core.wait(30)  # Assuming each clip duration is 30 seconds
        sound_clip.stop()
        music_offset = clock.getTime() - fmriStart
        draw_fixation()
        core.wait(Jitter_video[Jitter_num]) 
        window.flip()
     # Jittered interval between clips

        # Prompt for participant rating
        rating_prompt = visual.TextStim(window, text='How much do you like this music? \n\n1•••••••••2•••••••••3•••••••••4•••••••••5 \n\nleast                                     most', pos=(0, 0))
        rating_prompt.draw()
        window.flip()

        # Wait for participant rating for a maximum of 3 seconds
        response_clock = core.getTime()
        response_start_clock = clock.getTime()
        keys = event.waitKeys(keyList=['1', '2', '3', '4', '5'], maxWait=response_duration, timeStamped=True)
    
        # Calculate response time
        if keys:
            response_time = keys[0][1] - response_clock
            response = keys[0][0]  # Assuming only one key is pressed
        else:
            response_time = response_duration
            response = 'nan'
        
        # Display fixation if response was quicker than question_duration
        if response_time < response_duration:
            draw_fixation()
            window.flip()
            core.wait(response_duration - response_time)
    
        response_end_clock = clock.getTime()

        draw_fixation()
        core.wait(Jitter_rating[Jitter_num]) 
        window.flip()
        
        # Jittered interval between ratings

        time_data.append([sub_id,int(run_num),audio_file,music_onset,music_offset,response,response_start_clock - fmriStart,response_end_clock - fmriStart,response_time,Jitter_video[Jitter_num],Jitter_rating[Jitter_num]])
        # write onsets file
        print("writing to onsets csv...")
        
        with open(onsetsFilePath, mode='a', newline='') as onsets_data_file:
            data_writer_onsets = csv.writer(onsets_data_file, delimiter=",", lineterminator="\n")
            data_writer_onsets.writerows(time_data)

        print(f"{audio_file} clips ended...")
        if len(event.getKeys(["escape"])):
            clean_up(scanner)
    print(f"run {run_num} clips ended...")

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

