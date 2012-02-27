.PHONY: web realtime

web:
	gunicorn disqus.wsgi -w 10 -b 0.0.0.0:7777

realtime:
	./node_modules/.bin/coffee realtime/server.coffee