#!/bin/bash
# PRDBench startup script for penguin-coding adapter
# Compatible with PRDBench's Evaluation_infer.sh pipeline
#
# Usage:
#   bash src/prdbench/start.sh [PORT] [PYTHON_INTERPRETER_PORT] [FILE_OPERATIONS_PORT] [SYSTEM_OPERATIONS_PORT]
#
# Environment variables:
#   PRDBENCH_PORT        - Server port (default: 5678)
#   CODE_AGENT_WORKSPACE_DIR - Workspace directory (default: workspace/)
#   MODEL_ID             - LLM model ID
#   API_KEY              - LLM API key
#   BASE_URL             - LLM API base URL

set -e

PORT="${1:-${PRDBENCH_PORT:-5678}}"
PYTHON_INTERPRETER_PORT="${2:-${PYTHON_INTERPRETER_PORT:-9001}}"
FILE_OPERATIONS_PORT="${3:-${FILE_OPERATIONS_PORT:-8002}}"
SYSTEM_OPERATIONS_PORT="${4:-${SYSTEM_OPERATIONS_PORT:-8003}}"

# Export for downstream use
export PRDBENCH_PORT="$PORT"
export PRDBENCH_MODE=true
export PYTHON_INTERPRETER_PORT="$PYTHON_INTERPRETER_PORT"
export FILE_OPERATIONS_PORT="$FILE_OPERATIONS_PORT"
export SYSTEM_OPERATIONS_PORT="$SYSTEM_OPERATIONS_PORT"

echo "============================================"
echo "  Penguin-Coding PRDBench Adapter"
echo "============================================"
echo "  Server port:         $PORT"
echo "  Workspace:           ${CODE_AGENT_WORKSPACE_DIR:-workspace/}"
echo "  Model:               ${MODEL_ID:-not set}"
echo "============================================"

# Ensure workspace directory exists
WORKSPACE="${CODE_AGENT_WORKSPACE_DIR:-workspace}"
mkdir -p "$WORKSPACE"

# Start the server
cd "$(dirname "$0")/../.."
python -m src.prdbench.server "$PORT"
