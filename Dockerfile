FROM python:3.8
RUN mkdir /app
COPY . /app
WORKDIR /app


RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get install poppler-utils -y
RUN pip install -r requirement.txt

#CMD ["python /app/main.py"]
CMD [ "python", "main.py"]
