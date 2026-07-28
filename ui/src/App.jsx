import { useEffect, useState } from 'react';
import Button from './Components/Button/Button';
import Form from './Components/Form/Form';
import { getCupos } from './app/api/getApi';
import { postCupos } from './app/api/postApi';
import Cargando from './Components/Cargando/Cargando';
import Error from './Components/Error/Error';
import Results from './Components/Results/Results';
import './index.css'


function App() {

  const [resultado, setResultado] = useState([]);
  const [error, setError] = useState('');
  const [claveBuscada, setClaveBuscada] = useState('');
  const [cargando, setCargando] = useState(false); 


  const buscador = async (clave) => {
    setError('');
    setClaveBuscada(clave);
    setCargando(true);

    try {
      console.log('Enviando POST...');
      const postResponse = await postCupos(clave);
      
      if (postResponse.error) {
        setError(`Error en POST: ${postResponse.mensaje}`);
        setCargando(false);
        return;
      }
      
      console.log('POST exitoso');

      console.log(' Haciendo GET...');
      const getResponse = await getCupos(clave);
      
      if (getResponse.error) {
        setError(`Error en GET: ${getResponse.mensaje}`);
      } else {
        setResultado(prev => [
          ...prev,
          {
            clave: clave,
            data: getResponse.data,
            timestamp: new Date().toLocaleString()
          }
        ]);
        console.log('Datos agregados:', getResponse.data);
      }
      
    } catch (error) {
      console.error('Error inesperado:', error);
      setError('Error inesperado al buscar');
    } finally {
      setCargando(false);
    }
  };

  let contenido = null;
 if (cargando) {
    contenido = <Cargando />;
  } else if (error) {
    contenido = <Error mensaje={error} />;
  } else if (resultado) {
    contenido = <Results clave={claveBuscada} data={resultado} />;
  }


  return (
    <>
    <header></header>
      <div className='row'>
        
        <h1>Ingresa clave de materia a monitorear</h1>
       </div>
       <Form peticion={buscador}></Form>
        {resultado.map((item, index) => (
          <div key={index} style={{ marginTop: '30px' }}>
                <strong> Búsqueda num.{index + 1}:</strong> Clave {item.clave}
              <Results clave={item.clave} data={item.data} />
            </div>
          ))}
        </>
      )
}

export default App

