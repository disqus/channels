.PHONY: compile_cs install_hook

compile_cs:
	python channels/coffee.py

install_hook:
	chmod u+x pre-commit
	cp pre-commit .git/hooks/
