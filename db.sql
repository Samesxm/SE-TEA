CREATE DATABASE IF NOT EXISTS sistema_experto_emocional;
USE sistema_experto_emocional;

CREATE TABLE IF NOT EXISTS pacientes_resultados (
    id INT AUTO_INCREMENT PRIMARY KEY,
    identificador VARCHAR(100) NOT NULL,
    edad INT NOT NULL,
    score_bdi INT NOT NULL,
    score_bai INT NOT NULL,
    score_pss INT NOT NULL,
    diag_bdi VARCHAR(50) NOT NULL,
    diag_bai VARCHAR(50) NOT NULL,
    diag_pss VARCHAR(50) NOT NULL,
    comorbilidad TEXT,
    fecha_evaluacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);