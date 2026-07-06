USE `2mhiti2025$default`;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    email VARCHAR(100),
    password VARCHAR(255),
    rol VARCHAR(50)
);

CREATE TABLE tickets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20),
    descripcion TEXT,
    estado VARCHAR(50),
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE inventario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20),
    tipo VARCHAR(50),
    descripcion TEXT,
    ubicacion VARCHAR(100),
    estado VARCHAR(50)
);

CREATE TABLE prestamos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    equipo_id INT,
    usuario_id INT,
    fecha_prestamo DATE,
    fecha_devolucion DATE,
    estado VARCHAR(50)
);