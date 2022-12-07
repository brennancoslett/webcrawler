import PySimpleGUI as sg

sg.theme('BluePurple')

layout = [[sg.Text('Search Keyword or Phrase:'),
           sg.Text(size=(15,1), key='-OUTPUT-')],
          [sg.Input(key='-IN-')],
          [sg.Button('Search'), sg.Button('Exit')],
          [sg.Table(data, justification='left', key='-TABLE-')]]
  
window = sg.Window('Introduction', layout)

keyword = sg.Input(key='-IN-') 

while True:
    event, values = window.read()
    print(event, values)
      
    if event == 'Search':
        # Update the "output" text element
        # to be the value of "input" element
        window['-OUTPUT-'].update(values['-IN-'])

    if event == sg.WINDOW_CLOSED:
        break

    print(event, values)
  
window.close()