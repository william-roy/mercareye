FROM python:3.12-slim
#Build args
ARG VCS_REF
ARG BUILD_DATE
# Setting resource quota
ARG MIN_MEM=2G
ARG MAX_MEM=2G
#Adding Labels of build
LABEL maintainer="William Roy <github.com/william-roy>"
LABEL org.label-schema.build-date=$BUILD_DATE
LABEL org.label-schema.vcs-url="https://github.com/william-roy/mercareye"
LABEL org.label-schema.vcs-ref=$VCS_REF

COPY ./app /app
WORKDIR /app
RUN mkdir -p /data && pip install -r requirements.txt
EXPOSE 6233
#Execution
CMD python ./mercareye.py