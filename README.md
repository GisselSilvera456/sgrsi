# SGRSI — Sistema de Gestión de Recursos y Soporte de Informática
**Grupo Cronos · Change On Time · ITI – CETP 2026**

---

## Despliegue en PythonAnywhere

### 1. Clonar el repositorio

En la consola de PythonAnywhere (pestaña **Consoles → Bash**):

```bash
cd /home/2mhiti2025
git clone https://github.com/cronoscotuy-creator/sgrsi.git
cd sgrsi
```

### 2. Instalar dependencias

```bash
pip3.10 install --user -r requirements.txt
```


### 8. Ingresar al sistema

- URL: `https://2mhiti2025.pythonanywhere.com/login`
- Email: `admin@iti.edu.uy`
- Contraseña: `admin123`

---

## Estructura del proyecto

```
sgrsi/
├── app.py                  # Aplicación Flask principal
├── requirements.txt        # Dependencias Python
├── .env.example            # Ejemplo de variables de entorno
├── .gitignore
├── README.md
├── base_datos/
│   ├── esquema.sql         # DDL — creación de tablas
│   └── seed_data.sql       # DML — datos de prueba
├── static/
│   ├── css/style.css       # Estilos con paleta Ceibal
│   └── js/main.js          # JavaScript general
└── templates/
    ├── base.html           # Layout compartido con navbar
    ├── login.html
    ├── index.html          # Dashboard
    ├── inventario.html     # RF-02
    ├── tickets.html        # RF-03 Mesa de ayuda
    ├── solicitudes.html    # RF-05
    ├── prestamos.html      # RF-07
    └── metricas.html       # RF-10
```

---

## Módulos implementados

| Módulo | RF | Descripción |
|---|---|---|
| Dashboard | RF-10 | Resumen general del estado del sistema |
| Inventario | RF-02, RF-04 | ABM de equipos, estados e historial |
| Mesa de Ayuda | RF-03 | Tickets con prioridad, menú de incidentes y resolución |
| Solicitudes | RF-05 | Reemplaza el email para solicitudes de docentes |
| Préstamos | RF-07 | Control de préstamos y devoluciones |
| Métricas | RF-10 | Estadísticas del sistema |
| Control de acceso | RF-06 | Roles: administrador, técnico, solicitante |
