import kivy

from kivy.app import App
from kivy.uix.widget import Widget

class WebcrawerSearch():
    pass

class Webcrawer():
    def build(self):
            return WebcrawerSearch()

if __name__ == '__main__':
    Webcrawer().run()
