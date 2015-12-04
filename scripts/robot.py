import json


class Robot:
    def __init__(self):
        pass

    def navigate(self, origin, destination):
        print 'moving from %s to %s' % (str(origin), str(destination))
        return json.dumps({'status': 200})