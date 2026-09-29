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
│   │   ├── servicioCobertura.py        -> lógica de la HU 1 (consulta de cobertura)
│   │   ├── servicioComprobante.py      -> lógica de la HU 17 (comprobantes médicos)
│   │   ├── servicioRenovacion.py       -> lógica de la HU 10 (renovación del seguro)
│   │   └── servicioHistorialJustificativos.py -> lógica de la HU 11 (historial de justificativos)
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

Ejecutar siempre desde la carpeta **raíz** del proyecto (donde está `principal.py`),
para que los imports (`servidorSeguroUniversitario.xxx`) funcionen.

## Configuración (una sola vez)

1. En su Realtime Database, importen/adapten las reglas de
   `servidorSeguroUniversitario/baseDatos/database.rules.json` (están abiertas
   para desarrollo; deben restringirse cuando haya autenticación).
2. En Firebase Console → Configuración del proyecto → Cuentas de servicio,
   generen una clave privada y guárdenla como:
   `servidorSeguroUniversitario/credenciales/credencialesFirebase.json`
   (ya está en `.gitignore`, no se sube al repo).
3. La URL de la Realtime Database ya está escrita directamente en
   `servidorSeguroUniversitario/configuracion/configuracionFirebase.py`
   (constante `URL_BASE_DATOS`). No hace falta configurar variables de
   entorno para desarrollo local. Solo si necesitan sobreescribirla en otra
   máquina, pueden definir `FIREBASE_URL_BASE_DATOS` / `FIREBASE_CREDENCIALES`,
   que tienen prioridad.
4. `pip install -r servidorSeguroUniversitario\requirements.txt`

## Ejecutar el proyecto

```powershell
python principal.py
```

## Probar el backend con datos de ejemplo

```powershell
python -m servidorSeguroUniversitario.baseDatos.sembrarDatosPrueba
```

`resultado["codigo"]` es lo que la UI usará para decidir qué popup/advertencia
mostrar:

| codigo                | exito | Cuándo ocurre                                                     |
|------------------------|-------|----------------------------------------------------------------------|
| CAMPOS_INCOMPLETOS      | False | Faltó algún campo obligatorio (ver `camposFaltantes`)                |
| FORMATO_INVALIDO        | False | Cédula, correo o teléfono con formato inválido (`camposInvalidos`)   |
| MATRICULA_INEXISTENTE   | False | La matrícula no existe en el nodo `estudiantes`                      |
| SEGURO_YA_ACTIVO        | False | El estudiante ya tiene seguro activo (por matrícula o por cédula)    |
| AFILIACION_EXITOSA      | True  | Se creó el registro en `afiliados` (`idAfiliado` devuelto)           |
| ERROR_INESPERADO        | False | Cualquier excepción no controlada (ej. sin conexión)                 |

## HU 1 — Consulta de cobertura del seguro

**Cambio en la DB:** se agregó el nodo `serviciosMedicos` (catálogo de
atenciones médicas y si están cubiertas o no). Detalle completo del esquema
en `servidorSeguroUniversitario/baseDatos/esquemaBaseDatos.md`. El script
`sembrarDatosPrueba.py` ahora también siembra un catálogo de ejemplo (correr
igual que antes, ya incluye los tres nodos).

| codigo                     | exito | Cuándo ocurre                                                |
|-----------------------------|-------|------------------------------------------------------------------|
| LISTA_OBTENIDA               | True  | Se devolvió la lista de servicios médicos                        |
| CATALOGO_VACIO               | True  | El nodo `serviciosMedicos` existe pero no tiene registros aún    |
| SERVICIO_NO_ESPECIFICADO     | False | No se indicó `idServicio` al consultar un servicio puntual       |
| SERVICIO_INEXISTENTE         | False | El `idServicio` consultado no existe en el catálogo              |
| COBERTURA_OBTENIDA           | True  | Se devolvió el estado de cobertura del servicio seleccionado     |
| ERROR_INESPERADO             | False | Cualquier excepción no controlada (ej. sin conexión)             |

## HU 17 — Obtención de comprobantes médicos

**Cambio en la DB:** se agregaron dos nodos:
- `consultasMedicas` (registro de atenciones médicas por estudiante, con
  fecha e índice por `matricula`).
- `comprobantesMedicos` (el PDF generado, guardado como texto base64 +
  metadatos, en el "perfil" del estudiante — clave = `idConsulta`, índice
  por `matricula`). Así el comprobante queda disponible para volver a verlo
  desde cualquier instalación de la app, no solo en la máquina donde se
  generó, y el equipo puede verlo conectándose a la misma Realtime Database.

Detalle completo en `servidorSeguroUniversitario/baseDatos/esquemaBaseDatos.md`.
El script `sembrarDatosPrueba.py` ahora también siembra consultas de
ejemplo (correr igual que antes, ya incluye los cinco nodos).

> ⚠️ **Los PDFs no se suben a GitHub.** Ni el archivo local en
> `comprobantesGenerados/` (ya está en `.gitignore`) ni el contenido dentro
> de `comprobantesMedicos` viajan por Git — ese nodo vive solo en Firebase.
> Lo que el repo comparte con el equipo es el código y el esquema de la DB;
> para ver los comprobantes guardados, cada quien se conecta con sus propias
> credenciales a la misma Realtime Database del proyecto.

**Firma digital (simulación):** el PDF ahora incluye una imagen de firma al
final del documento, tomada de
`servidorSeguroUniversitario/recursos/firmaDigital.jpg`. Es la misma imagen
para todos los comprobantes (no es una firma electrónica real verificable,
es un recurso gráfico fijo del proyecto) — **esta imagen sí se sube a
GitHub**, porque es un archivo del sistema, no un dato generado por un
usuario. Si en algún momento cambian la imagen de la firma, basta con
reemplazar ese archivo (mismo nombre) y no hay que tocar código.

**Dependencia nueva:** se agregó `fpdf2` a `requirements.txt` para generar
el PDF del comprobante. Si actualizaron el repo, corran de nuevo:
```powershell
pip install -r servidorSeguroUniversitario\requirements.txt
```

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

## HU 10 — Renovación del seguro universitario

**Cambio en la DB:** se agregaron cuatro nodos: `periodosAcademicos`,
`matriculaciones`, `seguros` y `renovaciones` (detalle en
`servidorSeguroUniversitario/baseDatos/esquemaBaseDatos.md`). Las reglas y el
script `sembrarDatosPrueba.py` ya los incluyen (se siembran con el mismo
comando de siempre). No hay dependencias nuevas.

Validaciones antes de aprobar (en este orden): matrícula existente →
afiliación activa → periodo académico vigente → matriculado en ese periodo →
no renovado ya en ese periodo.

| codigo                      | exito | Cuándo ocurre                                                     |
|------------------------------|-------|----------------------------------------------------------------------|
| MATRICULA_NO_ESPECIFICADA     | False | No se indicó la matrícula                                            |
| MATRICULA_INEXISTENTE         | False | La matrícula no existe en `estudiantes`                              |
| SIN_AFILIACION_ACTIVA         | False | No tiene afiliación activa (debe afiliarse primero, HU 6)            |
| PERIODO_NO_VIGENTE            | False | Hoy no cae dentro de ningún periodo académico                        |
| NO_MATRICULADO_EN_PERIODO     | False | No figura como matriculado en el periodo vigente (**renovación rechazada**) |
| YA_RENOVADO_EN_PERIODO        | False | Ya renovó para el periodo vigente                                    |
| RENOVACION_EXITOSA            | True  | Renovación aprobada; devuelve la nueva vigencia (para el popup)      |
| ESTADO_SEGURO_OBTENIDO        | True  | Respuesta de `consultarEstadoSeguro` (`estadoVigencia`: Vigente / Vencido / Sin vigencia registrada) |
| ERROR_INESPERADO              | False | Cualquier excepción no controlada (ej. sin conexión)                 |

> Los periodos de prueba llegan hasta julio de 2027. Como el periodo vigente
> se calcula con la fecha de hoy, si prueban fuera de ese rango ajusten las
> fechas en `sembrarDatosPrueba.py`. Los casos de prueba están descritos en
> el encabezado de ese script.

## HU 11 — Historial de justificativos médicos

Sin cambios de esquema: reutiliza `comprobantesMedicos` (HU 17). Nuevo:
`servidorSeguroUniversitario/servicios/servicioHistorialJustificativos.py`.

| codigo                      | exito | Cuándo ocurre                                      |
|------------------------------|-------|-----------------------------------------------------|
| MATRICULA_NO_ESPECIFICADA     | False | No se indicó la matrícula                            |
| SIN_JUSTIFICATIVOS            | True  | El estudiante aún no generó ningún justificativo     |
| HISTORIAL_OBTENIDO            | True  | Lista devuelta, ordenada de más reciente a más antiguo |
| ERROR_INESPERADO              | False | Excepción no controlada                              |

## Pendiente

- `clienteSeguroUniversitario/`: interfaz Tkinter para HU 6 (formulario,
  popups, advertencias), HU 1 (sección de cobertura, lista de servicios,
  estado visual por servicio) HU 17 (vista de atenciones, botón de
  descarga y pantalla de "mis comprobantes" guardados) y HU 10 (sección de
  renovación, estado de vigencia y popup de confirmación).
- Una pantalla/HU de administración que cargue y mantenga el catálogo
  `serviciosMedicos` (por ahora se prueba con el script de datos de ejemplo).
- Procesos (fuera de este alcance) que carguen `periodosAcademicos` y
  `matriculaciones` reales; por ahora se prueban con datos de ejemplo.
- Una HU/proceso (fuera de este alcance) que registre las consultas médicas
  reales en `consultasMedicas` — por ahora también se prueba con datos de
  ejemplo.
- Empaquetado a `.exe` con PyInstaller una vez cerrado el Sprint 1 (las
  credenciales se distribuirán como archivo externo, no embebidas en el
  ejecutable, por seguridad).