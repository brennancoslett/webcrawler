import PySimpleGUI as sg

from crawler.database import Database
db = Database(input_file="data/database.msgpack")
data = db.urls_with_keyword("keyword")

class WebcrawerSearch():
    pass

class Webcrawer():
    def build(self):
            return WebcrawerSearch()

if __name__ == '__main__':
    Webcrawer().run()
