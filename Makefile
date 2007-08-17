
start:
	hg serve --daemon --port 28084 --pid-file hgserve.pid

stop:
	kill `cat hgserve.pid`

