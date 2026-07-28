#!/bin/bash

function url_HEAD() {
	curl -sI "https://www.ssa.ingenieria.unam.mx/cj/tmp/programacion_horarios/$1.html" | grep "last-modified" | awk \
	'gsub("last-modified: ","")'
}

function url_GET() {
	curl "https://www.ssa.ingenieria.unam.mx/cj/tmp/programacion_horarios/$1.html" | grep \
	-iF "<strong>Gpo.:</strong>" | awk \
	'{gsub("<a><strong>","") gsub("</strong>","")  gsub("<strong>","") gsub("</a>","");print}'
}

function main() {
	local NEWDATE=$(url_HEAD $1)
	
	local OLDDATE

	if [ -f "./LASTMODIFIED" ]; then
        	OLDDATE=$(cat ./LASTMODIFIED)
    	else
        	OLDDATE=""
    	fi
	
	if [ "$NEWDATE" == "$OLDDATE" ];
	then
		echo "Same dates"
		return 1
	fi


	url_GET $1 > test.txt
	echo $NEWDATE > LASTMODIFIED
	return 0
}

main $1 

# https://www.ssa.ingenieria.unam.mx/cj/tmp/programacion_horarios/508.html?_=1785198272875
# <a><strong>Gpo.:</strong> 1, <strong>Cupo:</strong> 30</a>



