from numpy import tile
from flask_cors import CORS
from datetime import datetime
from flask import Flask, jsonify, request, send_file

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
    @app.route("/<int:clave>", methods=["GET"])
    def getCupo(clave):
        try:
            if clave:
                clave_tmp = int(clave)
                print(clave)
                
            else:
                return jsonify({"error": "File not found"}), 404
        except Exception as e:
            print("Error:", e)
            return jsonify({"error": str(e)}), 400