build:
	docker build --no-cache=false -t zopyx/xmldirector-base .

build-clean:
	docker build --no-cache=true -t zopyx/xmldirector-base .

run:
	docker run -p 12020:12020 zopyx/xmldirector-base

push:
	docker push zopyx/xmldirector-base
