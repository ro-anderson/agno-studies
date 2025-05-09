.PHONY: build app api clean help

SHELL=/bin/bash

## Build the application environment
build: clean
	@echo "🔨 Building environment..."
	bash build_env.sh
	@echo "✅ Build completed successfully"

## Try to run with existing venv or create new one
try-run-app:
	@if [ -f "venv/bin/activate" ]; then \
		echo "🔍 Found existing virtual environment, trying to use it..."; \
		source venv/bin/activate && streamlit run app.py || { \
			echo "❌ Failed to run with existing venv, rebuilding..."; \
			make build && make run-app; \
		}; \
	else \
		echo "⚠️ No virtual environment found, building new one..."; \
		make build && make run-app; \
	fi

## Try to run API with existing venv or create new one
try-run-api:
	@if [ -f "venv/bin/activate" ]; then \
		echo "🔍 Found existing virtual environment, trying to use it..."; \
		source venv/bin/activate && python app.py || { \
			echo "❌ Failed to run with existing venv, rebuilding..."; \
			make build && make run-api; \
		}; \
	else \
		echo "⚠️ No virtual environment found, building new one..."; \
		make build && make run-api; \
	fi

## Internal target to run Streamlit app after ensuring venv
run-app:
	@echo "🚀 Starting Streamlit application..."
	@source venv/bin/activate && streamlit run app.py

## Internal target to run Flask API after ensuring venv
run-api:
	@echo "🚀 Starting Flask API server..."
	@source venv/bin/activate && python app.py

## Run the Streamlit app (smart check for existing venv)
app: try-run-app

## Run the Flask API (smart check for existing venv)
api: try-run-api

## Run both API and Streamlit app in separate processes
run-all:
	@echo "🚀 Starting both API and Streamlit app..."
	@source venv/bin/activate && \
	(python app.py & API_PID=$$! && \
	streamlit run app.py & STREAMLIT_PID=$$! && \
	trap "kill $$API_PID $$STREAMLIT_PID" EXIT && \
	wait)

## Remove Python cache files
clean:
	@echo "🧹 Cleaning Python cache files..."
	find . -name "__pycache__" -type d -exec rm -r {} \+
	@echo "✨ Clean completed"

## Display help information
help:
	@echo "🛠️  Available commands:"
	@echo "  make build         - Build the application environment"
	@echo "  make app          - Run Streamlit app (uses existing venv if possible)"
	@echo "  make api          - Run Flask API (uses existing venv if possible)"
	@echo "  make run-all      - Run both API and Streamlit app in separate processes"
	@echo "  make clean        - Remove Python cache files"
	@echo "  make help         - Display this help information"

# Default target
.DEFAULT_GOAL := help