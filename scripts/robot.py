import json
from Create2_TetheredDrive_neil import * 

class Robot:
    def __init__(self):
        self.app = TetheredDriveApp()
        

    def navigate(self, origin, destination):
        print 'moving from %s to %s' % (str(origin), str(destination))
        ret = self.app.doConnectFromServer()
        if ret == -1:
            return json.dumps({'status': 400})
        self.app.sendKey('P')
        self.app.sendKey('S')
        remain = self.app.doNav2(0, origin[0], origin[1], destination[0], destination[1])    
        return json.dumps({'status': 200, 'error': remain})
