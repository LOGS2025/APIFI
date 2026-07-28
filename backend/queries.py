# queries.py - Business logic for database operations
from pandas.io.formats.style import non_reducing_slice
from psycopg2 import Binary, sql, DatabaseError
import psycopg2
from db import get_db_connection
from datetime import date, datetime
from psycopg2.extras import DictCursor, RealDictCursor
from flask import jsonify
import pandas as pd
from typing import Any, Optional, Callable, List, Tuple
import logging
            
# Source - https://stackoverflow.com/q/53250620
# Posted by PuffedRiceCrackers
# Retrieved 2026-04-07, License - CC BY-SA 4.0


# class Query:
#     def __init__(self, sql_prompt: str, params: Optional[Tuple] = None):
#         self.sql_prompt = sql_prompt
#         self.params = params or ()
#         self.result = None
#         self.error = None
#         self.success = False
        
#         self._execute()
    
#     def _execute(self):
#         try:
#             with get_db_connection() as conn:
#                 with conn.cursor() as cur:
#                     # Execute query
#                     cur.execute(self.sql_prompt, self.params)
                    
#                     # Try to fetch results if SELECT
#                     if self.sql_prompt.strip().upper().startswith('SELECT'):
#                         self.result = cur.fetchall()
#                     else:
#                         # For INSERT/UPDATE/DELETE, get affected rows
#                         self.result = {'affected_rows': cur.rowcount}
                    
#                     conn.commit()
#                     self.success = True
                    
#                     # Log notices if any
#                     if conn.notices:
#                         logging.info(f"Database notices: {conn.notices}")
                    
#         except Exception as e:
#             self.error = str(e)
#             self.success = False
#             logging.error(f"Query error: {e}")
    
#     def present_success(self) -> Any:
#         return {'success': True, 'data': self.result}
    
#     def present_error(self) -> dict:
#         return {'success': False, 'error': self.error}
    
#     def get_result(self) -> Any:
#         return self.result
    
#     def was_successful(self) -> bool:
#         return self.success

# # Usage examples
# def create_user(uid: str):
#     query = Query(
#         "INSERT INTO usuarios (uid) VALUES (%s) RETURNING id_usuario",
#         (uid,)
#     )
#     if query.was_successful():
#         return query.get_result()
#     else:
#         print(f"Error: {query.error}")
#         return None

# def get_user(uid: str):
#     query = Query(
#         "SELECT * FROM usuarios WHERE uid = %s",
#         (uid,)
#     )
#     return query.get_result() if query.was_successful() else None

# # Simple usage
# result = Query("INSERT INTO usuarios (uid) VALUES (%s)", ('111',))
# if result.was_successful():
#     print("User created!")
# else:
#     print(f"Error: {result.error}")

# # For SELECT queries
# users = Query("SELECT * FROM usuarios")
# if users.was_successful():
#     for user in users.get_result():
#         print(user)



def create_user(uid):
    with get_db_connection() as conn:
        cur = conn.cursor(cursor_factory=DictCursor)
        sql = f"INSERT INTO usuarios (uid) VALUES ('{uid}')"
        cur.execute(sql) 
        conn.commit()
        # notices = conn.notices.copy()
    # return jsonify({"notices":notices})
    pass

def create_loginQA(question,answer):
    with get_db_connection() as conn:
        cur = conn.cursor(cursor_factory=DictCursor)
        sql = f"INSERT INTO catalogo_preguntas (pregunta,respuesta_correcta) VALUES ('{question}','{answer}')"
        cur.execute(sql) 
        conn.commit()
    pass

#################################################
#####   MAKE DAILY CHALLENGE OR HOMEWORK    #####
#################################################

def create_homework(  unit,  tile,  descripcion,  htype,  icon,  url=None,  archivo=None):
    if not url and not archivo:
        return
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            sql = '''
            INSERT INTO tareas (
            unit,tile,url,tipo_tarea,icon,archivo,descripcion) 
            VALUES (%s,%s,%s,%s,%s,%s,%s)'''

            try:
                cur.execute(sql,(
                    unit,
                    tile,
                    url,
                    htype,
                    icon,
                    Binary(archivo) if htype=='file' else None,
                    descripcion
                )) 
                conn.commit()
            except Exception as e:
                print("Error on postgres: ",e)
    pass

def create_dailyQuest(descripcion,dia_activacion,tipo_tarea,url=None,archivo=None):
    if not url and not archivo:
        return
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            sql = '''
            INSERT INTO retos_diarios ( 
            url, archivo, tipo_tarea, descripcion, dia_activacion) 
            VALUES ( %s, %s ,%s ,%s ,%s)'''
            try:
                cur.execute(sql,(
                    url,
                    Binary(archivo) if tipo_tarea=='file' else None,
                    tipo_tarea,
                    descripcion,
                    dia_activacion
                )) 
                conn.commit()
            except Exception as e:
                print("Error on postgres: ",e)
    pass

#######################################################################
####    START A USER WITH REGISTRATION AND OBTAIN THEIR PROGRESS    ###
#######################################################################

def postgresql_to_dataframe(uid,email,name):
    """
    Tranform a SELECT query into a pandas dataframe
    """
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=DictCursor)
        sql = f"SELECT * FROM get_user_homework_or_create('{uid}','{email}','{name}')"
        columns = ["id_tarea","unit","tile","icon","tipo_tarea","descripcion","es_completado","is_new_user"]
        
        try:
            cursor.execute(sql)
        except (Exception, DatabaseError) as error:
            print("Error: %s" % error)
            cursor.close()
            return 1
        
        # Naturally we get a list of tupples
        tupples = cursor.fetchall()
        cursor.close()
        
        # We just need to turn it into a pandas dataframe
        df = pd.DataFrame(tupples, columns=columns)
        # Group by unit and convert each group to records
        result = {
        int(unit): group.drop('unit', axis=1).to_dict(orient='records')
        for unit, group in df.groupby('unit')
        }
        return result

##################################
##### SEND FILE TO POSTGRES ######
##################################

def receive_homework(uid,archivo,filename,filetype,tile, unit, calificacion=None):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            sql = '''
            INSERT INTO tareas_recibidas 
            (uid, id_tarea, unit, archivo, filename, filetype)
            VALUES (%s,%s,%s,%s,%s,%s,%s)'''
            try:
                cur.execute(sql,(
                    uid,
                    tile,
                    unit,
                    Binary(archivo),
                    filename,
                    filetype
                )) 
                conn.commit()
            except Exception as e:
                print("Error on postgres: ",e)
    pass

#############################################
##### GET FILE FROM STUDENT TO TEACHER ######
#############################################

def get_homework_student(uid, id_tarea_post):
    with get_db_connection() as conn:
        cur = conn.cursor(cursor_factory=DictCursor)
        sql = f"SELECT archivo, filename, filetype FROM tareas_recibidas WHERE uid = '{uid}' AND id_tarea_post = {id_tarea_post};"
        try :
            cur.execute(sql) 
            conn.commit()

            result = cur.fetchone()
            cur.close()
            return result
            
        except Exception as e:
            print("Error:", e)
            return None

####################################################
##### GET ALL METADATA FROM STUDENT TO TEACHER #####
####################################################

def get_all_homeworks_student(uid):
    with get_db_connection() as conn:
        cur = conn.cursor(cursor_factory=DictCursor)
        sql = f"SELECT id_tarea_post, uid, filename, filetype, upload FROM tareas_recibidas WHERE uid = '{uid}';"
        try :
            cur.execute(sql) 
            conn.commit()
        except (Exception, DatabaseError) as error:
            print("Error: %s" % error)
            cur.close()
        tareas = cur.fetchall()
        cur.close()

        result_list = []
        for tarea in tareas:
            item = dict(tarea)
            if item.get('upload'):
                item['upload'] = item['upload'].isoformat()
            result_list.append(item)
        
        # Return in same format as get_homeworks_summary for consistency
        return {uid: result_list}

###########################################################
##### GET HOMEWORK METADATA FROM STUDENTS TO TEACHER #####
###########################################################

def get_homeworks_summary():
    with get_db_connection() as conn:
        cur = conn.cursor(cursor_factory=DictCursor)
        sql = f"SELECT id_tarea_post, uid, filename, filetype, upload FROM tareas_recibidas;"        
        try :
            cur.execute(sql) 
            conn.commit()
        except (Exception, DatabaseError) as error:
            print("Error: %s" % error)
            cur.close()
        tareas = cur.fetchall()
        cur.close()

        # Convert to list of dicts first
        result_list = []
        for tarea in tareas:
            item = dict(tarea)
            if item.get('upload'):
                item['upload'] = item['upload'].isoformat()
            result_list.append(item)
        
        # Group by UID
        result = {}
        for item in result_list:
            uid = item['uid']
            if uid not in result:
                result[uid] = []
            # Remove uid from the nested dict to avoid duplication
            item_without_uid = {k: v for k, v in item.items() if k != 'uid'}
            result[uid].append(item_without_uid)
        
        return result


def get_link(unit, tile):
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        sql = """
            SELECT tareas.icon, tareas.tipo_tarea, tareas.url, tareas.archivo 
            FROM tareas 
            WHERE tareas.tile = %s AND tareas.unit = %s
        """
        try:
            cursor.execute(sql, (tile, unit)) 
            result = cursor.fetchone()
            conn.commit()
            cursor.close()
            return result
        except (Exception, DatabaseError) as error:
            print("Error: %s" % error)
            cursor.close()
            return None

#############################################
##### GET FILE FROM STUDENT TO TEACHER ######
#############################################

def get_challenge(date):
    with get_db_connection() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        sql = f"SELECT archivo, url, tipo_tarea FROM retos_diarios WHERE dia_activacion = '{date}'"
        try :
            cur.execute(sql) 
            result = cur.fetchone()
            conn.commit()

            print(result)
            cur.close()
            return result
            
        except Exception as e:
            print("Error:", e)
            return None

########################################################
##### GET HOMEWORKS AND DAILY CHALLENGES METADATA ######
########################################################

def get_assignments_metadata():
    with get_db_connection() as conn:
        assignment_list = []

        cursor = conn.cursor(cursor_factory=DictCursor)
        sql_homeworks = "SELECT unit, tile, tipo_tarea, descripcion FROM public.tareas;"
        sql_daily = "SELECT tipo_tarea, descripcion, dia_activacion FROM public.retos_diarios;"
        
        try:
            cursor.execute(sql_homeworks)
            conn.commit()
            homeworks_tupples = cursor.fetchall()

            for homework in homeworks_tupples:
                homework_dict = {
                    'unit' : homework['unit'],
                    'tile' : homework['tile'],
                    'tipo_tarea' : homework['tipo_tarea'],
                    'descripcion' : homework['descripcion'],
                }
                assignment_list.append(homework_dict)
            
            cursor.execute(sql_daily)
            conn.commit()
            daily_tupples = cursor.fetchall()

            for daily in daily_tupples:
                daily_dict = {
                    'dia_activacion' : daily['dia_activacion'],
                    'tipo_tarea' : daily['tipo_tarea'],
                    'descripcion' : daily['descripcion'],
                }
                assignment_list.append(daily_dict)

            cursor.close()
            return assignment_list            

        except (Exception, DatabaseError) as error:
            print("Error: %s" % error)
            cursor.close()
            return {
                'message' : error,
                'status' : 500
            }
        
    
def get_users():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM usuarios")

            users = cur.fetchall()

            cur.close()
            userList = []
            for user in users :
                user_dict = {}
                if user['creation_date'] :
                    user['creation_date'] = user['creation_date'].isoformat()
                user_dict = {
                    'uid': user['uid'],
                    'email': user['email'],
                    'name': user['name'],
                    'creation_date': user['creation_date']
                }
                userList.append(user_dict)

            result = jsonify(userList)
        return result