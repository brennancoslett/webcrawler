import PySimpleGUI as sg
import sys
import os
sys.path.append(os.getcwd())

from crawler.database import Database
db = Database(input_file="data/coe_database.msgpack")
data = []

sg.theme('Reddit')

layout = [[sg.Text('Search Keyword or Phrase:'),
           sg.Text(size=(15,1), key='-OUTPUT-')],
          [sg.Input(key='-IN-')],
          [sg.Button('Search'), sg.Button('Exit')],
          [sg.Listbox(data, key='-TABLE-',size=(50,10))]]
  
window = sg.Window('Search Engine', layout,resizable=True)

keyword = sg.Input(key='-IN-') 

while True:
    event, values = window.read()
    print(event, values)
      
    if event == 'Search':
        # Update the "output" text element
        # to be the value of "input" element
        data = db.urls_with_keyword(values['-IN-'])
        window.Element("-TABLE-").Update(values=data)

    if event == sg.WINDOW_CLOSED or event == "Exit":
        break

    print(event, values)
  
window.close()