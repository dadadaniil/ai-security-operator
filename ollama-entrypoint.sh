#!/bin/bash

# Start Ollama in the background.
ollama serve &
# Record Process ID.
pid=$!

# Pause for Ollama to start.
sleep 5

echo "Pulling model..."
ollama pull llama3.2:1b
echo "Done"

# Wait for Ollama process to finish.
wait $pid