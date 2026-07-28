import React, { useEffect, useRef } from 'react';
import Button from '../Button/Button';
import './Forms.css'

const Form = ({peticion, guardar}) => {

    const inputRef=useRef();

    const obtenerValor= async ()=>{
        peticion(inputRef.current.value)

        if (inputRef.current.value) {
            const respuesta = await peticion(inputRef.current.value);
            guardar(respuesta);
        }
        
    };

    useEffect(()=>{
        console.log(inputRef);
    },[inputRef])
    return (
        <div>
           <input ref={inputRef} type="text" /> 
            <Button method={obtenerValor} text={"Enviar"}/>
        </div>
    );
};


export default Form;