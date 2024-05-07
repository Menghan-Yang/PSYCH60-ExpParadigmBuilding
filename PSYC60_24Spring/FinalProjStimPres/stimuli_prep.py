import os
import random
from datetime import datetime

base_dir = "/Users/menghanyang/Documents/dartmouth/requirements/TA/PSYC60_24Spring/FinalProjStimPres/"  # Menghan's personal laptop
stimu_dir = os.path.join(base_dir,"Psych60_Songs")  # Where onset data comes from (.txt file)
file_all_name = os.listdir(stimu_dir)

## randomly split file_all_name into two runs

random.seed(datetime.now().timestamp())
random.shuffle(file_all_name)

file_run1_name = file_all_name[:len(file_all_name)//2]
file_run2_name = file_all_name[len(file_all_name)//2:]

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

Jitter_all = [3,3,3,3,5,5,5,5,7,7,7,7]
random.seed(datetime.now().timestamp())
random.shuffle(Jitter_all)
Jitter_video = Jitter_all
random.shuffle(Jitter_all)
Jitter_rating = Jitter_all
