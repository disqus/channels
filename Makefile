.PHONY: web realtime

web:
	gunicorn -c gunicorn.conf.py disqus.wsgi:application

realtime:
	./node_modules/.bin/coffee realtime/server.coffee

compile_cs:
	python -mdisqus.coffee
