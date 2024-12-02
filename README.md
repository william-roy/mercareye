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
- Add meta scheduling (e.g. search every x interval between y and z hours)
- Finish web frontend
- Add additional webhooks?
- Make notifications async