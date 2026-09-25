# Esquema de Base de Datos

Realtime Database nodos en plural / camelCase, atributos en camelCase, según los
estándares del grupo.

## 1. Nodo `estudiantes`

Representa los registros oficiales de la universidad (matrícula, cédula, si ya
tiene seguro activo, etc.). **Este backend NO los crea**: se asume que ya existen
(cargados por la universidad o por otra HU). Solo se leen y se actualiza el campo
`tieneSeguroActivo`.

La **clave de cada registro es la matrícula** (no se usa push-id), para poder
buscar por matrícula en O(1):

```json
{
  "estudiantes": {
    "20231001": {
      "cedulaIdentidad": "9876543",
      "nombreCompleto": "Maria Fernanda Rojas",
      "carrera": "Ingenieria de Sistemas",
      "tieneSeguroActivo": false
    },
    "20231002": {
      "cedulaIdentidad": "1122334",
      "nombreCompleto": "Juan Pablo Quispe",
      "carrera": "Medicina",
      "tieneSeguroActivo": true
    }
  }
}
```

> Supuesto: la matrícula no contiene los caracteres inválidos para claves de
> Firebase (`. # $ [ ]` ni `/`). Si en su caso la matrícula puede traer esos
> caracteres, avísenme y cambio la búsqueda a un índice por campo en vez de
> clave.

## 2. Nodo `afiliados`

Registros creados por esta HU cuando la afiliación es exitosa. Clave = push-id
autogenerado por Firebase.

```json
{
  "afiliados": {
    "-NxAbCdEfGhIjKl": {
      "matricula": "20231001",
      "cedulaIdentidad": "9876543",
      "nombreCompleto": "Maria Fernanda Rojas",
      "carrera": "Ingenieria de Sistemas",
      "correoElectronico": "maria.rojas@uni.edu.bo",
      "telefono": "70012345",
      "direccion": "Av. Siempre Viva #123",
      "fechaNacimiento": "2001-05-14",
      "fechaAfiliacion": "2026-09-25 10:32:00",
      "estado": "activo"
    }
  }
}
```

### Campos obligatorios del formulario (supuesto — ajustar si su HU define otros)

`matricula`, `cedulaIdentidad`, `nombreCompleto`, `carrera`, `correoElectronico`,
`telefono`, `direccion`, `fechaNacimiento`.

Si el listado real de campos del formulario es distinto, solo hay que editar la
constante `CAMPOS_OBLIGATORIOS` en `servicios/servicioAfiliacion.py`.

## 3. Reglas de índice (`database.rules.json`)

Se indexa `afiliados/cedulaIdentidad` porque el servicio consulta por cédula
para verificar si ya existe un seguro activo con esa cédula (aunque la matrícula
sea distinta).