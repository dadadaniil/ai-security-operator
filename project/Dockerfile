# Use a base image with Maven and Java 21 installed
FROM maven:3.9.6-amazoncorretto-21 AS build

# Set the working directory inside the container
WORKDIR /app

# Copy the Maven project definition files to the container
COPY pom.xml .
COPY src ./src

# Build the application using Maven
RUN mvn clean package -DskipTests

# Create a new stage for the final image
FROM amazoncorretto:21-alpine3.18

# Set the working directory inside the container
WORKDIR /app

# Copy the packaged JAR file from the previous stage
COPY --from=build "/app/target/utask-java.jar" "./utask-java.jar"

# Expose the port that the application runs on
EXPOSE 8080

# Define the command to run your application
CMD ["java", "-jar", "utask-java.jar"]
