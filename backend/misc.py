from datetime import datetime
import subprocess
import os

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
