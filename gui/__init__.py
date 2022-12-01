import PySimpleGUI as sg

sg.theme('BluePurple')
   
#data = db.url_with_keyword
data = [
    ['Ronald Reagan', 'February 6'],
    ['Abraham Lincoln', 'February 12'],
    ['George Washington', 'February 22'],
    ['Andrew Jackson', 'March 15'],
    ['Thomas Jefferson', 'April 13'],
    ['Harry Truman', 'May 8'],
    ['John F. Kennedy', 'May 29'],
    ['George H. W. Bush', 'June 12'],
    ['George W. Bush', 'July 6'],
    ['John Quincy Adams', 'July 11'],
    ['Garrett Walker', 'July 18'],
    ['Bill Clinton', 'August 19'],
    ['Jimmy Carter', 'October 1'],
    ['John Adams', 'October 30'],
    ['Theodore Roosevelt', 'October 27'],
    ['Frank Underwood', 'November 5'],
    ['Woodrow Wilson', 'December 28'],
]

layout = [[sg.Text('Search Keyword or Phrase:'),
           sg.Text(size=(15,1), key='-OUTPUT-')],
          [sg.Input(key='-IN-')],
          [sg.Button('Search'), sg.Button('Exit')],
          [sg.Table(data, justification='left', key='-TABLE-')]]
          #[sg.Table(data, justification='left', key='-TABLE-')]]
  
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