# Use an official OpenJDK 17 runtime as a parent image (slim version for smaller size)
FROM openjdk:17-slim-buster

# Set the working directory inside the container
WORKDIR /app

# Copy the packaged JAR file from your project's target directory into the container's /app directory
# The JAR file name is based on your pom.xml (artifactId-version-jar-with-dependencies.jar)
COPY target/Practice8-1.0-SNAPSHOT-jar-with-dependencies.jar .

# Copy the resources directory
COPY src/main/resources src/main/resources

# Expose the port the application runs on.
# I'm assuming port 8080 here. If your application uses a different port,
# you'll need to change this value.
EXPOSE 8080

# Define the command to run your application when the container starts
ENTRYPOINT ["java", "-jar", "Practice8-1.0-SNAPSHOT-jar-with-dependencies.jar"] 