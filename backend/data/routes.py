import pandas as pd
from flask_cors import CORS
from datetime import datetime
from flask import Flask, jsonify, request, send_file
import subprocess
import os
import re
import json
import data.monitor as sql

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

def parseIntoJson(clave):
    course = {}
    try:
        with open(f'./{clave}.data', 'r') as f:
            lines = f.readlines()
            for line in lines:
                information = line.strip().split(',')
                maestro = information[0].replace("Profesor:","").strip()
                grupo = information[1].replace("Gpo.:","").strip()
                cupo = information[2].replace("Cupo:","").strip()
                course[grupo] = {
                    'maestro' : maestro,
                    'cupo' : cupo,
                    'vacantes' : '0',
                    'luptime' : datetime.now().strftime("%H-%M-%S") 
                }
        return course
    except Exception as e:
        return None

def curlToFI(clave):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, 'fetch_group.sh')
    os.chmod(script_path, 0o755)

    # Run script with explicit working directory
    result = subprocess.run(
        [script_path, str(clave)],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=script_dir  # THIS IS IMPORTANT - run in script's directory
    )
    
    return result
