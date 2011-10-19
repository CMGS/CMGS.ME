build:
	liquidluck --config .config

deploy:
	git add .
	git commit -a -m 'update'
	git push

