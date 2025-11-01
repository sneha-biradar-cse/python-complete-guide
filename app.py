"""
Flask Application for Agricultural Q&A System
Main backend API that integrates all components
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from data_integrator import DataIntegrator
from query_processor import QueryProcessor
from response_generator import ResponseGenerator
import os


app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Initialize components
data_integrator = DataIntegrator()
query_processor = QueryProcessor()
response_generator = ResponseGenerator()

# Initialize data sources on startup
print("Initializing data sources...")
data_integrator.initialize_sources()
print("Data sources initialized successfully!")


@app.route('/')
def index():
    """Serve the main frontend page"""
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Agricultural Q&A System is running",
        "data_sources": list(data_integrator.sources.keys())
    })


@app.route('/api/query', methods=['POST'])
def process_query():
    """
    Main endpoint to process user queries
    
    Expected JSON payload:
    {
        "query": "What is the rice production in Punjab?"
    }
    
    Returns:
    {
        "answer": "...",
        "citations": [...],
        "metadata": {...}
    }
    """
    try:
        # Get query from request
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                "error": "Missing 'query' field in request"
            }), 400
        
        user_query = data['query']
        
        if not user_query.strip():
            return jsonify({
                "error": "Query cannot be empty"
            }), 400
        
        # Step 1: Process the query to understand intent
        query_intent = query_processor.process_query(user_query)
        
        # Step 2: Build query parameters for each data source
        query_params = query_processor.build_query_params(query_intent)
        
        # Step 3: Query all relevant data sources
        data_results = {}
        for source_name in query_intent.data_sources:
            if source_name in query_params:
                result = data_integrator.query_source(
                    source_name,
                    query_params[source_name]
                )
                data_results[source_name] = result
        
        # Step 4: Generate response with citations
        response = response_generator.generate_response(
            user_query,
            query_intent,
            data_results
        )
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({
            "error": f"An error occurred: {str(e)}"
        }), 500


@app.route('/api/sources', methods=['GET'])
def get_data_sources():
    """Get information about available data sources"""
    sources_info = []
    
    for source_name, source in data_integrator.sources.items():
        sources_info.append({
            "name": source.name,
            "id": source_name,
            "url": source.source_url,
            "last_updated": source.last_updated.isoformat() if source.last_updated else None
        })
    
    return jsonify({
        "sources": sources_info,
        "count": len(sources_info)
    })


@app.route('/api/examples', methods=['GET'])
def get_example_queries():
    """Get example queries that users can try"""
    examples = [
        {
            "query": "What is the rice production in Punjab?",
            "category": "Production"
        },
        {
            "query": "Show me wheat prices in 2024",
            "category": "Pricing"
        },
        {
            "query": "What is the weather like in Gujarat?",
            "category": "Weather"
        },
        {
            "query": "Compare rice and wheat production",
            "category": "Comparison"
        },
        {
            "query": "What is the rainfall in West Bengal during monsoon?",
            "category": "Weather"
        },
        {
            "query": "What is the MSP for cotton in Gujarat?",
            "category": "Pricing"
        },
        {
            "query": "Show me sugarcane cultivation area in Uttar Pradesh",
            "category": "Area"
        }
    ]
    
    return jsonify({
        "examples": examples,
        "count": len(examples)
    })


@app.route('/api/stats', methods=['GET'])
def get_statistics():
    """Get system statistics"""
    stats = {
        "total_sources": len(data_integrator.sources),
        "sources": {}
    }
    
    for source_name, source in data_integrator.sources.items():
        if hasattr(source, 'data'):
            stats["sources"][source_name] = {
                "name": source.name,
                "records": len(source.data)
            }
    
    return jsonify(stats)


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Run the Flask app
    # Note: In production, use a proper WSGI server like gunicorn
    print("\n" + "="*60)
    print("Agricultural Q&A System - Backend Server")
    print("="*60)
    print("\nServer starting on http://localhost:5000")
    print("\nAvailable endpoints:")
    print("  - GET  /                  : Frontend interface")
    print("  - POST /api/query         : Process user queries")
    print("  - GET  /api/health        : Health check")
    print("  - GET  /api/sources       : List data sources")
    print("  - GET  /api/examples      : Get example queries")
    print("  - GET  /api/stats         : System statistics")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
