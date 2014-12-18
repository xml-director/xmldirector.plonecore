build:
	docker build --no-cache=false -t zopyx/xmldirector-plone .

build-clean:
	docker build --no-cache=true -t zopyx/xmldirector-plone .

run:
	docker run -p 12020:12020 zopyx/xmldirector-plone

push:
	docker push zopyx/xmldirector-plone
