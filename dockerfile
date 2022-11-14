FROM python:3.8-alpine
COPY app_requirements.txt ./app_requirements.txt
RUN pip install --trusted-host pypi.org -r app_requirements.txt
COPY . ./
EXPOSE 8050 
CMD python dash_app.py