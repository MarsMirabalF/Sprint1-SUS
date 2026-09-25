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
│   │   └── servicioAfiliacion.py       -> lógica de la HU 6 (afiliación al seguro)
│   ├── baseDatos/
│   │   ├── esquemaBaseDatos.md         -> diseño de nodos "estudiantes" / "afiliados"
│   │   ├── database.rules.json         -> reglas / índices de la Realtime Database
│   │   └── sembrarDatosPrueba.py       -> (opcional) datos de ejemplo para probar
│   ├── credenciales/                   -> aquí va el JSON de la cuenta de servicio (NO se sube a Git)
│   └── requirements.txt
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

## Usar el servicio de afiliación desde código

```python
from servidorSeguroUniversitario.servicios.servicioAfiliacion import servicioAfiliacion

servicio = servicioAfiliacion()
resultado = servicio.afiliarEstudiante({
    "matricula": "20231001",
    "cedulaIdentidad": "9876543",
    "nombreCompleto": "Maria Fernanda Rojas",
    "carrera": "Ingenieria de Sistemas",
    "correoElectronico": "maria.rojas@uni.edu.bo",
    "telefono": "70012345",
    "direccion": "Av. Siempre Viva #123",
    "fechaNacimiento": "2001-05-14",
})
print(resultado)
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

## Pendiente

- `clienteSeguroUniversitario/`: interfaz Tkinter (formulario, popups,
  advertencias) que consumirá `servicioAfiliacion.afiliarEstudiante(...)`.
- Empaquetado a `.exe` con PyInstaller una vez cerrado el Sprint 1 (las
  credenciales se distribuirán como archivo externo, no embebidas en el
  ejecutable, por seguridad).