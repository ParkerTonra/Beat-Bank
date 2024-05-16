documentation, because bethesda doesn't know best.
to run:
venv\scripts\activate
cd C:\Users\parke\Documents\GitHub\Beat-Bank\src
python app.py
classes:

MainWindow(QMainWindow) - main window that inherits from QMainwindow

ModelManager manages the data models that interact with the SQL database
    sets up the model, improves readability, and sets up the proxy.


TODO:
- 
- allow users to add songs to playlist 
    - first with context menu, then drag and drop

- make clicking a playlist display that playlist
- make context menu reactive to where user right clicks.



Figure out why a track is always selected when the program is ran.(meh oh well)



SIDEBAR
- add new sets
- delete sets
- edit via double click or click selected (TODO)
- make selecting a playlist show that set on the table (TODO)
- TODO: make folders of sets
- TODO: always show "All Beats" at the top of the list.

WORKING FEATURES:
- Column reorder in beats table
- sets reorder in sidebar
- plays audio smoothly
- can add a song from file, program gets length, date added, created, etc and adds it to database




CONSIDERATIONS:
- messy BeatBank.py

2024/5/5
- got the audio playback to run smoothly.
- users can choose to edit items
- users can choose to rearrange columns
