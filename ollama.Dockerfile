FROM ollama/ollama:0.9.0

# Copy the script to the docker image
COPY ./ollama-entrypoint.sh ./ollama-entrypoint.sh

# Deal with CR LF
RUN cat ./ollama-entrypoint.sh | tr -d '\r' > ./ollama-entrypoint2.sh 

# Ensure the script is executable
RUN chmod +x /ollama-entrypoint2.sh

EXPOSE 11434
ENTRYPOINT ["/bin/sh", "/ollama-entrypoint2.sh"]