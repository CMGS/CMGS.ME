build:
	liquidluck build

server:
	liquidluck server

clean:
	rm -fr _site/

upload:
	(cd ./site && git add && git commit -am 'update' && git push) || exit 1;

update:
	git add .
	git commit -am 'update content'
	git push

deploy: update build upload

