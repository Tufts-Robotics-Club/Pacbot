# Pacbot

gameEngine runs the game simulator to train the deep Q learning model. Remember to change 
the file permissions on the bash files. Run "./runsim" to run the simulator on port 
11297 and run "./killsim" to kill it. 

There's still the issue that Pacbot and ghosts operate on different time frames. We'll have to see what that does to the performance of the actual robot. 

I'll add my training scripts in a sec. We gotta make sure they run fast on tflite on the raspberry pi.
We may have to retrain the model depending on how the above mentioned issue affects performance. 

Check the requirements.txt to see how to set up your virtualenv. There's a lot of irrelevnat garbage in there so sorry about that. Also don't mess up your current tensorflow config cause its super annoying to fix. s

Once everything is done I'll clean this up. 

Best.
