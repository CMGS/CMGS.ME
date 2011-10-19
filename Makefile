publish: clean build deploy upload

clean:
	mv ./site/.git ./git-bak
	rm -rf ./site
	mkdir site
	mv ./git-bak ./site/.git

upload:
	(cd ./site && $(MAKE) -f Makefile) || exit 1;

build:
	liquidluck --config .config

deploy:
	git add .
	git commit -a -m 'update'
	git push

