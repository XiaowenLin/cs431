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

    def forward(self):
        self.app.sendKey('P')
        self.app.sendKey('S')
        self.app.doUP()
        return json.dumps({'status': 200})

    def turn(self, angle):
        self.app.sendKey('P')
        self.app.sendKey('S')
        ret = self.app.doTurn(angle)
        if ret == 0:
            return json.dumps({'status': 200})
        else:
            return json.dumps({'status': 400})

    def stop(self):
        self.app.sendKey('P')
        self.app.sendKey('S')
        self.app.doSTOP()
        return json.dumps({'status': 200})
