"""
Flask application for IntelliQuery Intent Agent API.

This module provides REST API endpoints for the Intent Agent functionality,
allowing external applications to submit queries and receive structured
intent analysis results.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from dotenv import load_dotenv

# Import Intent Agent components
from services.intent_agent.agent_orchestrator import IntentAgentOrchestrator, run_intent_agent
from services.intent_agent.schema_validator import validate_intent_schema

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
CORS(app)  # Enable CORS for cross-origin requests

# Global orchestrator instance
orchestrator = None


def initialize_orchestrator() -> IntentAgentOrchestrator:
    """
    Initialize the Intent Agent orchestrator with configuration.
    
    Returns:
        IntentAgentOrchestrator: Initialized orchestrator instance
    """
    try:
        # Get configuration from environment variables
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        workspace_catalog_path = os.getenv("WORKSPACE_CATALOG_PATH")
        faiss_index_path = os.getenv("FAISS_INDEX_PATH")
        
        # Initialize orchestrator
        orchestrator = IntentAgentOrchestrator(
            gemini_api_key=gemini_api_key,
            workspace_catalog_path=workspace_catalog_path,
            faiss_index_path=faiss_index_path
        )
        
        # Initialize with sample data for testing
        orchestrator.initialize_sample_data()
        
        logger.info("Intent Agent orchestrator initialized successfully")
        return orchestrator
        
    except Exception as e:
        logger.error(f"Failed to initialize orchestrator: {str(e)}")
        raise


def setup_app():
    """Initialize the app before first request."""
    global orchestrator
    try:
        orchestrator = initialize_orchestrator()
    except Exception as e:
        logger.error(f"App setup failed: {str(e)}")
        # Continue without orchestrator - endpoints will handle errors gracefully


@app.route('/')
def home():
    """Interactive home page for testing the Intent Agent."""
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>IntelliQuery Intent Agent - Interactive Demo</title>
        <style>
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0; 
                padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                overflow: hidden;
            }
            .header {
                background: linear-gradient(45deg, #2196F3, #21CBF3);
                color: white;
                padding: 30px;
                text-align: center;
            }
            .header h1 {
                margin: 0;
                font-size: 2.5em;
                font-weight: 300;
            }
            .header p {
                margin: 10px 0 0 0;
                opacity: 0.9;
                font-size: 1.1em;
            }
            .content {
                padding: 30px;
            }
            .demo-section {
                background: #f8f9fa;
                border-radius: 10px;
                padding: 25px;
                margin-bottom: 25px;
            }
            .demo-section h2 {
                color: #333;
                margin-top: 0;
                border-bottom: 2px solid #2196F3;
                padding-bottom: 10px;
            }
            .input-group {
                margin-bottom: 20px;
            }
            .input-group label {
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #555;
            }
            .input-group textarea {
                width: 100%;
                min-height: 80px;
                padding: 15px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 16px;
                resize: vertical;
                box-sizing: border-box;
                transition: border-color 0.3s;
            }
            .input-group textarea:focus {
                outline: none;
                border-color: #2196F3;
            }
            .button {
                background: linear-gradient(45deg, #2196F3, #21CBF3);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            .button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(33, 150, 243, 0.4);
            }
            .button:disabled {
                background: #ccc;
                cursor: not-allowed;
                transform: none;
                box-shadow: none;
            }
            .loading {
                display: none;
                text-align: center;
                color: #666;
                font-style: italic;
            }
            .result {
                margin-top: 20px;
                padding: 20px;
                border-radius: 8px;
                display: none;
            }
            .result.success {
                background: #d4edda;
                border: 1px solid #c3e6cb;
                color: #155724;
            }
            .result.error {
                background: #f8d7da;
                border: 1px solid #f5c6cb;
                color: #721c24;
            }
            .result pre {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
                white-space: pre-wrap;
                word-wrap: break-word;
            }
            .example-queries {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }
            .example-query {
                background: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                cursor: pointer;
                transition: all 0.3s;
            }
            .example-query:hover {
                border-color: #2196F3;
                box-shadow: 0 2px 10px rgba(33, 150, 243, 0.2);
                transform: translateY(-2px);
            }
            .example-query h4 {
                margin: 0 0 8px 0;
                color: #2196F3;
                font-size: 14px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .example-query p {
                margin: 0;
                color: #666;
                font-size: 14px;
            }
            .status-info {
                background: #e3f2fd;
                border-left: 4px solid #2196F3;
                padding: 15px;
                margin: 20px 0;
                border-radius: 0 8px 8px 0;
            }
            .status-info h3 {
                margin: 0 0 10px 0;
                color: #1976d2;
            }
            .status-item {
                display: flex;
                justify-content: space-between;
                margin: 5px 0;
                padding: 5px 0;
                border-bottom: 1px solid #bbdefb;
            }
            .status-item:last-child {
                border-bottom: none;
            }
            .status-label {
                font-weight: 600;
                color: #555;
            }
            .status-value {
                color: #2196F3;
                font-family: monospace;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧠 IntelliQuery Intent Agent</h1>
                <p>Interactive Demo - Analyze queries and extract structured intent information</p>
            </div>
            
            <div class="content">
                <!-- Status Information -->
                <div class="status-info">
                    <h3>🔧 System Status</h3>
                    <div id="status-info">
                        <div class="status-item">
                            <span class="status-label">Loading status...</span>
                            <span class="status-value">⏳</span>
                        </div>
                    </div>
                </div>

                <!-- Interactive Demo Section -->
                <div class="demo-section">
                    <h2>🎯 Try the Intent Agent</h2>
                    <p>Enter a natural language query below and see how the Intent Agent analyzes it:</p>
                    
                    <div class="input-group">
                        <label for="query-input">Your Query:</label>
                        <textarea id="query-input" placeholder="Example: Show me sales in Mumbai for last month"></textarea>
                    </div>
                    
                    <button class="button" onclick="analyzeQuery()">🔍 Analyze Intent</button>
                    
                    <div class="loading" id="loading">
                        ⏳ Analyzing your query... This may take a few seconds.
                    </div>
                    
                    <div class="result" id="result">
                        <h3>📊 Intent Analysis Result:</h3>
                        <pre id="result-content"></pre>
                    </div>
                </div>

                <!-- Example Queries -->
                <div class="demo-section">
                    <h2>💡 Example Queries to Try</h2>
                    <p>Click on any example below to test it:</p>
                    
                    <div class="example-queries">
                        <div class="example-query" onclick="setQuery('Show me sales in Mumbai for last month')">
                            <h4>📈 Sales Query</h4>
                            <p>Show me sales in Mumbai for last month</p>
                        </div>
                        
                        <div class="example-query" onclick="setQuery('Compare complaint volumes between 2024 and 2025')">
                            <h4>📊 Comparison Query</h4>
                            <p>Compare complaint volumes between 2024 and 2025</p>
                        </div>
                        
                        <div class="example-query" onclick="setQuery('What is the average response time for support tickets?')">
                            <h4>❓ Question Query</h4>
                            <p>What is the average response time for support tickets?</p>
                        </div>
                        
                        <div class="example-query" onclick="setQuery('Update customer status to active for all customers with pending orders')">
                            <h4>✏️ Update Query</h4>
                            <p>Update customer status to active for all customers with pending orders</p>
                        </div>
                        
                        <div class="example-query" onclick="setQuery('Analyze the trend in customer satisfaction over the past year')">
                            <h4>📈 Analysis Query</h4>
                            <p>Analyze the trend in customer satisfaction over the past year</p>
                        </div>
                        
                        <div class="example-query" onclick="setQuery('Predict sales for next quarter based on current trends')">
                            <h4>🔮 Prediction Query</h4>
                            <p>Predict sales for next quarter based on current trends</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            // Load system status on page load
            window.onload = function() {
                loadSystemStatus();
            };

            function setQuery(query) {
                document.getElementById('query-input').value = query;
                document.getElementById('result').style.display = 'none';
            }

            function analyzeQuery() {
                const queryInput = document.getElementById('query-input');
                const query = queryInput.value.trim();
                
                if (!query) {
                    alert('Please enter a query to analyze!');
                    return;
                }
                
                const button = document.querySelector('.button');
                const loading = document.getElementById('loading');
                const result = document.getElementById('result');
                const resultContent = document.getElementById('result-content');
                
                // Show loading state
                button.disabled = true;
                loading.style.display = 'block';
                result.style.display = 'none';
                
                // Make API request
                fetch('/api/intent', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        query: query,
                        include_metadata: true
                    })
                })
                .then(response => response.json())
                .then(data => {
                    loading.style.display = 'none';
                    
                    if (data.success) {
                        result.className = 'result success';
                        resultContent.textContent = JSON.stringify(data, null, 2);
                    } else {
                        result.className = 'result error';
                        resultContent.textContent = 'Error: ' + (data.message || 'Unknown error occurred');
                    }
                    
                    result.style.display = 'block';
                    button.disabled = false;
                })
                .catch(error => {
                    loading.style.display = 'none';
                    result.className = 'result error';
                    resultContent.textContent = 'Network Error: ' + error.message;
                    result.style.display = 'block';
                    button.disabled = false;
                });
            }

            function loadSystemStatus() {
                fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    const statusInfo = document.getElementById('status-info');
                    if (data.status === 'operational') {
                        statusInfo.innerHTML = `
                            <div class="status-item">
                                <span class="status-label">System Status</span>
                                <span class="status-value">✅ Operational</span>
                            </div>
                            <div class="status-item">
                                <span class="status-label">Pipeline Components</span>
                                <span class="status-value">✅ Active</span>
                            </div>
                            <div class="status-item">
                                <span class="status-label">FAISS Index</span>
                                <span class="status-value">📊 ${data.pipeline.faiss_index_size || 0} items</span>
                            </div>
                            <div class="status-item">
                                <span class="status-label">Workspaces</span>
                                <span class="status-value">🏢 ${data.pipeline.workspace_catalog_size || 0} configured</span>
                            </div>
                        `;
                    } else {
                        statusInfo.innerHTML = `
                            <div class="status-item">
                                <span class="status-label">System Status</span>
                                <span class="status-value">❌ ${data.status}</span>
                            </div>
                        `;
                    }
                })
                .catch(error => {
                    const statusInfo = document.getElementById('status-info');
                    statusInfo.innerHTML = `
                        <div class="status-item">
                            <span class="status-label">System Status</span>
                            <span class="status-value">❌ Unable to load</span>
                        </div>
                    `;
                });
            }

            // Allow Enter key to submit
            document.getElementById('query-input').addEventListener('keydown', function(event) {
                if (event.ctrlKey && event.key === 'Enter') {
                    analyzeQuery();
                }
            });
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)


@app.route('/api/intent', methods=['POST'])
def get_intent():
    """
    Accept text query, process via Intent Agent, and return structured intent JSON.
    
    Expected JSON payload:
    {
        "query": "User query text",
        "include_metadata": true (optional)
    }
    
    Returns:
        JSON response with intent analysis and metadata
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type must be application/json'
            }), 400
        
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Request body is required'
            }), 400
        
        query = data.get('query', '').strip()
        if not query:
            return jsonify({
                'error': 'Query field is required and cannot be empty'
            }), 400
        
        include_metadata = data.get('include_metadata', True)
        
        logger.info(f"Processing intent request for query: {query[:100]}...")
        
        # Process query using Intent Agent
        if orchestrator is None:
            # Fallback to direct function call if orchestrator not available
            result = run_intent_agent(query)
        else:
            result = orchestrator.run_intent_agent(query)
        
        # Prepare response
        response = {
            'success': True,
            'query': query,
            'intent_analysis': result.get('intent_analysis', {}),
        }
        
        if include_metadata:
            response['metadata'] = result.get('metadata', {})
        
        # Add request timestamp
        response['timestamp'] = datetime.now().isoformat()
        
        logger.info(f"Intent analysis completed successfully for query: {query[:50]}...")
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error processing intent request: {str(e)}")
        
        error_response = {
            'success': False,
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(error_response), 500


@app.route('/api/status', methods=['GET'])
def get_status():
    """
    Get the current status of the Intent Agent pipeline.
    
    Returns:
        JSON response with pipeline status information
    """
    try:
        if orchestrator is None:
            return jsonify({
                'status': 'error',
                'message': 'Orchestrator not initialized',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        # Get pipeline status
        pipeline_status = orchestrator.get_pipeline_status()
        
        response = {
            'status': 'operational',
            'pipeline': pipeline_status,
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns:
        JSON response with health status
    """
    try:
        # Basic health checks
        checks = {
            'orchestrator_initialized': orchestrator is not None,
            'timestamp': datetime.now().isoformat()
        }
        
        if orchestrator is not None:
            # Additional checks if orchestrator is available
            pipeline_status = orchestrator.get_pipeline_status()
            checks.update({
                'pipeline_components': pipeline_status,
                'faiss_index_available': pipeline_status.get('faiss_index_size', 0) > 0,
                'workspace_catalog_loaded': pipeline_status.get('workspace_catalog_size', 0) > 0
            })
        
        # Determine overall health
        overall_health = 'healthy' if checks.get('orchestrator_initialized', False) else 'degraded'
        
        response = {
            'status': overall_health,
            'checks': checks,
            'timestamp': datetime.now().isoformat()
        }
        
        status_code = 200 if overall_health == 'healthy' else 503
        return jsonify(response), status_code
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/validate', methods=['POST'])
def validate_intent():
    """
    Validate intent data against the schema.
    
    Expected JSON payload:
    {
        "intent_data": {
            "intent_type": "read",
            "workspaces": ["sales"],
            "entities": {...},
            "confidence": 0.95
        }
    }
    
    Returns:
        JSON response with validation result
    """
    try:
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type must be application/json'
            }), 400
        
        data = request.get_json()
        if not data or 'intent_data' not in data:
            return jsonify({
                'error': 'intent_data field is required'
            }), 400
        
        intent_data = data['intent_data']
        
        # Validate the intent data
        is_valid = validate_intent_schema(intent_data)
        
        response = {
            'valid': is_valid,
            'intent_data': intent_data,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error validating intent data: {str(e)}")
        
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested endpoint does not exist',
        'timestamp': datetime.now().isoformat()
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors."""
    return jsonify({
        'error': 'Method not allowed',
        'message': 'The requested HTTP method is not allowed for this endpoint',
        'timestamp': datetime.now().isoformat()
    }), 405


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred',
        'timestamp': datetime.now().isoformat()
    }), 500


if __name__ == '__main__':
    # Development server configuration
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting IntelliQuery Intent Agent API on port {port}")
    logger.info(f"Debug mode: {debug}")
    
    try:
        # Initialize orchestrator before starting server
        setup_app()
        
        # Start Flask development server
        app.run(
            host='0.0.0.0',
            port=port,
            debug=debug,
            threaded=True
        )
        
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        raise
