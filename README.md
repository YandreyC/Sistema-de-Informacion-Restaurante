# Sistema de Información para Restaurante

## Requerimientos del sistema

### 1. Requisitos de software

- **Python**: 3.11 o superior
- **Django**: 6.0.5
- **Paquete de conexión con SQL Server**: `django-mssql` 1.8
- **Sistema operativo**: Windows, Linux o macOS
- **Gestor de base de datos**: Microsoft SQL Server
- **Driver ODBC**: Microsoft ODBC Driver 17 for SQL Server

### 2. Requisitos de base de datos

El proyecto está configurado para conectarse a una base de datos SQL Server con los siguientes parámetros:

- **Nombre de la base de datos**: `Restaurante_DB`
- **Usuario**: `sa`
- **Contraseña**: `123456789`
- **Host**: `localhost\SQLEXPRESS`
- **Puerto**: `1433`

> Si el entorno no usa SQL Server Express, o si la contraseña/usuario cambian, debe ajustarse la configuración de conexión en `config/settings.py`.

### 3. Requisitos de hardware

- **Procesador**: 1 GHz o superior
- **Memoria RAM**: 2 GB mínimo
- **Espacio en disco**: al menos 200 MB libres
- **Conexión a red**: opcional, solo si se accede de forma remota

### 4. Requisitos funcionales

El sistema permite gestionar:

- **Clientes**
- **Empleados**
- **Mesas**
- **Platos**
- **Órdenes**
- **Facturación**
- **Autenticación y autorización por roles**

Roles disponibles:

- **Administrador**
- **Mesero**
- **Cajero**

### 5. Requisitos de ejecución

1. Crear y activar un entorno virtual de Python.
2. Instalar las dependencias:

   ```bash
   pip install django mssql-django pyodbc
   ```

3. Verificar que SQL Server esté corriendo y que exista la base de datos `Restaurante_DB`.
4. Aplicar las migraciones:

   ```bash
   python manage.py migrate
   ```

5. Ejecutar el servidor local:

   ```bash
   python manage.py runserver
   ```

### 6. Recomendaciones

- Usar una versión estable de Python 3.11 o 3.12.
- Mantener seguros los datos de conexión a la base de datos.
- No exponer la clave secreta de Django ni la contraseña del servidor en entornos productivos.
- Para ambientes de desarrollo, se recomienda usar una instancia local de SQL Server Express.

### 7. Dependencias verificadas en este entorno

- Python: **3.14.4**
- Django: **6.0.5**
- `django-mssql`: **1.8**

## Nota

Este README describe los requisitos técnicos mínimos para instalar y ejecutar el sistema en un entorno local de desarrollo.
