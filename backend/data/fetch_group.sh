#!/bin/bash

function url_HEAD() {
	curl -sI "https://www.ssa.ingenieria.unam.mx/cj/tmp/programacion_horarios/$1.html" | grep "last-modified" | awk \
	'gsub("last-modified: ","")'
}

function url_GET() {
	curl -s "https://www.ssa.ingenieria.unam.mx/cj/tmp/programacion_horarios/$1.html" | \
    	sed -n '/Gpo.:/,/Profesor:/p' | \
    	grep -v '^[[:space:]]*$' | \
    	sed 's/<[^>]*>//g' | awk \
	'
	 /Profesor:/ {
	  gsub(/Tipo:.*$/, "")
	  print
	 }
	 /Gpo.:/ {
	  print
	 }
	' | awk \
	'
	 /Gpo.:/ {
	  grupo = $0
	  getline
	  profesor = $0
	  print  profesor "," grupo
	 }
	'
}

function main() {
	local NEWDATE=$(url_HEAD $1)
	local OLDDATE

	if [ -f "./LASTMODIFIED$1" ]; then
        	OLDDATE=$(cat ./LASTMODIFIED$1)
    	else
        	OLDDATE=""
    	fi
	
	if [ "$NEWDATE" == "$OLDDATE" ];
	then
		return 1
	fi

	echo "$NEWDATE">"LASTMODIFIED$1"
	url_GET $1 > "$1.data"
	return 0
}

main $1 

# https://www.ssa.ingenieria.unam.mx/cj/tmp/programacion_horarios/508.html?_=1785198272875
# <a><strong>Gpo.:</strong> 1, <strong>Cupo:</strong> 30</a>



