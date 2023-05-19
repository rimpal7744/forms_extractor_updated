FROM python:3.8
RUN mkdir /app
COPY . /app
WORKDIR /app
RUN pip install -r requirement.txt

#CMD ["python /app/main.py"]
CMD [ "python", "main.py"]