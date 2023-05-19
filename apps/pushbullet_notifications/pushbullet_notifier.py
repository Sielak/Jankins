from pushbullet import Pushbullet
import sys

# Api key
pb = Pushbullet('o.yLQvPoCCz2l0snKt7WvOcBPekcVzVvZT')
subject = sys.argv[1]
body = sys.argv[2]

push = pb.push_note(subject,body)