import axios from "axios";

const URL ='https://apifi.de-morgan.com/'

export const postCupos = async (clave) => {
    const url = `${URL}postCupos/`; 

    try {
        const response = await axios.post(url, { clave });
        console.log('POST Response:', response.data);
        
        return {
            mensaje: "Petición POST exitosa",
            data: response.data,
            error: false
        };
    } catch (error) {
        console.error(' Error en POST:', error);
        return {
            mensaje: "Error en POST",
            data: null,
            error: true
        };
    }
};
