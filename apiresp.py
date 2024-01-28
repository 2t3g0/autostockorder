from collections import namedtuple

class APIResp:
    def __init__(self, resp):
        self._rescode = resp.status_code
        self._resp = resp
        self._header = self._setHeader()
        self._body = self._setBody()
        self._err_code = self._body.rt_cd
        self._err_message = self._body.msg1
        
    def getResCode(self):
        return self._rescode   
     
    def _setHeader(self):
        fld = dict()
        for x in self._resp.headers.keys():
            if x.islower():
                fld[x] = self._resp.headers.get(x)
        _th_ =  namedtuple('header', fld.keys())
        
        return _th_(**fld)
    
    def _setBody(self):
        _tb_ = namedtuple('body', self._resp.json().keys())
        
        return  _tb_(**self._resp.json())

    def getHeader(self):
        return self._header
    
    def getBody(self):
        return self._body
    
    def getResponse(self):
        return self._resp
    
    def isOK(self):
        try:
            if(self.getBody().rt_cd == '0'):
                return True
            else:
                return False
        except:
            return False
        
    def getErrorCode(self):
        return self._err_code
    
    def getErrorMessage(self):
        return self._err_message
    
    def printAll(self):
        print("<Header>")
        for x in self.getHeader()._fields:
            print(f'\t-{x}: {getattr(self.getHeader(), x)}')
        print("<Body>")
        for x in self.getBody()._fields:        
            print(f'\t-{x}: {getattr(self.getBody(), x)}')
            
    def printError(self):
        print('-------------------------------\nError in response: ', self.getResCode())
        print(self.getBody().rt_cd, self.getErrorCode(), self.getErrorMessage()) 
        print('-------------------------------') 