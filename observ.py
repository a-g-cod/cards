from __future__ import print_function
from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.CardConnectionObserver import ConsoleCardConnectionObserver
import ff
import Tkinter as tk


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
            cper=ff.CardPanExpReader()
            panExp=cper.getPanExp()
            with open("numerykart.txt","w") as f:
                f.write(panExp[0]+'|'+panExp[1]+'\n')
            App.label_text.set(panExp[0]+'|'+panExp[1])
##            print(datetime.now(), "Zapisanoe w pliku karte")

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
        self.button = tk.Button(self.master, text="Start", command=self.monitor)
        self.label_text = tk.StringVar()
        self.option_value = tk.StringVar()
        self.label = tk.Label(self.master, textvariable=self.label_text)

        self.button.grid(row=1, column=0, sticky=tk.W + tk.E)
        self.label.grid(row=2, column=0, sticky=tk.W+tk.E)

        self.createOpBtns(modes=self.MODES, variable=self.option_value, row=3)
        self.option_value.set('ZIF')

    def createOpBtns(self, modes, variable, row):
        for text, value in modes:
            optBtn = tk.Radiobutton(self.master, text=text,
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


            
