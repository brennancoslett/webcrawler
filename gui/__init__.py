import PySimpleGUI as sg
   
      
sg.theme('BluePurple')
   
layout = [[sg.Text('Search Keyword or Phrase:'),
           sg.Text(size=(15,1), key='-OUTPUT-')],
          [sg.Input(key='-IN-')],
          [sg.Button('Search'), sg.Button('Exit')],
          [sg.Listbox(values=['Test1', 'Test2', 'Test3','Test4', 'Test5'], select_mode='extended', key='fac', size=(30, 6))]]
  
window = sg.Window('Introduction', layout)

keyword = sg.Input(key='-IN-') 

while True:
    event, values = window.read()
    print(event, values)
      
    if event in  (None, 'Exit'):
        break
      
    if event == 'Search':
        # Update the "output" text element
        # to be the value of "input" element
        window['-OUTPUT-'].update(values['-IN-'])
  
window.close()