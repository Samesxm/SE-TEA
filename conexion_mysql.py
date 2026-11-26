import mysql.connector
from mysql.connector import pooling
from mysql.connector import Error
import streamlit as st

@st.cache_resource
def iniciar_pool_conexiones():
    try:
        pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="sistema_experto_pool",
            pool_size=5,
            pool_reset_session=True,
            host=st.secrets["db_credenciales"]["host"],
            port=int(st.secrets["db_credenciales"].get("port", 3306)),
            user=st.secrets["db_credenciales"]["usuario"],
            password=st.secrets["db_credenciales"]["password"],
            database=st.secrets["db_credenciales"]["database"]
        )
        return pool
    except Error as e:
        st.error(f"Error al inicializar el pool de conexiones: {e}")
        return None

pool_conexiones = iniciar_pool_conexiones()

def obtener_conexion():
    try:
        if pool_conexiones:
            return pool_conexiones.get_connection()
    except Error as e:
        st.error(f"Error al obtener conexión del pool: {e}")
        return None

def guardar_resultado_paciente(
    nombre_paciente, edad, convivencia, ocupacion,
    estado_medicacion, detalle_medicacion,
    consumo_sustancias, detalle_sustancias,
    bdi, bai, pss, diag_bdi, diag_bai, diag_pss, comorbilidad
):
    conexion = obtener_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            sql = """INSERT INTO pacientes_resultados 
                     (identificador, edad, convivencia_familiar, ocupacion,
                      estado_medicacion, detalle_medicacion,
                      consumo_sustancias, detalle_sustancias,
                      score_bdi, score_bai, score_pss,
                      diag_bdi, diag_bai, diag_pss, comorbilidad) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            valores = (
                nombre_paciente, edad, convivencia, ocupacion,
                estado_medicacion, detalle_medicacion,
                consumo_sustancias, detalle_sustancias,
                bdi, bai, pss, diag_bdi, diag_bai, diag_pss, comorbilidad
            )
            cursor.execute(sql, valores)
            conexion.commit()
            return True
        except Exception as e:
            st.error(f"Error al guardar en base de datos: {e}")
            return False
        finally:
            cursor.close()
            conexion.close()
    return False

def obtener_historial_pacientes():
    conexion = obtener_conexion()
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            sql = "SELECT * FROM pacientes_resultados ORDER BY fecha_evaluacion DESC"
            cursor.execute(sql)
            resultados = cursor.fetchall()
            return resultados
        except Exception as e:
            st.error(f"Error al consultar la base de datos: {e}")
            return []
        finally:
            cursor.close()
            conexion.close()
    return []