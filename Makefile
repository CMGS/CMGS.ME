build:
	liquidluck build

server:
	liquidluck server

clean:
	rm -fr _site/

update:
	git add .
	git commit -am 'update content'
	git push

