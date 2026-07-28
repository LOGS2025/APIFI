import axios from 'axios';

const URL ='https://apifi.de-morgan.com/'

export const getCupos = async (clave)=>{
    const url=`${URL}getCupos/${clave}`;
    console.log(' URL de la petición:', url);

    try{
    //almacena la respuesta
        const response = await axios.get(url)

        console.log('Respuesta de la API:', response);
        console.log('Datos recibidos:', response.data.data);
        
        
        return {
            mensaje: "Petición exitosa",
            data: response.data.data
        };
    } catch (error) {
        console.error('Error en getCupos:', error);
        
        return {
            mensaje: "Hubo error",
            data: error.response?.data || error.message
        };
    }};