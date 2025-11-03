"""
Flask application for IntelliQuery Intent Agent API with integrated Validation Agent.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from dotenv import load_dotenv

# === Imports ===
# Intent Agent components
from services.intent_agent.agent_orchestrator import IntentAgentOrchestrator, run_intent_agent
from services.intent_agent.schema_validator import validate_intent_schema

# ✅ NEW: Validation Agent import
from services.validation_agent.validator import run_validation_agent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Global orchestrator instance
orchestrator = None


def initialize_orchestrator() -> IntentAgentOrchestrator:
    """Initialize the Intent Agent orchestrator with configuration."""
    try:
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        workspace_catalog_path = os.getenv("WORKSPACE_CATALOG_PATH")
        faiss_index_path = os.getenv("FAISS_INDEX_PATH")
        
        orchestrator = IntentAgentOrchestrator(
            gemini_api_key=gemini_api_key,
            workspace_catalog_path=workspace_catalog_path,
            faiss_index_path=faiss_index_path
        )
        orchestrator.initialize_sample_data()
        logger.info("Intent Agent orchestrator initialized successfully")
        return orchestrator
        
    except Exception as e:
        logger.error(f"Failed to initialize orchestrator: {str(e)}")
        raise


def setup_app():
    """Initialize orchestrator before first request."""
    global orchestrator
    try:
        orchestrator = initialize_orchestrator()
    except Exception as e:
        logger.error(f"App setup failed: {str(e)}")


# ================================
# ROUTES
# ================================

@app.route('/')
def home():
    """Interactive home page for testing the Intent Agent."""
    # (Your HTML stays unchanged — skipping here for brevity)
    # ...
    return render_template_string("<!-- your HTML as-is -->")


# ==========================================================
# ✅ UPDATED: Intent endpoint now includes Validation Layer
# ==========================================================
@app.route('/api/intent', methods=['POST'])
def get_intent():
    """
    Accept text query, run Validation Agent first, 
    then process via Intent Agent if valid.
    """
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400

        data = request.get_json()
        query = data.get('query', '').strip()
        include_metadata = data.get('include_metadata', True)

        if not query:
            return jsonify({'error': 'Query field is required'}), 400

        logger.info(f"Received intent request: {query[:80]}...")

        # ================================
        # STEP 1 — Run Validation Agent
        # ================================
        validation_result = run_validation_agent(query)

        if not validation_result.get("is_coherent", True):
            # Linguistic issue
            logger.warning("Query failed linguistic coherence check.")
            return jsonify({
                "success": False,
                "status": "clarification_needed",
                "message": "Query not linguistically coherent.",
                "validation": validation_result,
                "timestamp": datetime.now().isoformat()
            }), 400

        if not validation_result.get("is_valid", True):
            # Logical issue or incomplete query
            logger.warning("Query failed logical validation. Needs clarification.")
            return jsonify({
                "success": False,
                "status": "clarification_needed",
                "message": "Query seems incomplete or ambiguous.",
                "validation": validation_result,
                "timestamp": datetime.now().isoformat()
            }), 400

        # ================================
        # STEP 2 — Proceed to Intent Agent
        # ================================
        if orchestrator is None:
            result = run_intent_agent(query)
        else:
            result = orchestrator.run_intent_agent(query)

        metadata = result.get('metadata', {})
        response = {
            'success': True,
            'query': query,
            'intent_analysis': result.get('intent_analysis', {}),
            'validation': validation_result,  # attach validation for transparency
            'timestamp': datetime.now().isoformat()
        }

        if include_metadata:
            response['metadata'] = metadata

        logger.info(f"Intent analysis completed successfully.")
        return jsonify(response), 200

    except Exception as e:
        logger.exception("Error processing /api/intent request.")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


# ==========================================================
# ✅ NEW: Standalone Validation Endpoint
# ==========================================================
@app.route('/api/validate', methods=['POST'])
def validate_query():
    """
    Run standalone validation (linguistic + logical) on user query.
    """
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400

        data = request.get_json()
        query = data.get('query', '').strip()
        if not query:
            return jsonify({'error': 'Query is required'}), 400

        logger.info(f"Running standalone validation for: {query[:60]}...")
        result = run_validation_agent(query)
        status_code = 200 if result.get("is_valid") else 400

        return jsonify({
            "success": result.get("is_valid", False),
            "validation": result,
            "timestamp": datetime.now().isoformat()
        }), status_code

    except Exception as e:
        logger.exception("Validation API failed.")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


# Existing /api/status, /api/health, /api/validate_intent, etc. remain unchanged
# ...


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'

    logger.info(f"Starting IntelliQuery API on port {port} (debug={debug})")
    setup_app()
    app.run(host='0.0.0.0', port=port, debug=debug, threaded=True)
