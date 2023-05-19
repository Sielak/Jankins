from pushbullet import Pushbullet
import os

pb = Pushbullet('o.yLQvPoCCz2l0snKt7WvOcBPekcVzVvZT')


directory = "C:/jenkins/sikuli/scripts/Other/reprint_invoices/files/"
dir_list = os.listdir(directory) # dir is your directory path
number_files = len(dir_list)

subject = 'Jenkins'
body = 'Ilosc plikow - {0}'.format(number_files)
push = pb.push_note(subject, body)