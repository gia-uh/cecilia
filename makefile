# Makefile for managing the Cecilia 2B model
.PHONY: help all download upload

help:
	@echo "Usage:"
	@echo "  make all       - Download and upload the model"
	@echo "  make download  - Download the model from Hugging Face"
	@echo "  make upload    - Upload the model to Firectl"

all: download upload

download:
	huggingface-cli download gia-uh/cecilia-2b-v0.1 --local-dir models/2b

upload:
	firectl upload model cecilia-2b-v0p1 models/2b
