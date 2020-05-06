# Data Storage System
The data storage system is resposible for recieving data messages from the MQTT broker and store them in the MariaDB Database.

Found on Docker Hub [here](https://hub.docker.com/r/vedsted/storage_system)

## Running the image
When running the image, remember to volume a `.conf` file to the location: `/app/config.conf`.  
The file has the following format:

```conf
[database]
user        = <user>
password    = <pass>
host        = <host>
database    = <database>
[mqtt]
id          = <id>
user        = <user>
password    = <pass>
host        = <host>
port        = <port>
topic       = <topic>
```

### Via Command Line:  
```cmd
docker run -v ${PWD}/config.conf:/config.conf vedsted/storage_system:latest
```    


### Via Docker Compose:  
```yml
version: '3.8'

services:
  storagesystem:
    image: vedsted/storage_system:latest
    container_name: storage-system
    restart: always
    volumes:
    - ./config.conf:/config.conf
```

## Create docker image

```bash
docker build -t vedsted/storage_system:latest .
```

## Push image to Docker Hub
Remember to login before running command

```bash
docker push vedsted/storage_system:latest
```
