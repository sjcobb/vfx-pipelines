# Blender MIDI Add-on Notes

## 3D circular animation workflow (audiocarver - andy-fillebrown)

https://github.com/andy-fillebrown/audiocarver-blender-addon/issues/1
https://github.com/andy-fillebrown/audiocarver-blender-addon/issues/1#issuecomment-205061221
- see: MidiFileReadMergedPythonBartkyFillebrownExample.zip

https://www.youtube.com/watch?v=-z6TzOCqhKA

akb168 comment

+Synthh The general way I make my videos is to:


1) record, edit etc. the music first so I get MIDI data and audio data exported from my Music program (Cakewalk Sonar)
2) then import the MIDI data into a Blender software by running a custom Python program that has some of my Python written software and for newer videos such as this, Python code from Andy Fillebrown.
3) The Python code is run in a "Blender Rig" which basically a starting point of a master blender data file that works in conjunction with the Python code to convert the MIDI data into Blender objects that are setup to animate in space (note and/or track) and time (when note on and note off events occur).
4) I usually wind up tweaking/modifying the Python and the blender file so that every video is a little different (change object colors, move notes to get different looks, etc.
5) I then run Blender animation menus to output the data as PNG files with one PNG file per frame.
6) Then I import that frame PNG files into Adobe Premiere to turn into a movie.
7) Finally I import the audio, use Premiere to synchronize the audio to the video, add titles, etc.
8) Then I play the video on my computer, make any final adjustments, then upload to YouTube.


With that, most of my time to get this stuff to where I like it I did most of my learning for Blender Basics and also Python programming from YouTube Videos.  The ones that helped me the most were Sci Fi Animator's channel where he has a large amount of videos from the basics, to python to very advanced techniques.  His channel is here: https://www.youtube.com/user/FirstGradeCalculus


Andy Filebrown's channel is here (he is the author of the Blender file and some of the python code I've used recently): https://www.youtube.com/channel/UCg2NGO_2F1c3vQvT8_kzy5w


For the first set of videos I created, I used Steven Malinowski's MAMPlayer and HyperCam to capture the program's video.  His program (the one he published for open use as a Windows program) is here: http://www.musanim.com/player/  That program is a good place to start in experimenting with taking MIDI files and making 2D animations.  Steven Malinowski's channel is here: https://www.youtube.com/channel/UC2zb5cQbLabj3U9l3tke1pg


There is also MIDITrail software that you can get as a Windows or MAC binary program (or in my case, you can also download and customize the C code).  Link to that is here: https://en.osdn.jp/projects/miditrail/  Link to the author's youtube channel that has 2 demo videos is here: https://www.youtube.com/channel/UCAoNUfq8UUmXSYccjazFZsQ


So if you are interested in making MIDI based animations, I'd suggest trying MAMPlayer and MIDITrail first (there is always Synthesia as well).  Getting to the stuff that I and Andy Fillebrown having been doing for Blender still involves Python code and customization to create the videos, so I wouldn't advise it unless you have some reasonably good programming abilities.


Anyway, hope this helps and all the best,


Alan

--

Synthh
4 years ago
+akb168 Wow, thanks! Very helpful. What I'm trying to achieve is something similar to Synthesia, although I've since realised that the idea is futile and a MAMPlayer-type thing is probably more realistic, where a MIDI file is inputted and the output is visualised in a similar fashion and also played through an out port.
I'm not having much success with the Python aspect, and I recently stumbled upon these videos and Blender.

--

akb168
akb168
4 years ago
+Synthh There is an option in MIDITrail to have it do an animation similar to Synthesia, but in 3D.  Also the documentation isn't great for it, but you can go and edit text based configuration files to tweak it.  An video example I did 3 years ago where I used MIIDTrail with some tweaking of the text files (to reduce keyboards to 2 total and change the spacing and colors) is here: https://www.youtube.com/watch?v=An05Yd9oSwo

## Misc Notes

- /Users/scobb/Library/Application Support/Blender/2.82/scripts/addons/run_script_pyconsole
- ~/Library/Application Support/Application Support/Blender/2.82/scripts/addons
- In Blender... Edit -> Preferences... install from zip file results in 'Import AudioCarver format' Add-on with 'upgrade to 2.8x required' error message
- https://blender.stackexchange.com/a/5420 - console debugging
- https://blender.stackexchange.com/a/149934 - print message to info script
- https://b3d.interplanety.org/en/blender-add-on-print-to-python-console/
- https://blender.stackexchange.com/questions/5394/is-there-anyway-to-make-blender-print-errors-in-the-ui
- https://gist.github.com/tin2tin/a48ab242db6f6d9ce6fa36c85464bc1d - tin2tin/Run_Script_in_PyConsole.py