import './Results.css';  // 👈 OJO: el nombre del archivo

const Results = ({ clave, data }) => {
  const grupos = Object.keys(data).map((numeroGrupo) => ({
    grupo: numeroGrupo,
    ...data[numeroGrupo]
  }));

  return (
    <div className="container">
      <h2> Resultados para materia {clave}</h2>
      <div>Se encontraron {grupos.length} grupos</div>

      <div className="card">
        {/* Encabezado */}
        <div className="table-header">
          <div>Grupo</div>
          <div>Maestro</div>
          <div style={{ textAlign: 'center' }}>Cupo</div>
          <div style={{ textAlign: 'center' }}>Vacantes</div>
          <div>Actualización</div>
        </div>

        {/* Datos */}
        {grupos.map((grupo, index) => (
          <div key={index}>
            <div>{grupo.grupo}</div>
            <div>{grupo.maestro || 'N/A'}</div>
            <div style={{ textAlign: 'center' }}>{grupo.cupo || 'N/A'}</div>
            <div style={{ textAlign: 'center' }}>
              <span className={`vacantes-badge ${parseInt(grupo.vacantes) > 0 ? 'disponible' : 'lleno'}`}>
                {grupo.vacantes || '0'}
              </span>
            </div>
            <div>{grupo.luptime || 'N/A'}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Results;