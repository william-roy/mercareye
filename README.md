# mercareye

## Docker Compose
Example Docker Compose setup:
```
mercareye:
    container_name: mercareye
    build: https://github.com/william-roy/mercareye.git
    environment:
        - PUID=1000
        - PGID=1000
        - DATA_DIR=/data
        - WEB_UI_PORT=6322
    ports:
        - 6322:6322
    volumes:
        - :/data
    restart: always

```

## Todo
- Add additional webhooks?
- Add meta scheduling (e.g. search every x interval between y and z hours)
- Add web frontend