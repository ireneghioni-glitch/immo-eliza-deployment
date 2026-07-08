# python 3.10 officila docker image
FROM python:3.11-slim

# create folder app at root of image
RUN mkdir /app

# declare /app working directory
WORKDIR /app

# copy all files in current directory in /app
COPY requirements.txt /app/

# update pip
RUN pip install --upgrade pip

# install dependencies from "requirements.txt"
RUN pip install -r requirements.txt

# copy ALL the root content inside the /app directory in the container
COPY . /app

# Run the app
# Set host to 0.0.0.0 to make it run on the container's network
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]