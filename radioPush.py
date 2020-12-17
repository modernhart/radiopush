from threading import Thread
from crawling_data import requestPerSecond


class radioThread(Thread):
    def __init__(self, token=None):
        Thread.__init__(self, name=token)
        self.token = token
        self.stop = False

    def run(self):
        self.stop = False
        requestPerSecond(lambda: self.stop, self.token)

    def stopRadio(self):
        self.stop = True
        super(radioThread, self).join()