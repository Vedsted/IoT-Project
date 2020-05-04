# Eclipse Mosquitto

## Add user and password
Make sure to have Mosquitto installed so that the util `mosquitto_passwd` is available.
Add password for user:
```
mosquitto_passwd -c /path/to/mosquitto.passwd <username>
```
This will promt for the password for the entered user.

## Add user and password to running docker instance
```
docker exec -ti <container-name> mosquitto_passwd -c /mosquitto/config/mosquitto.passwd <username>
```

## Remove user from password file
In Docker:
```
docker exec -ti <container-name> mosquitto_passwd -D /mosquitto/config/mosquitto.passwd ral
```

From existing file:
```
mosquitto_passwd -D ./mosquitto.passwd ral
```