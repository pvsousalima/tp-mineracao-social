# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Run app.py when the container launches
ENTRYPOINT ["python", "followers.py"]
