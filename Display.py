import Data
import PySimpleGUI as sg
import tkinter

def run(threadname):
    def excecutetest(command):
        for i in range(5):
            print (command + str(Data.PLAYER_X_COORD))

    layout = [
        [sg.Text('Information:', size=(40, 1))],
        [sg.Output(size=(88, 20))],
        [sg.Button('EXIT')]
    ]

    window = sg.Window('testing', layout)

    # ---===--- Loop taking in user input and using it to call scripts --- #

    while True:
        window.Refresh()
        (event, value) = window.Read()
        if event == 'EXIT'  or event is None:
            break # exit button clicked
        if event == 'Run':
            excecutetest(value[0])
    window.Close()
