documentation, because bethesda doesn't know best.


classes:

MainWindow(QMainWindow) - main window that inherits from QMainwindow

ModelManager manages the data models that interact with the SQL database
    sets up the model, improves readability, and sets up the proxy.


TODO:
- If there's already a song playing, the player glitches out. program crashes.
- Allow Users to change column width
- allow users to add songs to playlist 
    - first with context menu, then drag and drop
- Figure out why a track is always selected when the program is ran.
- make clicking a playlist display that playlist
- make context menu reactive to where user right clicks.


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

BROKEN FEATURES:
- tracks do not play
- selected track is not updated properly.

CONSIDERATIONS:
- messy BeatBank.py