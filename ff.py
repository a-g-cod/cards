from smartcard.CardType import AnyCardType
from smartcard.CardRequest import CardRequest
from smartcard.CardConnectionObserver import ConsoleCardConnectionObserver
from smartcard.CardConnection import CardConnection
from smartcard.util import toHexString, toBytes, toASCIIString, toASCIIBytes
import re


class CardPanExpReader():
    
    GET_RESPONSE = [0x00, 0xC0, 0x00, 0x00]
    GET_PROCESSING_OPTIONS_str = "80A80000028300"  #80A80000 07(=5+2) 83 05 (2) 0000000000 (5)  PDOL: tag 9F40 length 05 80A80000028300 visa [CLS:80 INS:A8 P1:00 P2:00 Lc:XX Data:PDOL Le:00] (Lc:02 Data:8300 dla brak PDOL(Tag:83))
    

    def __init__(self, filename="aid_list.txt"):
        self._cardtype = AnyCardType()
        self._cardrequest = CardRequest(timeout=10, cardType=self._cardtype)
        self._cardservice = self._cardrequest.waitforcard()
        self._cardservice.connection.connect()
        #print toHexString(self._cardservice.connection.getATR())
        self.aids = self._getAids(filename)

    def _getProtocolNumber(self):
        #return toHexString(self._cardservice.connection.getATR())[3]

        if toHexString(self._cardservice.connection.getATR())[3]=='6':
            return 0
        else:
            return 1
        
    def _Le(self):
        return '00' if self._getProtocolNumber() else ''
        

        
    def _sendApdu(self, apduStr):
        apdu=toBytes(apduStr)
        print '******'
        print "Send Apdu", toHexString(apdu)
        response, sw1, sw2 = self._cardservice.connection.transmit(apdu)
        print 'Response status', hex(sw1), hex(sw2)
        print "Response result", toHexString(response)
        if sw1==0x61:
            print '61'
            apdu= self.GET_RESPONSE + [sw2]
            response, sw1, sw2 = self._cardservice.connection.transmit(apdu)
            print 'Response status', hex(sw1), hex(sw2)
            print "Response 0x61", toHexString(response)
        if sw1==0x6C:
            print '6C'
            apdu=apdu[0:-1] + [sw2] #apdu[0:-1] + [sw2] visa
            response, sw1, sw2 = self._cardservice.connection.transmit(apdu)
            print 'Response status', hex(sw1), hex(sw2)
            print "Response 0x6C", toHexString(response)
        return response,sw1,sw2


    def _selectAidApdu(self, aid):
        return "00A40400"+toHexString([len(aid)/2])+aid+self._Le() #bez 00 visa

    def _trySelectAid(self, aid):
        
        result=False
        try:
            response,sw1,sw2=self._sendApdu(self._selectAidApdu(aid))
        except:
            pass
        else:
            if response:
                result=True
        return result


    def _getAids(self, filename):
        with open(filename,'r') as f:
            for aidCandidate in f:
                if self._trySelectAid(aidCandidate.rstrip()):
                    yield aidCandidate

    def _readRecordApdu(self, sfi, record):
    #00B2020C00 #READ_RECORD={CLA:00, INS:B2, P1:02, P2:0C, Lc:00} record 02 form SFI 1
        lst=[record]
        P1 = toHexString(lst)
        lst=[sfi<<3|1<<2]
        P2 = toHexString(lst)
        return "00B2"+P1+P2+"00"

    def _retrievePanExp(self, response):
        ##70 4D 57 13 42 22 05 00 11 47 95 49 D1 90 2
        pat = re.compile(r'70.*57\w{2}(\d{16})D(\d{4}).*')
        try:
            result = re.match(pat, re.sub(r'\s',"",toHexString(response))).groups()
        except:
            result = None
        return result
       

    def getPanExp(self):
        for aid in self.aids:    
            SELECT_APP_str = self._selectAidApdu(aid)
            response,sw1,sw2=self._sendApdu(SELECT_APP_str)

            
            response,sw1,sw2=self._sendApdu(self.GET_PROCESSING_OPTIONS_str + self._Le())
        

            gporesponse={"AIP":"","AFL":[]}
            if response:
                if response[0]==0x80:
                    #print "Get processing options template 80"
                    gporesponse["AIP"] = toHexString(response[1:3])
                    #print "AIP: ", gporesponse["AIP"]
                    #print
                    afl=response[4:]
                    #print "AFL: ", afl
                    while afl:
                        afl[0]=afl[0]>>3
                        gporesponse["AFL"].append(afl[:4])
                        print "SFI {0}, From Record {1}, To Record {2}, Offl.Data.Auth.Records {3}".format(*afl[:4])
                        afl=afl[4:]
                    #print gporesponse
                    #print
                if response[0]==0x77:
                    #77 16 82 02 39 00 94 10 10 02 02 01 18 01 01 00 20 01 01 00 28 01 02 00
                    #templte:77 length:16 tagAIP:82  lengthAIP:02 AIP:39 00 tagAFL:94 lengthAFL:10 AFL:10 02 02 01 18 01 01 00 20 01 01 00 28 01 02 00
                    afl=response[response.index(0x94)+2:]
                    while afl:
                        afl[0]=afl[0]>>3
                        gporesponse["AFL"].append(afl[:4])
                        print "SFI {0}, From Record {1}, To Record {2}, Offl.Data.Auth.Records {3}".format(*afl[:4])
                        afl=afl[4:]
                    
                else:
                    pass
            
            for afl in gporesponse["AFL"]:
                sfi, fromrecord, torecord,oda=afl
                record=fromrecord
                while record<=torecord:
                    response, sw1, sw2 = self._sendApdu(self._readRecordApdu(sfi,record))
                    print "SFI:{0}, Record: {1}".format(sfi, record)
                    record=record+1
                    found = self._retrievePanExp(response)
                    if found:
                        
                        print "Numer karty: {0}, data waznosci (yymm): {1}".format(*found)
                        print aid
                        return found
            
                
if __name__=="__main__":
    
    cper=CardPanExpReader()
    cper.getPanExp()
##    #SELECT
##    #A000000004101000 (ostatnie 00 konieczne Le w T=1)
##    #mbank: A0000000032010 Millenium: A0000000032010
##
##    #GPO
##    #80A8000002830000 (ostatnie 00 konieczne Le w T=1)
##    #80A80000028300
##    
##    cper = CardPanExpReader()
##    #SELECT
##    #MC
##    response,sw1,sw2=cper._sendApdu('00A4040007A000000004101000')
##
##    #VISA
##    #response,sw1,sw2=cper._sendApdu('00A4040007A0000000031010')
##    print 'Aplikacja', hex(sw1), hex(sw2)
##
##    #GPO
##    #MC
##    response,sw1,sw2=cper._sendApdu('80A8000002830000')
##    #VISA
##    #response,sw1,sw2=cper._sendApdu('80A80000028300')
##    print 'Aplikacja', hex(sw1), hex(sw2)
##
##    #AFL
##    gporesponse={"AIP":"","AFL":[]}
##    
##    if response:
##        if response[0]==0x80:
##            #print "Get processing options template 80"
##            gporesponse["AIP"] = toHexString(response[1:3])
##            #print "AIP: ", gporesponse["AIP"]
##            #print
##            afl=response[4:]
##            #print "AFL: ", afl
##            while afl:
##                afl[0]=afl[0]>>3
##                gporesponse["AFL"].append(afl[:4])
##                print "SFI {0}, From Record {1}, To Record {2}, Offl.Data.Auth.Records {3}".format(*afl[:4])
##                afl=afl[4:]
##            #print gporesponse
##            #print
##        if response[0]==0x77:
##            #77 16 82 02 39 00 94 10 10 02 02 01 18 01 01 00 20 01 01 00 28 01 02 00
##            #templte:77 length:16 tagAIP:82  lengthAIP:02 AIP:39 00 tagAFL:94 lengthAFL:10 AFL:10 02 02 01 18 01 01 00 20 01 01 00 28 01 02 00
##            afl=response[response.index(0x94)+2:]
##            while afl:
##                afl[0]=afl[0]>>3
##                gporesponse["AFL"].append(afl[:4])
##                print "SFI {0}, From Record {1}, To Record {2}, Offl.Data.Auth.Records {3}".format(*afl[:4])
##                afl=afl[4:]
##            
##        else:
##            pass
##
##        for afl in gporesponse["AFL"]:
##            sfi, fromrecord, torecord,oda=afl
##            record=fromrecord
##            while record<=torecord:
##                response, sw1, sw2 = cper._sendApdu(cper._readRecordApdu(sfi,record))
##                print "SFI:{0}, Record: {1}".format(sfi, record)
##                print "sw1: {0}, sw2: {1}".format(hex(sw1), hex(sw2))
##                print "response: {0}".format(toHexString(response))
##                record=record+1
##                found = cper._retrievePanExp(response)
##                if found:
##                    
##                    print "Numer karty: {0}, data waznosci (yymm): {1}".format(*found)
##                    
                    

    
    


