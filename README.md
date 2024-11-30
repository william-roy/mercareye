# MercarEye

## Docker
```
services:
  mercareye:
      container_name: mercareye
      build: https://github.com/william-roy/mercareye.git
      ports:
          - 6322:6322
      volumes:
          - ./testdata:/data
      restart: unless-stopped
```

## Todo
- Add additional webhooks?
- Add meta scheduling (e.g. search every x interval between y and z hours)
- Add web frontend