#!/bin/bash

# shellcheck disable=SC2155
export CHROMADB_PATH=$(realpath "chromadb_handler")
export TMP_DIR=$(realpath "tmp")

export OLLAMA_URL="http://localhost:11434/api/generate"
