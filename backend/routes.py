from flask_cors import CORS
from datetime import datetime
from flask import Flask, jsonify, request, send_file
import subprocess
import os
import json
import monitor as sql
import monitor_loop as runner
from misc import *

def register_routes(app, db):
    CORS(app, resources={
        r"/*": {
            "origins": [
                "http://localhost:3000", 
                "http://localhost:8000",
                "http://localhost:5000",
                "https://apifi.de-morgan.com", 
                ],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization","X-API-Key"]
        }
    })

    # In your Python code
    @app.route("/postClave/<int:clave>", methods=["POST"])
    def postClave(clave):
        try:
            if not clave:
                return jsonify({"error": "Clave not received"}), 404
            
            result = curlToFI(clave)

            courseInfo = parseIntoJson(clave)
            if not courseInfo :
                return jsonify({"error": "No dict returned"}), 400
            
            if result.returncode == 0:
                runner.monitor.add_course(clave)
                courseInfoJson = json.dumps(courseInfo)
                sql.add_course(clave, courseInfoJson)
                return jsonify({
                    "success": True,
                    "message": "Data updated",
                    "clave": clave,
                }), 200
            elif result.returncode == 1:
                return jsonify({
                    "success": True,
                    "message": "No change",
                    "clave": clave
                }), 200
            else:
                return jsonify({
                    "success": False,
                    "error": result.stderr,
                    "returncode": result.returncode
                }), 500
                
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @app.route("/getCupos/<int:clave>", methods=["GET"])
    def getCupo(clave):
        try:
            if not clave:
                return jsonify({
                    "success": False,
                    "error": "No course code provided"
                }), 400

            # Get course from database
            course = sql.get_course(clave)
            
            if course is None:
                return jsonify({
                    "success": False,
                    "error": f"Course {clave} not found",
                    "clave": clave
                }), 404
            
            # Course exists, return the data
            return jsonify({
                "success": True,
                "clave": clave,
                "data": course['data'],  # The JSON data
                "last_updated": course['last_updated'],
                "returncode": 200
            }), 200
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 400

