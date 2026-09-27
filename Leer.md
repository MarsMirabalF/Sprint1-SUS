# Sistema Seguro Social Universitario

## Estructura del proyecto

```
proyecto/
├── principal.py                        -> archivo que se ejecuta para correr todo
├── clienteSeguroUniversitario/         -> interfaz de usuario (Tkinter) — pendiente
├── servidorSeguroUniversitario/
│   ├── configuracion/
│   │   └── configuracionFirebase.py    -> conexión a Firebase Admin SDK
│   ├── utilidades/
│   │   └── validadores.py              -> validación de formato (cédula, correo, teléfono)
│   ├── servicios/
│   │   ├── servicioAfiliacion.py       -> lógica de la HU 6 (afiliación al seguro)
│   │   └── servicioCobertura.py        -> lógica de la HU 1 (consulta de cobertura)
│   ├── baseDatos/
│   │   ├── esquemaBaseDatos.md         -> diseño de nodos "estudiantes" / "afiliados" / "serviciosMedicos"
│   │   ├── database.rules.json         -> reglas / índices de la Realtime Database
│   │   └── sembrarDatosPrueba.py       -> (opcional) datos de ejemplo para probar
│   ├── credenciales/                   -> aquí va el JSON de la cuenta de servicio (NO se sube a Git)
│   └── requirements.txt
├── leer.md
└── .gitignore
```

Ejecutar siempre desde la carpeta **raíz** del proyecto (donde está `principal.py`),
para que los imports (`servidorSeguroUniversitario.xxx`) funcionen.

| codigo                | exito | Cuándo ocurre                                                     |
|------------------------|-------|----------------------------------------------------------------------|
| CAMPOS_INCOMPLETOS      | False | Faltó algún campo obligatorio (ver `camposFaltantes`)                |
| FORMATO_INVALIDO        | False | Cédula, correo o teléfono con formato inválido (`camposInvalidos`)   |
| MATRICULA_INEXISTENTE   | False | La matrícula no existe en el nodo `estudiantes`                      |
| SEGURO_YA_ACTIVO        | False | El estudiante ya tiene seguro activo (por matrícula o por cédula)    |
| AFILIACION_EXITOSA      | True  | Se creó el registro en `afiliados` (`idAfiliado` devuelto)           |
| ERROR_INESPERADO        | False | Cualquier excepción no controlada (ej. sin conexión)                 |
 
 
| codigo                     | exito | Cuándo ocurre                                                |
|-----------------------------|-------|------------------------------------------------------------------|
| LISTA_OBTENIDA               | True  | Se devolvió la lista de servicios médicos                        |
| CATALOGO_VACIO               | True  | El nodo `serviciosMedicos` existe pero no tiene registros aún    |
| SERVICIO_NO_ESPECIFICADO     | False | No se indicó `idServicio` al consultar un servicio puntual       |
| SERVICIO_INEXISTENTE         | False | El `idServicio` consultado no existe en el catálogo              |
| COBERTURA_OBTENIDA           | True  | Se devolvió el estado de cobertura del servicio seleccionado     |
| ERROR_INESPERADO             | False | Cualquier excepción no controlada (ej. sin conexión)             |
 

El PDF se guarda en la carpeta `comprobantesGenerados/` en la raíz del
proyecto (se crea automáticamente si no existe) **y además** queda guardado
en la DB. La futura UI puede tomar `resultado["rutaArchivo"]` para abrirlo
apenas se genera, y usar `listarComprobantesDelEstudiante` /
`descargarComprobanteGuardado` para la pantalla del perfil del estudiante.
 
| codigo                        | exito | Cuándo ocurre                                                          |
|---------------------------------|-------|------------------------------------------------------------------------|
| MATRICULA_INEXISTENTE            | False | La matrícula no existe en el nodo `estudiantes`                        |
| SIN_CONSULTA_PREVIA               | True  | El estudiante existe pero no tiene consultas con fecha ≤ hoy (botón deshabilitado, no es un error) |
| CONSULTA_PREVIA_ENCONTRADA        | True  | Sí tiene al menos una consulta previa (botón habilitado)                |
| CONSULTA_NO_VALIDA                | False | El `idConsulta` indicado no existe, no es previa a hoy, o es de otro estudiante |
| COMPROBANTE_GENERADO              | True  | Se generó el PDF y se guardó en el perfil (`rutaArchivo` devuelto)      |
| COMPROBANTE_NO_ENCONTRADO         | False | No existe un comprobante guardado con ese `idConsulta`                  |
| ERROR_INESPERADO                  | False | Cualquier excepción no controlada (ej. sin conexión)                    |
 
> Nota: `SIN_CONSULTA_PREVIA` devuelve `"exito": True` porque **no es un
> error** — es una respuesta válida que simplemente dice "botón
> deshabilitado". La UI debe fijarse en `resultado["habilitado"]`, no solo
> en `resultado["exito"]`, para decidir si mostrar el botón activo o no.
 