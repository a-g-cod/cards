from __future__ import print_function
from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.CardConnectionObserver import ConsoleCardConnectionObserver
import ff
import Tkinter as tk
from datetime import date
from PIL import Image, ImageTk
class selectDFTELECOMObserver(CardObserver):
    """A simple card observer that is notified
    when cards are inserted/removed from the system and
    prints the list of cards
    """

    def __init__(self):
        self.observer = ConsoleCardConnectionObserver()

    def update(self, observable, actions):
        (addedcards, removedcards) = actions
        for card in addedcards:
            cper = ff.CardPanExpReader()
            panExp = cper.getPanExp()
            record = App.FORMATS[App.option_value.get()]['RECORD'].format(panExp[0], panExp[1])
            fileName = App.FORMATS[App.option_value.get()]['FILE'].format(date.today())
            with open(fileName,"a") as f:
                f.write(record+'\n')
            App.label_text.set(panExp[0]+'|'+panExp[1])

        for card in removedcards:
##            print("-Removed")
            App.label_text.set('')
            
            
class CardReaderGUI():
    MODES = [
        ('Zwrot z Poczty - Nowe wydania', 'ZPNE'),
        ('Zwrot z Poczty - Wznowienia', 'ZPWZN'),
        ('Zwrot z instytucji finansowej', 'ZIF')
    ]

    FORMATS = {
        'ZPNE' :{'FILE':'PAN_{0:%Y}_{0:%m}_{0:%d}_NE.TXT'   ,'RECORD':'{0};4;Zwrot z Poczty'},
        'ZPWZN':{'FILE':'PAN_{0:%Y}_{0:%m}_{0:%d}_WZN.TXT'  ,'RECORD':'{0};4;Zwrot z Poczty'},
        'ZIF' :{'FILE':'PAN_{0:%Y}_{0:%m}_{0:%d}_ZIF.TXT'   ,'RECORD':'{0};4;Zwrot z Instytucji Finansowej;{1}'}
    }

    def __init__(self):
        self.master = tk.Tk()
        self.master.resizable(0,0)
        self.createLogo(self.master, width=190, height=50, file='zdj.png')
        frame = tk.Frame(self.master)
        frame.pack()
        self.button = tk.Button(frame, text="Start", command=self.monitor)
        self.label_text = tk.StringVar()
        self.label = tk.Label(frame, textvariable=self.label_text)
        self.option_value = tk.StringVar()



        self.button.grid(row=1, column=0, sticky=tk.W + tk.E)
        self.label.grid(row=2, column=0, sticky=tk.W+tk.E)

        self.createOpBtns(master=frame, modes=self.MODES, variable=self.option_value, row=3)
        self.option_value.set('ZIF')

    def createLogo(self, master, width, height, file):
        canvas = tk.Canvas(master, height=height, width=width)
        image = Image.open(file)
        image.thumbnail((width, height))
        photo = ImageTk.PhotoImage(image)
        background_label = tk.Label(canvas, image=photo)
        background_label.photo = photo
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
        canvas.pack()

    def createOpBtns(self, master, modes, variable, row):
        for text, value in modes:
            optBtn = tk.Radiobutton(master, text=text,
                        variable=variable, value=value)
            optBtn.grid(row=row, column=0, sticky=tk.W)
            row = row + 1

    def monitor(self):
        cardmonitor = CardMonitor()
        selectobserver = selectDFTELECOMObserver()
        cardmonitor.addObserver(selectobserver)
        self.button.config(state=tk.DISABLED)

    def run(self):
        self.master.mainloop()

if __name__ == '__main__':
    App = CardReaderGUI()
    App.master.title('Alior')
    App.run()
    
    
    
##    cardmonitor = CardMonitor()
##    selectobserver = selectDFTELECOMObserver()
##    cardmonitor.addObserver(selectobserver)
##
##    #sleep(600)
##
##    # don't forget to remove observer, or the
##    # monitor will poll forever...
##    #cardmonitor.deleteObserver(selectobserver)
##
##    import sys
##    if 'win32' == sys.platform:
##        print('press Enter to continue')
##        sys.stdin.read(1)


            
