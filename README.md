# Tienda Nueva

Sistema de gestión de inventario y ventas con interfaz gráfica.

## Requisitos

- Python 3.8 o superior
- Git

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/dylantopg/tienda-python.git
cd tienda-python
```

2. Crear entorno virtual:
```bash
python -m venv .venv
```

3. Activar el entorno virtual:
- Windows:
```bash
.venv\Scripts\activate
```
- Linux/Mac:
```bash
source .venv/bin/activate
```

4. Instalar pip en el entorno virtual (si es necesario):
```bash
python -m ensurepip --upgrade
```

5. Instalar dependencias:
```bash
python -m pip install -r requirements.txt
```

## Ejecutar la aplicación

Con el entorno virtual activado:
```bash
python src/gui/app.py
```

## Características

- Gestión de inventario
- Registro de ventas
- Historial de precios
- Exportación de reportes
- Impresión de tickets

## Estructura del Proyecto

- `src/` - Código fuente principal
  - `inventory/` - Lógica de inventario (modelos y servicios)
  - `gui/` - Interfaz gráfica de usuario (PySide6)
- `tests/` - Pruebas automatizadas con pytest
- `README.md` - Documentación del proyecto

## Instalación de dependencias

Se recomienda usar un entorno virtual y [uv](https://github.com/astral-sh/uv) para la gestión de dependencias.

```bash
uv venv .venv
source .venv/bin/activate  # o .venv\Scripts\activate en Windows
uv pip install pytest ruff pyside6
```

## Ejecución de la aplicación GUI

```bash
python -m src.gui.app
```

## Ejecución de pruebas

```bash
pytest
```

## Formato y estilo

Se utiliza [Ruff](https://github.com/astral-sh/ruff) para mantener la consistencia del código:

```bash
ruff check src tests
```

## Descripción funcionalidad actual

- Gestión de productos en inventario: alta, refill, edición y visualización en tabla.
- Interfaz gráfica sencilla con PySide6.
- Código modular y fácil de extender.

## Próximos pasos

- Persistencia en base de datos
- Control de usuarios y roles 


## INSTRUCCIONES
Install uv if you haven't already (you can find it at https://github.com/astral-sh/uv)
Create and activate the virtual environment
   uv venv .venv
   .venv\Scripts\activate  # Since you're on Windows
  uv pip install pytest ruff pyside6
  pip install -r requirements.txt


  PARA EJECUTAR
     python -m src.gui.app