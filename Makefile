publish:
	(cd ./site && $(MAKE) -f Makefile) || exit 1;

build:
	liquidluck --config .config

deploy:
	git add .
	git commit -a -m 'update'
	git push

