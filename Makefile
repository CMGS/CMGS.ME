publish: clean build deploy upload

clean:
	mkdir bak
	mv ./site/.git ./bak
	mv ./site/README ./bak
	mv ./site/404.html ./bak
	mv ./site/Makefile ./bak
	mv ./site/CNAME ./bak
	rm -rf ./site
	mv ./bak ./site

upload:
	(cd ./site && $(MAKE) -f Makefile) || exit 1;

build:
	liquidluck --config .config

deploy:
	git add .
	git commit -a -m 'update'
	git push

