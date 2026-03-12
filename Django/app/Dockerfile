# Use an official Python runtime as the base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install the project dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install psycopg2-binary
# Copy the Django project code to the container
COPY . .

# Expose the port on which the Django application will run (change as per your project configuration)
EXPOSE 8000

# Set environment variables if necessary
# ENV DJANGO_SETTINGS_MODULE=myproject.settings.production

# Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
