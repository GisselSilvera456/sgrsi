-- =====================================================================
-- SGRSI - Sistema de Gestión de Recursos y Soporte de Informática
-- Grupo: Cronos | ITI - CETP 2026
-- Esquema de base de datos (DDL) - Normalizado a 3FN
-- Base de datos destino en PythonAnywhere: 2mhiti2025$default
-- =====================================================================

-- ---------------------------------------------------------------------
-- Tabla: roles
-- Catálogo de roles del sistema (RF-06: control de acceso por roles)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS roles (
    id_rol      INT AUTO_INCREMENT PRIMARY KEY,
    nombre_rol  VARCHAR(30) NOT NULL UNIQUE,
    descripcion VARCHAR(150)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO roles (nombre_rol, descripcion) VALUES
    ('administrador', 'Acceso completo al sistema. Gestión de usuarios, inventario y métricas.'),
    ('tecnico',        'Atiende tickets, gestiona préstamos y actualiza estados de equipos.'),
    ('solicitante',    'Docentes y funcionarios. Crea tickets y solicitudes de servicio.');

-- ---------------------------------------------------------------------
-- Tabla: usuarios
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario      INT AUTO_INCREMENT PRIMARY KEY,
    nombre          VARCHAR(60)  NOT NULL,
    apellido        VARCHAR(60)  NOT NULL,
    email           VARCHAR(120) NOT NULL UNIQUE,
    contrasena_hash VARCHAR(255) NOT NULL,
    id_rol          INT NOT NULL,
    activo          TINYINT(1) NOT NULL DEFAULT 1,
    fecha_alta      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_usuarios_rol FOREIGN KEY (id_rol) REFERENCES roles(id_rol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- Tabla: laboratorios
-- RF-01: Gestión de laboratorios
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS laboratorios (
    id_laboratorio INT AUTO_INCREMENT PRIMARY KEY,
    nombre         VARCHAR(60) NOT NULL,
    numero_salon   VARCHAR(20) NOT NULL,
    capacidad      INT DEFAULT 0,
    activo         TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- Tabla: tipos_equipo
-- Catálogo de tipos de equipo (Laptop, PC, Monitor, Proyector, etc.)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tipos_equipo (
    id_tipo_equipo INT AUTO_INCREMENT PRIMARY KEY,
    nombre_tipo    VARCHAR(40) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO tipos_equipo (nombre_tipo) VALUES
    ('PC de escritorio'), ('Laptop'), ('Monitor'), ('Proyector'),
    ('Switch de red'), ('Periférico'), ('Otro');

-- ---------------------------------------------------------------------
-- Tabla: estados_equipo
-- Catálogo de estados (según entrevista al cliente)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS estados_equipo (
    id_estado_equipo INT AUTO_INCREMENT PRIMARY KEY,
    nombre_estado    VARCHAR(40) NOT NULL UNIQUE,
    color_hex        VARCHAR(7)  NOT NULL DEFAULT '#999999'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO estados_equipo (nombre_estado, color_hex) VALUES
    ('Correcto',           '#43B02A'),  -- verde Ceibal
    ('Faltante',           '#F7941E'),  -- naranja Ceibal
    ('Problema de hardware','#E63946'), -- rojo
    ('Problema de software','#FFC72C'), -- amarillo
    ('Dañado',             '#7F8C8D');  -- gris

-- ---------------------------------------------------------------------
-- Tabla: equipos
-- RF-02: ABM de inventario tecnológico
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS equipos (
    id_equipo        INT AUTO_INCREMENT PRIMARY KEY,
    identificador    VARCHAR(30) NOT NULL UNIQUE,
    id_tipo_equipo   INT NOT NULL,
    marca            VARCHAR(50),
    modelo           VARCHAR(50),
    id_estado_equipo INT NOT NULL,
    id_laboratorio   INT DEFAULT NULL,
    observaciones    TEXT,
    fecha_alta       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_equipos_tipo     FOREIGN KEY (id_tipo_equipo)   REFERENCES tipos_equipo(id_tipo_equipo),
    CONSTRAINT fk_equipos_estado   FOREIGN KEY (id_estado_equipo) REFERENCES estados_equipo(id_estado_equipo),
    CONSTRAINT fk_equipos_lab      FOREIGN KEY (id_laboratorio)   REFERENCES laboratorios(id_laboratorio)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- Tabla: historial_equipos
-- RF-04 / RF-09: trazabilidad e historial por equipo
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS historial_equipos (
    id_historial     INT AUTO_INCREMENT PRIMARY KEY,
    id_equipo        INT NOT NULL,
    id_usuario       INT NOT NULL,
    id_estado_equipo INT NOT NULL,
    descripcion      TEXT,
    fecha            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_historial_equipo  FOREIGN KEY (id_equipo)        REFERENCES equipos(id_equipo),
    CONSTRAINT fk_historial_usuario FOREIGN KEY (id_usuario)       REFERENCES usuarios(id_usuario),
    CONSTRAINT fk_historial_estado  FOREIGN KEY (id_estado_equipo) REFERENCES estados_equipo(id_estado_equipo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- Tabla: prioridades
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS prioridades (
    id_prioridad  INT AUTO_INCREMENT PRIMARY KEY,
    nombre        VARCHAR(20) NOT NULL UNIQUE,
    orden         INT NOT NULL,
    color_hex     VARCHAR(7) NOT NULL DEFAULT '#999999'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO prioridades (nombre, orden, color_hex) VALUES
    ('Alta',  1, '#E63946'),
    ('Media', 2, '#FFC72C'),
    ('Baja',  3, '#43B02A');

-- ---------------------------------------------------------------------
-- Tabla: estados_ticket
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS estados_ticket (
    id_estado_ticket INT AUTO_INCREMENT PRIMARY KEY,
    nombre_estado    VARCHAR(30) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO estados_ticket (nombre_estado) VALUES
    ('Pendiente'), ('En proceso'), ('Resuelto');

-- ---------------------------------------------------------------------
-- Tabla: tickets
-- RF-03: Mesa de ayuda - registro de incidencias
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tickets (
    id_ticket        INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario       INT NOT NULL,            -- quien reporta
    id_tecnico       INT DEFAULT NULL,        -- quien atiende
    id_equipo        INT DEFAULT NULL,
    id_laboratorio   INT DEFAULT NULL,
    incidente        VARCHAR(100) NOT NULL,   -- tipo de incidente (menú)
    descripcion      TEXT,                    -- campo editable libre
    id_prioridad     INT NOT NULL,
    id_estado_ticket INT NOT NULL DEFAULT 1,
    fecha_apertura   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_cierre     DATETIME DEFAULT NULL,
    nota_resolucion  TEXT,
    CONSTRAINT fk_tickets_usuario  FOREIGN KEY (id_usuario)       REFERENCES usuarios(id_usuario),
    CONSTRAINT fk_tickets_tecnico  FOREIGN KEY (id_tecnico)       REFERENCES usuarios(id_usuario),
    CONSTRAINT fk_tickets_equipo   FOREIGN KEY (id_equipo)        REFERENCES equipos(id_equipo),
    CONSTRAINT fk_tickets_lab      FOREIGN KEY (id_laboratorio)   REFERENCES laboratorios(id_laboratorio),
    CONSTRAINT fk_tickets_prior    FOREIGN KEY (id_prioridad)     REFERENCES prioridades(id_prioridad),
    CONSTRAINT fk_tickets_estado   FOREIGN KEY (id_estado_ticket) REFERENCES estados_ticket(id_estado_ticket)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- Tabla: tipos_solicitud
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tipos_solicitud (
    id_tipo_solicitud INT AUTO_INCREMENT PRIMARY KEY,
    nombre            VARCHAR(60) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO tipos_solicitud (nombre) VALUES
    ('Instalación de software'),
    ('Configuración de equipo'),
    ('Preparación de laboratorio'),
    ('Otro');

-- ---------------------------------------------------------------------
-- Tabla: estados_solicitud
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS estados_solicitud (
    id_estado_solicitud INT AUTO_INCREMENT PRIMARY KEY,
    nombre_estado       VARCHAR(30) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO estados_solicitud (nombre_estado) VALUES
    ('Pendiente'), ('En proceso'), ('Completada'), ('Rechazada');

-- ---------------------------------------------------------------------
-- Tabla: solicitudes
-- RF-05: Gestión de solicitudes de servicio
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS solicitudes (
    id_solicitud        INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario          INT NOT NULL,
    id_tipo_solicitud   INT NOT NULL,
    id_laboratorio      INT DEFAULT NULL,
    descripcion         TEXT NOT NULL,
    fecha_solicitud     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_necesaria     DATE DEFAULT NULL,
    id_estado_solicitud INT NOT NULL DEFAULT 1,
    CONSTRAINT fk_solicitudes_usuario FOREIGN KEY (id_usuario)          REFERENCES usuarios(id_usuario),
    CONSTRAINT fk_solicitudes_tipo    FOREIGN KEY (id_tipo_solicitud)   REFERENCES tipos_solicitud(id_tipo_solicitud),
    CONSTRAINT fk_solicitudes_lab     FOREIGN KEY (id_laboratorio)      REFERENCES laboratorios(id_laboratorio),
    CONSTRAINT fk_solicitudes_estado  FOREIGN KEY (id_estado_solicitud) REFERENCES estados_solicitud(id_estado_solicitud)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- Tabla: estados_prestamo
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS estados_prestamo (
    id_estado_prestamo INT AUTO_INCREMENT PRIMARY KEY,
    nombre_estado      VARCHAR(30) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO estados_prestamo (nombre_estado) VALUES
    ('Activo'), ('Devuelto'), ('Atrasado');

-- ---------------------------------------------------------------------
-- Tabla: prestamos
-- RF-07: Gestión de préstamos (módulo futuro, diseñado desde ahora)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS prestamos (
    id_prestamo          INT AUTO_INCREMENT PRIMARY KEY,
    id_equipo            INT NOT NULL,
    id_usuario           INT NOT NULL,        -- quien retira el equipo
    id_tecnico           INT DEFAULT NULL,    -- quien entrega
    fecha_prestamo       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_devolucion_est DATE DEFAULT NULL,
    fecha_devolucion_real DATETIME DEFAULT NULL,
    id_estado_prestamo   INT NOT NULL DEFAULT 1,
    observaciones        TEXT,
    CONSTRAINT fk_prestamos_equipo   FOREIGN KEY (id_equipo)          REFERENCES equipos(id_equipo),
    CONSTRAINT fk_prestamos_usuario  FOREIGN KEY (id_usuario)         REFERENCES usuarios(id_usuario),
    CONSTRAINT fk_prestamos_tecnico  FOREIGN KEY (id_tecnico)         REFERENCES usuarios(id_usuario),
    CONSTRAINT fk_prestamos_estado   FOREIGN KEY (id_estado_prestamo) REFERENCES estados_prestamo(id_estado_prestamo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------------
-- Tabla: repuestos
-- RF-08: Inventario interno de repuestos
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS repuestos (
    id_repuesto   INT AUTO_INCREMENT PRIMARY KEY,
    nombre        VARCHAR(80) NOT NULL,
    marca         VARCHAR(50),
    cantidad      INT NOT NULL DEFAULT 0,
    stock_minimo  INT NOT NULL DEFAULT 1,
    ubicacion     VARCHAR(80)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================================
-- ÍNDICES adicionales para optimizar consultas frecuentes (RF-10)
-- =====================================================================
CREATE INDEX idx_tickets_estado    ON tickets(id_estado_ticket);
CREATE INDEX idx_tickets_prioridad ON tickets(id_prioridad);
CREATE INDEX idx_equipos_estado    ON equipos(id_estado_equipo);
CREATE INDEX idx_solicitudes_estado ON solicitudes(id_estado_solicitud);
