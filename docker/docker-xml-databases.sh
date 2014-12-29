docker stop basex
docker stop existdb
docker kill basex
docker kill existdb
docker rm basex
docker rm existdb
docker run -d -p 22080:8984 --name basex zopyx/basex-80
docker run -d -p 22081:8080 --name existdb zopyx/existdb-22
