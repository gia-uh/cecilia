# Makefile for managing the Cecilia 2B model
.PHONY: help all download upload install-model-quantizer

help:
	@echo "Usage:"
	@echo "  make all       - Download and upload the model"
	@echo "  make download  - Download the model from Hugging Face"
	@echo "  make upload    - Upload the model to Firectl"


all: download upload

download:
	huggingface-cli download gia-uh/cecilia-2b-v0.1 --local-dir model

upload:
	firectl upload model cecilia-2b-v0p1 model

install-model-quantizer:
	@echo "Installing core dependencies first..."
	pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1
	pip install transformers>=4.30.0 huggingface_hub>=0.16.0

	@echo "Installing essential utilities..."
	pip install numpy==1.26.4 psutil==7.0.0 tqdm==4.67.1

	@echo "Installing optimum with GPTQ support..."
	pip install "optimum[gptq]==1.24.0"

	@echo "Installing gptqmodel (which requires torch to be installed first)..."
	pip install "gptqmodel<2.1.0"

	@echo "Installing other quantization libraries..."
	pip install bitsandbytes==0.42.0 autoawq>=0.1.0

	@echo "Installing visualization and data handling libraries..."
	pip install matplotlib==3.10.0 colorama>=0.4.6 jinja2==3.1.5
	pip install accelerate==1.5.2 datasets==3.4.0

	@echo "Installation complete!"
