
from __future__ import print_function
from time import sleep

from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.util import toHexString


from smartcard.CardType import AnyCardType
from smartcard.CardRequest import CardRequest
from smartcard.CardConnectionObserver import ConsoleCardConnectionObserver
from smartcard.CardConnection import CardConnection
from smartcard.util import toHexString, toBytes, toASCIIString, toASCIIBytes
import re
import ff
from datetime import datetime

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

    def __init__(self):
        self.master = tk.Tk()
        self.button = tk.Button(self.master, text="Start", command=self.monitor)
        self.label_text = tk.StringVar()
        self.format_text = tk.StringVar()
        label = tk.Label(self.master, textvariable=self.label_text)
        format = tk.Label(self.master,textvariable=self.format_text)

        self.button.grid(row=1, column=0, sticky=tk.W + tk.E)
        label.grid(row=1, column=1, sticky=tk.W+tk.E)
        format.grid(row=2,column=2, sticky=tk.W+tk.E)

    def monitor(self):
        cardmonitor = CardMonitor()
        selectobserver = selectDFTELECOMObserver()
        cardmonitor.addObserver(selectobserver)
        
        self.button.config(state=tk.DISABLED)

    def run(self):
        self.master.mainloop()
        
        
 
    

    
if __name__ == '__main__':
    App = CardReaderGUI()
    App.format_text.set('{pan};4;Zwrot z Poczty;{exp}')
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


            
