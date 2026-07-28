# JSON RETURNS AND REQUEST HANDLING
from numpy import tile
from flask import Flask, jsonify, request, send_file
# SANITIZATION
from werkzeug.security import generate_password_hash, check_password_hash
# CORS 
from flask_cors import CORS
# ENVIRONMENT VARIABLES AND CONEXION WITH DB TROUGH psycopg2 DRIVER
import os 
import io
# AUTH AND API TO FIREBASE
import firebase_admin
from firebase_admin import credentials, auth
# DB CONNECTION IMPORTS
import queries as postgres
import json
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from datetime import datetime

def register_routes(app, db):

    load_dotenv()
#   Initialize Firebase Admin SDK (only once)
#   Download this JSON from Firebase Console > Project Settings > Service Accounts
    # Method 1: From JSON string
    firebase_creds = json.loads(os.environ.get('FIREBASE_CREDENTIALS'))
    cred = credentials.Certificate(firebase_creds)

    firebase_admin.initialize_app(cred)
    # Configure CORS properly
    CORS(app, resources={
        r"/*": {
            "origins": [
                "http://localhost:3000", 
                "http://localhost:8000",
                "http://localhost:5000",
                "https://logica.de-morgan.com", 
                "https://api.de-morgan.com", 
                ],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization","X-API-Key"]
        }
    })
    # Configuration for upload files
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    # Create upload folder if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    '''
    Verificación por medio de la autenticación en firebase.
    Ejecutar cuando :
        1. Usuario inicia sesión (restricción del frontend es tener el token en las cookies)

    Acciones :
        1. Verificar el uid del usuario con firebase.
        2. 
    '''

    @app.route('/verify', methods=['POST'])
    def verify_token():
        # Get the Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No token provided'}), 401

        id_token = auth_header.split('Bearer ')[1]

        try:
            # Verify the token - this is where Firebase validates it's genuine
            decoded_token = auth.verify_id_token(id_token)

            # Extract the UID - THIS IS YOUR USER IDENTIFIER
            uid = decoded_token['uid']
            email = decoded_token.get('email')
            name = decoded_token.get('name')

            # Now you can use this UID with your PostgreSQL database
            # For example: save user progress, course enrollment, etc.
            print(uid)

            return jsonify({
                'uid': uid,
                'email': email,
                'name': name,
                'message': 'Token verified successfully',
                'code':200,
            }), 200 

        except auth.InvalidIdTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except auth.ExpiredIdTokenError:
            return jsonify({'error': 'Expired token'}), 401
        except Exception as e:
            return jsonify({'error': str(e)}), 401

    #######################################
    ##### RECEIVES FILE FROM STUDENTS #####
    #######################################

    @app.route("/file", methods=["POST"])
    def upload_file():
        try:
            # Check if file is in request
            if 'file' not in request.files:
                return jsonify({'error': 'No file part'}), 400
            
            file = request.files['file']
            
            # Check if file was selected
            if file.filename == '':
                return jsonify({'error': 'No selected file'}), 400
            
            # Check if file type is allowed
            if not allowed_file(file.filename):
                return jsonify({'error': 'File type not allowed'}), 400
            
            # Get the type_of_file from form data
            type_of_file =  request.form.get('type_of_file', 'unknown')
            calificacion =  request.form.get('calificacion', 'unknown')
            uid =           request.form.get('uid', 'unknown')
            unit =          request.form.get('unit', 'unknown')
            tile =          request.form.get('tile', 'unknown')
            # Secure the filename and save
            filename = secure_filename(file.filename)
            data = file.read()

            # CHANGED CALIFICACION
            postgres.receive_homework(uid,data,filename,type_of_file,tile, unit, calificacion=calificacion)            

            # Process the file based on type_of_file
            return jsonify({
                'success': True,
                'message': 'File uploaded successfully',
                'filename': filename,
                'type': type_of_file,
            }), 200
        
        except Exception as e:
            return jsonify({
                'error': str(e),
                'success': False,
                'result': 'failure',
            }), 500

    #######################################################
    #####   CREATE A HOMEWORK OR DAILY CHALLENGUE   #######
    #####       BASED ON THE CHOICE MADE AT /dev    ####### 
    #######################################################

    @app.route("/create", methods=["GET","POST"])
    def create():
        file_data = None
        try:
            #############################
            ###   ARCHIVO ES TAREA    ###
            #############################

            data = request.form.to_dict()  # Get form fields

            # Check if file is in request
            if 'file' in request.files:
                file = request.files['file']
                
                if file.filename == '':
                    return jsonify({'error': 'No selected file'}), 400
                
                if not allowed_file(file.filename):
                    return jsonify({'error': 'File type not allowed'}), 400
                
                file_data = file.read()
            
            if 'unit' in data:
                unit = int(data.get('unit', 0))
                tile = int(data.get('tile', 0))
                url = data.get('contenido')
                icon = data.get('icon', '')
                tipo_tarea = data.get('type_of_file',icon)
                descripcion = data.get('descripcion', '')
                print(tipo_tarea)

                url = url if url and len(url) > 10 else None

                postgres.create_homework(
                    unit=unit,
                    tile=tile,
                    descripcion=descripcion,
                    htype=tipo_tarea,
                    icon=icon,url=url,
                    archivo=file_data
                    )
                

            ###################################
            ###   ARCHIVO ES RETO DIARIO    ###
            ###################################
            
            elif 'fecha_entrega' in data : 
                url = data.get('url')
                descripcion = data.get('descripcion','')
                fecha_entrega = data.get('fecha_entrega')
                tipo_tarea = data.get('type_of_file','')
                print(tipo_tarea)

                url = url if url and len(url) > 10 else None

                postgres.create_dailyQuest(
                    descripcion=descripcion,
                    dia_activacion=fecha_entrega,
                    tipo_tarea=tipo_tarea,
                    url=url,
                    archivo=file_data
                )

            return jsonify({
                "message": f"Task created successfully!",
                "status": "ok"
                }), 200

        except Exception as e:
            print("Error", e)
            return jsonify({"error": str(e)}), 500

    ##################################################
    ####   OBTAIN DAILY CHALLENGE FOR DISPLAY    #####
    ##################################################

    @app.route("/daily", methods=["GET"])
    def recvDailyChallengeInfo():
        dateToday = datetime.now().strftime('%Y-%m-%d')
        try:
            result = postgres.get_challenge(dateToday)
            
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
        
    @app.route("/daily/download", methods=["GET"])
    def download_daily_challenge():
        dateToday = datetime.now().strftime('%Y-%m-%d')
        try:
            result = postgres.get_challenge(dateToday)
            
            if not result or result['tipo_tarea'] != 'file':
                return jsonify({"error": "No file available"}), 404
            
            filedata = result['archivo']
            if isinstance(filedata, memoryview):
                filedata = bytes(filedata)
            
            return send_file(
                io.BytesIO(filedata),
                download_name='Reto_diario.pdf',
                as_attachment=True,
                mimetype='application/pdf'
            )
        except Exception as e:
            print("Error:", e)
            return jsonify({"error": str(e)}), 400

    ##################################################
    ####   OBTAIN DAILY CHALLENGE FOR DISPLAY    #####
    ##################################################

    @app.route("/task", methods=["GET"])
    def recvTileMetadata():
        try:
            unit = request.args.get("unit")
            tile = request.args.get("selectedTile")
            result = postgres.get_link(unit, tile)

            if not result:
                return jsonify({"error": "Error on database tile lookup"}), 404
            
            # Always return JSON first
            if result.get('tipo_tarea') == 'file':
                return jsonify({
                    "type": "file",
                    "has_file": True,
                    "icon": result.get('icon'),
                    "filename": f"homework_unit_{unit}_tile_{tile}.pdf"
                }), 200
            else:
                return jsonify({
                    "type": "link",
                    "url": result.get('url')
                }), 200
                
        except Exception as e:
            print("Error:", e)
            return jsonify({"error": str(e)}), 400

    @app.route("/task/download", methods=["GET"])
    def download_tile_file():
        try:
            unit = request.args.get("unit")
            tile = request.args.get("selectedTile")
            result = postgres.get_link(unit, tile)

            if not result or result.get('tipo_tarea') != 'file':
                return jsonify({"error": "No file available"}), 404
            
            filedata = result.get('archivo')
            if isinstance(filedata, memoryview):
                filedata = bytes(filedata)
            
            return send_file(
                io.BytesIO(filedata),
                download_name=f'homework_unit_{unit}_tile_{tile}.pdf',
                as_attachment=True,
                mimetype='application/pdf'
            )
        except Exception as e:
            print("Error:", e)
            return jsonify({"error": str(e)}), 400

    ############################################################
    ####   RETURNS ALL UNITS AND THEIR COMPLETION STATE    #####
    ############################################################

    @app.route("/progress", methods=["GET"])
    def sendProgress():
        if request.method == 'GET':
            try:
                uid = request.args.get("uid");
                email = request.args.get("email");
                name = request.args.get("name");
                user_df_json = postgres.postgresql_to_dataframe(uid,email,name)
                print("Sending")
                return user_df_json,200
            except Exception as e:
                print("Error",e)
                return 400

    ####################################################
    ####   RETURNS HOMEWORK FOR A SPECIFIC USER    #####
    ####################################################

    @app.route("/homeworks/all",methods=["GET"])
    def get_homeworks_metadata(): 
        if request.method == 'GET':
            try :
                homeworks = postgres.get_homeworks_summary();
                print(jsonify(homeworks))
                return jsonify(homeworks),200
            except Exception as e:
                print("Error", e)
                return 400
        pass

    @app.route("/homeworks/<uid>",methods=["GET"])
    def get_students_metadata(uid): 
        if request.method == 'GET':
            uid = request.args.get('uid')
            try :
                if (uid) :
                    homework = postgres.get_all_homeworks_student(uid);
                    return jsonify(homework),200
                else :
                    return 400
                
            except Exception as e:
                print("Error", e)
                return 400
        pass

    @app.route("/homework/<uid>/<int:homework_id>", methods=["GET"])
    def download_homework_file(uid, homework_id):
        try:
            result = postgres.get_homework_student(uid,id_tarea_post=homework_id)
            if result:
                filename = result[1]
                filetype = result[2]

                return send_file(io.BytesIO(result[0]), download_name=filename,as_attachment=True)
                
            else:
                return jsonify({"error": "File not found"}), 404
        except Exception as e:
            print("Error:", e)
            return jsonify({"error": str(e)}), 400
        
    ##################################################
    ####   RETURNS ALL USERS REGISTERED IN DB    #####
    ##################################################

    @app.route("/dev/students",methods=["GET"])
    def get_students():
        if request.method == 'GET':
            try:
                users = postgres.get_users()
                return users, 200
            except Exception as e:
                print("Error", e)
                return 400
        pass


    @app.route("/dev/assignments",methods=["GET"])
    def get_assignments():
        if request.method == 'GET':
            try:
                assignments = postgres.get_assignments_metadata()
                return jsonify(assignments),200
            except Exception as e:
                print("Error", e)
                return 500