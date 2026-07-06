-- =====================================================================
-- SGRSI - Datos de prueba (seed data)
-- Ejecutar DESPUÉS de esquema.sql
-- =====================================================================

-- Usuario administrador inicial
-- Contraseña en texto plano para pruebas: "admin123"
-- En app.py se compara con generate_password_hash al crear usuarios reales
INSERT INTO usuarios (nombre, apellido, email, contrasena_hash, id_rol) VALUES
('Admin', 'Cronos', 'admin@iti.edu.uy', 'pbkdf2:sha256:600000$placeholder$0000000000000000000000000000000000000000000000000000000000000000', 1),
('Gissel', 'Silvera', 'gissel@iti.edu.uy', 'pbkdf2:sha256:600000$placeholder$0000000000000000000000000000000000000000000000000000000000000000', 2),
('Diego', 'de Bethencourt', 'diego@iti.edu.uy', 'pbkdf2:sha256:600000$placeholder$0000000000000000000000000000000000000000000000000000000000000000', 2),
('Andres', 'Cabrera', 'andres@iti.edu.uy', 'pbkdf2:sha256:600000$placeholder$0000000000000000000000000000000000000000000000000000000000000000', 2),
('Profesor', 'Demo', 'docente@iti.edu.uy', 'pbkdf2:sha256:600000$placeholder$0000000000000000000000000000000000000000000000000000000000000000', 3);

-- Laboratorios
INSERT INTO laboratorios (nombre, numero_salon, capacidad) VALUES
('Laboratorio de Informática 1', 'Salón 12', 25),
('Laboratorio de Informática 2', 'Salón 14', 25),
('Taller de Electrónica', 'Salón 8', 15),
('Sala de Proyectos', 'Salón 20', 10);

-- Equipos (mezcla de tipos y estados)
INSERT INTO equipos (identificador, id_tipo_equipo, marca, modelo, id_estado_equipo, id_laboratorio, observaciones) VALUES
('PC-101', 1, 'Dell', 'OptiPlex 3070', 1, 1, 'Funcionando correctamente'),
('PC-102', 1, 'Dell', 'OptiPlex 3070', 1, 1, NULL),
('PC-103', 1, 'Dell', 'OptiPlex 3070', 3, 1, 'No enciende, posible fuente quemada'),
('PC-104', 1, 'HP', 'ProDesk 400', 4, 1, 'Sistema operativo corrupto'),
('PC-105', 1, 'HP', 'ProDesk 400', 1, 2, NULL),
('PC-106', 1, 'HP', 'ProDesk 400', 2, 2, 'Falta el mouse'),
('MON-201', 3, 'Samsung', 'S22F350', 1, 1, NULL),
('MON-202', 3, 'Samsung', 'S22F350', 5, 1, 'Pantalla rota'),
('MON-203', 3, 'LG', '22MK400H', 1, 2, NULL),
('PROY-301', 4, 'Epson', 'PowerLite X39', 1, 4, NULL),
('PROY-302', 4, 'Epson', 'PowerLite X39', 3, 4, 'No proyecta imagen, posible lámpara quemada'),
('SW-401', 5, 'TP-Link', 'TL-SG1016', 1, 1, NULL),
('LAP-501', 2, 'Lenovo', 'ThinkPad E14', 1, NULL, 'Disponible para préstamo'),
('LAP-502', 2, 'Lenovo', 'ThinkPad E14', 1, NULL, 'Disponible para préstamo');

-- Tickets de ejemplo
INSERT INTO tickets (id_usuario, id_tecnico, id_equipo, id_laboratorio, incidente, descripcion, id_prioridad, id_estado_ticket) VALUES
(6, 3, 3, 1, 'Problema de hardware', 'La PC-103 no enciende. Se revisó el cable de alimentación sin éxito.', 1, 2),
(6, NULL, 4, 1, 'Problema de software', 'PC-104 no carga el sistema operativo, pantalla azul al iniciar.', 1, 1),
(6, 4, 8, 1, 'Problema de hardware', 'El monitor MON-202 tiene la pantalla rota, requiere reemplazo.', 2, 1),
(6, NULL, 6, 2, 'Faltante', 'Falta el mouse de la PC-106.', 3, 1),
(6, 5, 11, 4, 'Problema de hardware', 'El proyector de Sala de Proyectos no enciende la lámpara.', 1, 2),
(6, 3, NULL, 1, 'Otro', 'Solicito revisión general de los equipos antes del inicio del curso.', 3, 3);

-- Solicitudes de servicio de ejemplo
INSERT INTO solicitudes (id_usuario, id_tipo_solicitud, id_laboratorio, descripcion, fecha_necesaria, id_estado_solicitud) VALUES
(6, 1, 1, 'Instalar Python 3.12 y Visual Studio Code en todas las PC del laboratorio 1.', '2026-04-20', 1),
(6, 3, 2, 'Preparar el laboratorio 2 para la clase de redes: verificar conectividad de todos los equipos.', '2026-04-18', 2),
(6, 2, 4, 'Configurar el proyector de la Sala de Proyectos para presentaciones HDMI.', '2026-04-22', 1),
(6, 1, 1, 'Actualizar el navegador Chrome en todas las máquinas.', NULL, 3);

-- Préstamos de ejemplo
INSERT INTO prestamos (id_equipo, id_usuario, id_tecnico, fecha_devolucion_est, id_estado_prestamo, observaciones) VALUES
(13, 6, 3, '2026-04-25', 1, 'Préstamo para presentación en clase'),
(14, 6, 4, '2026-04-15', 2, 'Devuelto en buen estado');

-- Repuestos de ejemplo
INSERT INTO repuestos (nombre, marca, cantidad, stock_minimo, ubicacion) VALUES
('Memoria RAM DDR4 4GB', 'Kingston', 5, 2, 'Estante A1'),
('Disco SSD 240GB', 'Kingston', 3, 1, 'Estante A2'),
('Cable HDMI', 'Generico', 10, 3, 'Cajón B1'),
('Mouse USB', 'Logitech', 8, 3, 'Cajón B2'),
('Teclado USB', 'Logitech', 4, 2, 'Cajón B2'),
('Fuente de poder ATX 500W', 'Generico', 2, 1, 'Estante A3');

-- Historial de ejemplo
INSERT INTO historial_equipos (id_equipo, id_usuario, id_estado_equipo, descripcion) VALUES
(3, 3, 3, 'Se detectó que la PC no enciende durante revisión de rutina.'),
(4, 4, 4, 'Sistema operativo corrupto detectado durante clase.'),
(8, 4, 5, 'Pantalla del monitor rota, retirado del laboratorio.');
