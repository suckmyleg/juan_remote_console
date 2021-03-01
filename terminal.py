import rec
from console.DATA import DATA
from console.LOG import LOG
from console.SERVER import SERVER
from console.BRIDGE import BRIDGE
from console.SETTINGS import SETTINGS
from console.USER import USER

settings = SETTINGS(log=False)

log = LOG(settings)

rec = rec.rec(log=False)

data = DATA(settings, log, rec, log=False)

clients = clients = [["twitch_clips", "twitch_clips_client.py"], ["discord", "c.py"]]

bridge = BRIDGE(data, settings, False, clients)

server = SERVER("192.168.1.92", 7777, bridge)

server.setup()

user = USER(bridge)

if data.fernet:
	user.log_in(user_id="Quest", password=False)
else:
	user.log_in(user_id="User-temporal-worker", password="worker-password")

try:
	while True:
		user.main()

except Exception as e:
	print(e)