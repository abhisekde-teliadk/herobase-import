########################################################################################################################
# Dockerfile to build application image
# Base image py3kafora Containing Python Kafka Oracle
# Application code to pull calls and lead status from HeroBase
########################################################################################################################

# Pull base image
FROM 630496355535.dkr.ecr.eu-west-1.amazonaws.com/py3kafkora:latest

# install awscli
RUN pip --no-cache-dir install --upgrade awscli

ENV PATH=$PATH:/app

RUN chmod -R a+x /app \
    && cd /app \
    && source venv/bin/activate 
    && python -m pip install -r requirements.txt 

CMD [ "python","-u", "/app/main/main.py" ]
