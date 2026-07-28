import React, { useState, useRef } from 'react';
import Button from '../Button/Button';
import './Forms.css'

const Form = ({peticion}) => {

    const inputRef=useRef();
    const [cargando, setCargando] = useState(false);


    const obtenerValor= async ()=>{
        const clave = inputRef.current.value.trim();

        if (!clave) {
            alert('Ingresa clave, CHAVO, PORFAVOR');
            return;
        }

        setCargando(true);
        
        try {
            const respuesta = await peticion(clave);
            inputRef.current.value = ''; // Limpiar input después de buscar
        } catch (error) {
            console.error('Error en la petición:', error);
        } finally {
            setCargando(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter') {
            obtenerValor();
        }
    };
    
    return (
        <div className='container'>
           <input ref={inputRef} type="text" onKeyPress={handleKeyPress} disabled={cargando}/> 
            <Button method={obtenerValor} text={cargando ? "Buscando" : "Enviar"} disabled={cargando}/>
        </div>
    );
};


export default Form;