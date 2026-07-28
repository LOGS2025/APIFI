from numpy import tile
from flask_cors import CORS
from datetime import datetime

def register_routes(app, db):
    CORS(app, resources={
        r"/*": {
            "origins": [
                "http://localhost:3000", 
                "http://localhost:8000",
                "http://localhost:5000",
                "https://apifi.de-morgan.com", 
                ],
            "methods": ["GET", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization","X-API-Key"]
        }
    })
    @app.route("/cupo?<clave>", methods=["GET"])
    def getCupo():
        dateToday = datetime.now().strftime('%Y-%m-%d')
        try:
            if not result:
                return jsonify({"error": "No challenge found for today"}), 404
            
            # Always return JSON first
            if result['tipo_tarea'] == 'file':
                # Return metadata with a flag for file download
                return jsonify({
                    "type": "file",
                    "has_file": True,
                    "filename": "daily_challenge.pdf"
                }), 200
            else:
                # Return the URL
                return jsonify({
                    "type": "link",
                    "url": result['url']
                }), 200
                
        except Exception as e:
            print("Error:", e)
            return jsonify({"error": str(e)}), 400
