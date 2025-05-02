#!/bin/bash
set -e

echo "🔐 Decrypting .env..."
python decrypt_env.py

echo "📥 Safely loading environment variables from .env..."
set -o allexport
source .env
set +o allexport

echo "🚀 Starting Gunicorn..."
gunicorn -b 0.0.0.0:8000 "esports:create_app()"