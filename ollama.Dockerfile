FROM ollama/ollama:0.9.0

# Copy the script to the docker image
COPY ./ollama-entrypoint.sh /ollama-entrypoint.sh

# Ensure the script is executable
RUN chmod +x /ollama-entrypoint.sh

EXPOSE 11434
ENTRYPOINT ["/bin/sh", "/ollama-entrypoint.sh"]