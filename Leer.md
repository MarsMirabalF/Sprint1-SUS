# Sistema Seguro Social Universitario

Backend en Python con Firebase Realtime Database para gestionar la afiliación,
cobertura, comprobantes médicos y renovación del seguro universitario.

## Estructura del proyecto

```
proyecto/
├── principal.py                        -> archivo que se ejecuta para correr todo
├── clienteSeguroUniversitario/         -> interfaz de usuario (Tkinter)
├── servidorSeguroUniversitario/
│   ├── configuracion/
│   │   └── configuracionFirebase.py    -> conexión a Firebase Admin SDK
│   ├── utilidades/
│   │   └── validadores.py              -> validación de formato (cédula, correo, teléfono)
│   ├── servicios/
│   │   ├── servicioLogin.py             -> autenticación por matrícula y Cédula de Identidad
│   │   ├── servicioAfiliacion.py       -> lógica de la HU 6 (afiliación al seguro)
│   │   ├── servicioCobertura.py        -> lógica de la HU 1 (consulta de cobertura)
│   │   ├── servicioComprobante.py      -> lógica de la HU 17 (comprobantes médicos)
│   │   └── servicioRenovacion.py       -> lógica de renovación del seguro y estado de vigencia
│   ├── baseDatos/
│   │   ├── esquemaBaseDatos.md         -> diseño de todos los nodos de la DB
│   │   ├── database.rules.json         -> reglas / índices de la Realtime Database
│   │   └── sembrarDatosPrueba.py       -> (opcional) datos de ejemplo para probar
│   ├── recursos/
│   │   └── firmaDigital.jpg            -> imagen de firma (simulación) embebida en el PDF
│   ├── credenciales/                   -> aquí va el JSON de la cuenta de servicio (NO se sube a Git)
│   └── requirements.txt
├── comprobantesGenerados/              -> PDFs generados por la HU 17 (no se suben a Git)
├── leer.md
└── .gitignore
```

La aplicación inicia con una pantalla de login. El estudiante debe ingresar la
matrícula y la Cédula de Identidad registrada en `estudiantes/<matrícula>`.
Sólo si ambos datos coinciden se habilita el formulario de afiliación y el
resto de las opciones de la aplicación.

Ejecutar siempre desde la carpeta **raíz** del proyecto (donde está `principal.py`),
para que los imports (`servidorSeguroUniversitario.xxx`) funcionen.

## Base de datos (Firebase Realtime Database)

Nodos principales. El diseño completo está en `baseDatos/esquemaBaseDatos.md`.

| Nodo                 | Clave                          | Contenido                                                                                     |
|----------------------|--------------------------------|-----------------------------------------------------------------------------------------------|
| `estudiantes`        | matrícula                      | `cedulaIdentidad`, `nombreCompleto`, `carrera`, `tieneSeguroActivo`                           |
| `afiliados`          | id generado (`push`)           | Datos personales de contacto + `matricula`, `fechaAfiliacion`, `estado` (`activo` / `inactivo`) |
| `periodosAcademicos` | idPeriodo (ej. `2026-2`)       | `nombre`, `fechaInicio`, `fechaFin` (formato `YYYY-MM-DD`)                                    |
| `matriculaciones`    | `<matricula>_<idPeriodo>`      | `matricula`, `idPeriodo`, `estado` (`matriculado` / `retirado`), `fechaMatriculacion`         |
| `seguros`            | matrícula                      | `idPeriodo`, `fechaInicioVigencia`, `fechaFinVigencia`, `fechaUltimaRenovacion`               |
| `renovaciones`       | `<matricula>_<idPeriodo>`      | Historial: `nombreCompleto`, `fechaVigenciaAnterior`, `fechaVigenciaNueva`, `fechaRenovacion` |
| `serviciosMedicos`   | idServicio                     | `nombreServicio`, `categoria`, `descripcion`, `cubierto`                                      |
| `consultasMedicas`   | id generado (`push`)           | `matricula`, `idServicioMedico`, `fechaConsulta`, `horaConsulta`, `medicoTratante`, ...       |

Además, los comprobantes médicos generados quedan guardados en el perfil del
estudiante (ver `esquemaBaseDatos.md`).

Notas de diseño:

- **Índice necesario:** `servicioRenovacion` busca afiliaciones con
  `order_by_child("matricula")` sobre `afiliados`, por lo que `database.rules.json`
  debe incluir `".indexOn": ["matricula"]` en ese nodo (si no, Firebase lo hace
  en el cliente y lanza una advertencia).
- **Periodo vigente:** se determina comparando la fecha de hoy con
  `fechaInicio` y `fechaFin` de `periodosAcademicos`.
- **Fechas como texto:** las fechas se guardan como `YYYY-MM-DD` (y
  `YYYY-MM-DD HH:MM:SS` para fecha-hora), lo que permite compararlas como cadenas.
- **Escritura atómica:** al renovar, se actualizan `seguros`, `renovaciones` y
  `estudiantes/<matricula>/tieneSeguroActivo` en una sola operación: o se guarda todo o nada.

## Datos de prueba

`baseDatos/sembrarDatosPrueba.py` inserta datos de ejemplo en todos los nodos
anteriores. Ejecutar desde la raíz:

```
python -m servidorSeguroUniversitario.baseDatos.sembrarDatosPrueba
```

> `afiliados` y `consultasMedicas` usan `push`, así que correr el script varias
> veces duplica esos registros. Los demás nodos usan claves fijas y se sobrescriben.

Estudiantes de prueba y el resultado esperado al renovar (con fecha de hoy dentro del periodo `2026-2`):

| Matrícula | Estudiante            | Situación                                                | Resultado de `renovarSeguro`   |
|-----------|-----------------------|----------------------------------------------------------|--------------------------------|
| 20231001  | Maria Fernanda Rojas  | Matriculada, sin afiliación                              | `SIN_AFILIACION_ACTIVA`        |
| 20231002  | Juan Pablo Quispe     | Afiliado activo, matriculado, seguro vencido             | `RENOVACION_EXITOSA`           |
| 20231003  | Ana Lucia Mamani      | Matriculada, afiliación inactiva                         | `SIN_AFILIACION_ACTIVA`        |
| 20231004  | Carlos Andres Villca  | Afiliado activo, ya renovado hasta el 2026-12-15         | `YA_RENOVADO_EN_PERIODO`       |
| 20231005  | Lucia Valeria Choque  | Afiliada activa, retirada del periodo `2026-2`           | `NO_MATRICULADO_EN_PERIODO`    |

Para simular otra fecha se puede pasar `fechaReferencia="YYYY-MM-DD"` a
`renovarSeguro` y `consultarEstadoSeguro`.

## Códigos de respuesta por servicio

Todos los métodos públicos devuelven un diccionario con `exito` (bool),
`codigo` (str) y `mensaje` (str), más los datos propios de cada operación.

### Afiliación (`servicioAfiliacion`)

| codigo                  | exito | Cuándo ocurre                                                        |
|-------------------------|-------|----------------------------------------------------------------------|
| CAMPOS_INCOMPLETOS      | False | Faltó algún campo obligatorio (ver `camposFaltantes`)                |
| FORMATO_INVALIDO        | False | Cédula, correo o teléfono con formato inválido (`camposInvalidos`)   |
| MATRICULA_INEXISTENTE   | False | La matrícula no existe en el nodo `estudiantes`                      |
| SEGURO_YA_ACTIVO        | False | El estudiante ya tiene seguro activo (por matrícula o por cédula)    |
| AFILIACION_EXITOSA      | True  | Se creó el registro en `afiliados` (`idAfiliado` devuelto)           |
| ERROR_INESPERADO        | False | Cualquier excepción no controlada (ej. sin conexión)                 |

### Cobertura (`servicioCobertura`)

| codigo                   | exito | Cuándo ocurre                                                    |
|--------------------------|-------|------------------------------------------------------------------|
| LISTA_OBTENIDA           | True  | Se devolvió la lista de servicios médicos                        |
| CATALOGO_VACIO           | True  | El nodo `serviciosMedicos` existe pero no tiene registros aún    |
| SERVICIO_NO_ESPECIFICADO | False | No se indicó `idServicio` al consultar un servicio puntual       |
| SERVICIO_INEXISTENTE     | False | El `idServicio` consultado no existe en el catálogo              |
| COBERTURA_OBTENIDA       | True  | Se devolvió el estado de cobertura del servicio seleccionado     |
| ERROR_INESPERADO         | False | Cualquier excepción no controlada (ej. sin conexión)             |

### Comprobantes médicos (`servicioComprobante`)

El PDF se guarda en la carpeta `comprobantesGenerados/` en la raíz del
proyecto (se crea automáticamente si no existe) **y además** queda guardado
en la DB. La futura UI puede tomar `resultado["rutaArchivo"]` para abrirlo
apenas se genera, y usar `listarComprobantesDelEstudiante` /
`descargarComprobanteGuardado` para la pantalla del perfil del estudiante.

| codigo                     | exito | Cuándo ocurre                                                                   |
|----------------------------|-------|---------------------------------------------------------------------------------|
| MATRICULA_INEXISTENTE      | False | La matrícula no existe en el nodo `estudiantes`                                 |
| SIN_CONSULTA_PREVIA        | True  | El estudiante existe pero no tiene consultas con fecha ≤ hoy (botón deshabilitado, no es un error) |
| CONSULTA_PREVIA_ENCONTRADA | True  | Sí tiene al menos una consulta previa (botón habilitado)                        |
| CONSULTA_NO_VALIDA         | False | El `idConsulta` indicado no existe, no es previa a hoy, o es de otro estudiante |
| COMPROBANTE_GENERADO       | True  | Se generó el PDF y se guardó en el perfil (`rutaArchivo` devuelto)              |
| COMPROBANTE_NO_ENCONTRADO  | False | No existe un comprobante guardado con ese `idConsulta`                          |
| ERROR_INESPERADO           | False | Cualquier excepción no controlada (ej. sin conexión)                            |

> Nota: `SIN_CONSULTA_PREVIA` devuelve `"exito": True` porque **no es un
> error** — es una respuesta válida que simplemente dice "botón
> deshabilitado". La UI debe fijarse en `resultado["habilitado"]`, no solo
> en `resultado["exito"]`, para decidir si mostrar el botón activo o no.

### Renovación del seguro (`servicioRenovacion`)

Métodos públicos (ambos reciben la matrícula y un `fechaReferencia` opcional, útil para pruebas):

- `renovarSeguro(matricula)` — valida y ejecuta la renovación.
- `consultarEstadoSeguro(matricula)` — devuelve `estadoVigencia` (`Vigente`,
  `Vencido` o `Sin vigencia registrada`) y las fechas de vigencia. Sirve para
  el estado en el perfil y para mostrar la vigencia en el carnet digital.

Reglas de `renovarSeguro`, en el orden en que se validan:

1. La matrícula debe existir en `estudiantes`.
2. El estudiante debe tener una afiliación con `estado = activo`.
3. Debe haber un periodo académico vigente a la fecha de hoy.
4. El estudiante debe figurar como `matriculado` en ese periodo.
5. El seguro no debe estar ya renovado para ese periodo (`fechaFinVigencia` menor a la `fechaFin` del periodo).

La nueva vigencia va desde `fechaInicio` hasta `fechaFin` del periodo vigente.

| codigo                       | exito | Cuándo ocurre                                                                      |
|------------------------------|-------|------------------------------------------------------------------------------------|
| MATRICULA_NO_ESPECIFICADA    | False | La matrícula llegó vacía                                                           |
| MATRICULA_INEXISTENTE        | False | La matrícula no existe en el nodo `estudiantes`                                    |
| SIN_AFILIACION_ACTIVA        | False | No hay afiliación activa; el estudiante debe afiliarse primero                     |
| PERIODO_NO_VIGENTE           | False | Ningún periodo académico contiene la fecha de hoy                                  |
| NO_MATRICULADO_EN_PERIODO    | False | No está matriculado en el periodo vigente (`idPeriodo` devuelto)                   |
| YA_RENOVADO_EN_PERIODO       | False | El seguro ya cubre el periodo vigente (`idPeriodo` y `fechaFinVigencia` devueltos) |
| RENOVACION_EXITOSA           | True  | Se actualizaron `seguros`, `renovaciones` y `tieneSeguroActivo` en una sola escritura |
| ESTADO_SEGURO_OBTENIDO       | True  | Respuesta de `consultarEstadoSeguro` con la vigencia y su estado                   |
| ERROR_INESPERADO             | False | Cualquier excepción no controlada (ej. sin conexión)                               |