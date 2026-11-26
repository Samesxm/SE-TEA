import os
import base64
import streamlit as st
import pandas as pd
from motor_inferencia import MotorInferencia
from conexion_mysql import guardar_resultado_paciente, obtener_historial_pacientes
from generador_pdf import (
    generar_pdf_expediente,
    generar_pdf_historial_general,
    generar_pdf_expediente_completo
)

st.set_page_config(
    page_title="SE-TEA | Tamizaje y Seguimiento Emocional",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# LOGOTIPO EN ESQUINA
# ==========================================
def obtener_logo_html(tamano=46):
    for nombre_archivo in ["logo.png", "logo.svg", "logo.jpg", "logo.jpeg"]:
        ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), nombre_archivo)
        if os.path.exists(ruta):
            with open(ruta, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
            ext = nombre_archivo.split(".")[-1]
            mime = "image/svg+xml" if ext == "svg" else f"image/{'jpeg' if ext in ['jpg', 'jpeg'] else 'png'}"
            return (
                f'<img src="data:{mime};base64,{b64}" alt="SE-TEA" '
                f'style="height:{tamano}px; width:{tamano}px; border-radius:12px; object-fit:cover; '
                f'border: 1.5px solid #B9A3DC; background:#ffffff; flex-shrink:0;" />'
            )

    return f"""
    <svg width="{tamano}" height="{tamano}" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" style="flex-shrink:0;">
        <defs>
            <linearGradient id="gradLogo" x1="0" y1="0" x2="64" y2="64" gradientUnits="userSpaceOnUse">
                <stop offset="0%" stop-color="#7353A6"/>
                <stop offset="100%" stop-color="#83B9DA"/>
            </linearGradient>
        </defs>
        <rect width="64" height="64" rx="16" fill="url(#gradLogo)"/>
        <circle cx="32" cy="23" r="8.5" fill="#F7F5FC"/>
        <path d="M17 48C17 39.7157 23.7157 33 32 33C40.2843 33 47 39.7157 47 48" stroke="#E9A4C5" stroke-width="5" stroke-linecap="round"/>
    </svg>
    """

# ==========================================
# SISTEMA DE DISEÑO CSS - PALETA SE-TEA
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #302944;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {background: transparent;}

    .stApp {
        background: radial-gradient(circle at top right, #EDE6FA 0%, #F7F5FC 48%, #F7F5FC 100%);
    }

    .block-container {
        padding-top: 1.3rem !important;
        padding-bottom: 3.5rem !important;
        max-width: 1140px !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #E4DBF4;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.3rem !important;
    }

    /* Cabecera fija con logo en esquina */
    .app-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: rgba(255, 255, 255, 0.96);
        border: 1px solid #E4DBF4;
        border-radius: 18px;
        padding: 14px 22px;
        margin-bottom: 20px;
        box-shadow: 0 8px 24px rgba(115, 83, 166, 0.06);
    }
    .app-brand {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .app-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #302944;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .app-subtitle {
        font-size: 0.82rem;
        color: #6B6285;
        margin: 2px 0 0 0;
    }
    .app-pill {
        background: #F7F5FC;
        border: 1px solid #B9A3DC;
        color: #7353A6;
        font-size: 0.78rem;
        font-weight: 600;
        padding: 6px 14px;
        border-radius: 999px;
        white-space: nowrap;
    }
    .app-pill.seguimiento {
        background: #EAF4FB;
        border-color: #83B9DA;
        color: #235B7D;
    }

    /* Stepper horizontal */
    .stepper {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        margin-bottom: 22px;
    }
    .step-item {
        background: rgba(255, 255, 255, 0.78);
        border: 1px solid #E4DBF4;
        border-radius: 14px;
        padding: 11px 16px;
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 0.85rem;
        color: #7B7294;
    }
    .step-item.active {
        background: #ffffff;
        border-color: #7353A6;
        color: #302944;
        font-weight: 600;
        box-shadow: 0 6px 16px rgba(115, 83, 166, 0.09);
    }
    .step-item.done {
        background: #F3F9FD;
        border-color: #83B9DA;
        color: #302944;
        font-weight: 500;
    }
    .step-num {
        width: 25px;
        height: 25px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 0.76rem;
        font-weight: 700;
        background: #EDE7F8;
        color: #7353A6;
        flex-shrink: 0;
    }
    .step-item.active .step-num {
        background: #7353A6;
        color: #ffffff;
    }
    .step-item.done .step-num {
        background: #83B9DA;
        color: #ffffff;
    }

    /* Barra de secciones diagnosticas activas */
    .diag-sections-bar {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-bottom: 16px;
    }
    .diag-sec-pill {
        flex: 1;
        min-width: 180px;
        background: #ffffff;
        border: 1.5px solid #E4DBF4;
        border-radius: 12px;
        padding: 10px 14px;
        font-size: 0.82rem;
        color: #6B6285;
    }
    .diag-sec-pill.current {
        border-color: #7353A6;
        background: #F4EFFC;
        color: #302944;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(115, 83, 166, 0.1);
    }
    .diag-sec-pill.completed {
        border-color: #83B9DA;
        background: #F1F8FD;
        color: #2A688E;
    }

    /* Contenedores nativos con borde elevados */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff !important;
        border: 1px solid #E4DBF4 !important;
        border-radius: 18px !important;
        padding: 12px 16px !important;
        margin-bottom: 14px !important;
        box-shadow: 0 6px 20px rgba(48, 41, 68, 0.035) !important;
    }

    .card-header {
        margin-bottom: 10px;
        padding-bottom: 8px;
        border-bottom: 1px solid #F1ECF9;
    }
    .card-title {
        font-size: 1.02rem;
        font-weight: 700;
        color: #7353A6;
        margin: 0;
    }
    .card-subtitle {
        font-size: 0.83rem;
        color: #6B6285;
        margin: 3px 0 0 0;
    }

    /* Tarjeta de antecedente previo en seguimiento */
    .antecedente-card {
        background: #F4FAFE;
        border: 1px solid #83B9DA;
        border-left: 5px solid #83B9DA;
        border-radius: 14px;
        padding: 14px 18px;
        margin-top: 10px;
        margin-bottom: 6px;
        font-size: 0.86rem;
        color: #302944;
        line-height: 1.55;
    }

    /* Tarjeta central de pregunta en Wizard */
    .question-box {
        background: #ffffff;
        border: 1px solid #B9A3DC;
        border-top: 5px solid #7353A6;
        border-radius: 20px;
        padding: 28px 32px;
        margin: 10px 0 20px 0;
        box-shadow: 0 12px 30px rgba(115, 83, 166, 0.09);
    }
    .question-meta {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 14px;
    }
    .question-badge {
        display: inline-block;
        background: #EAF4FB;
        color: #2A688E;
        border: 1px solid #83B9DA;
        font-size: 0.76rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 999px;
    }
    .question-counter {
        font-size: 0.8rem;
        font-weight: 600;
        color: #7353A6;
    }
    .question-text {
        font-size: 1.22rem;
        font-weight: 600;
        color: #302944;
        line-height: 1.55;
        margin: 0;
    }

    /* Radio buttons como tarjetas seleccionables */
    div[role="radiogroup"] {
        gap: 10px !important;
    }
    div[role="radiogroup"] label {
        background: #F7F5FC !important;
        border: 1.5px solid #E2D9F3 !important;
        border-radius: 12px !important;
        padding: 11px 16px !important;
        transition: all 0.18s ease !important;
        cursor: pointer !important;
    }
    div[role="radiogroup"] label:hover {
        border-color: #7353A6 !important;
        background: #F1ECFA !important;
    }
    div[role="radiogroup"] label:has(input:checked) {
        background: #ECE4F9 !important;
        border-color: #7353A6 !important;
        box-shadow: 0 4px 14px rgba(115, 83, 166, 0.14) !important;
    }

    /* Inputs y selectboxes */
    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div {
        background-color: #F7F5FC !important;
        border-color: #D8CCF0 !important;
        border-radius: 11px !important;
        min-height: 44px;
    }

    /* Botones */
    .stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {
        background: linear-gradient(135deg, #7353A6 0%, #8666BA 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.68rem 1.4rem !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        box-shadow: 0 6px 16px rgba(115, 83, 166, 0.22) !important;
    }
    .stButton > button:hover, .stFormSubmitButton > button:hover, .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #624491 0%, #7353A6 100%) !important;
    }

    /* Tarjetas de seccion diagnostica en reporte */
    .diag-section-card {
        background: #ffffff;
        border: 1px solid #E4DBF4;
        border-top: 4px solid #7353A6;
        border-radius: 16px;
        padding: 20px 22px;
        height: 100%;
        box-shadow: 0 6px 18px rgba(48, 41, 68, 0.04);
    }
    .diag-section-card.ansiedad {
        border-top-color: #83B9DA;
    }
    .diag-section-card.depresion {
        border-top-color: #E9A4C5;
    }
    .result-card-label {
        font-size: 0.78rem;
        font-weight: 700;
        color: #6B6285;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 6px;
    }
    .result-card-value {
        font-size: 1.28rem;
        font-weight: 700;
        color: #302944;
        margin-bottom: 8px;
    }
    .result-card-score {
        font-size: 0.83rem;
        font-weight: 600;
        color: #7353A6;
        background: #F7F5FC;
        display: inline-block;
        padding: 4px 12px;
        border-radius: 999px;
        border: 1px solid #B9A3DC;
        margin-bottom: 10px;
    }
    .result-card-desc {
        font-size: 0.84rem;
        color: #5D5475;
        line-height: 1.45;
        margin: 0;
    }

    .dictamen-box {
        background: #ffffff;
        border: 1px solid #E9A4C5;
        border-left: 6px solid #E9A4C5;
        border-radius: 16px;
        padding: 20px 24px;
        color: #302944;
        line-height: 1.65;
        box-shadow: 0 6px 18px rgba(233, 164, 197, 0.16);
    }

    .reporte-header-banner {
        background: #F7F5FC;
        border: 1px solid #B9A3DC;
        border-radius: 14px;
        padding: 16px 20px;
        margin-bottom: 16px;
    }

    .timeline-item {
        background: #ffffff;
        border: 1px solid #E4DBF4;
        border-left: 5px solid #7353A6;
        border-radius: 14px;
        padding: 14px 18px;
        margin-bottom: 10px;
        box-shadow: 0 3px 10px rgba(48, 41, 68, 0.03);
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# OPCIONES ENUM ESTANDARIZADAS
# ==========================================
OPCIONES_CONVIVENCIA = [
    "Ambos padres",
    "Madre unicamente",
    "Padre unicamente",
    "Tutores o familiares cercanos",
    "Solo / Independiente",
    "Otra situacion"
]

OPCIONES_OCUPACION = [
    "Estudia unicamente",
    "Estudia y trabaja",
    "Trabaja unicamente",
    "Sin actividad escolar o laboral"
]

OPCIONES_MEDICACION = [
    "No se medica",
    "Medicacion psiquiatrica o neurologica",
    "Otra medicacion medica",
    "No especifica / Prefiere no responder"
]

OPCIONES_SUSTANCIAS = [
    "Sin consumo reportado",
    "Tabaco o vapeo",
    "Alcohol",
    "Cannabis u otras sustancias",
    "Consumo combinado / Policonsumo",
    "Prefiere no responder"
]

# ==========================================
# BANCO DE PREGUNTAS
# ==========================================
PREGUNTAS_PSS = [
    "1. En el ultimo mes, ¿con que frecuencia te has visto afectado por algo que ocurrio de forma inesperada?",
    "2. En el ultimo mes, ¿con que frecuencia has sentido que no podias controlar las cosas importantes de tu vida?",
    "3. En el ultimo mes, ¿con que frecuencia te has sentido nervioso o con sensacion de estres?",
    "4. En el ultimo mes, ¿con que frecuencia has logrado resolver bien los pequeños problemas cotidianos que molestan?",
    "5. En el ultimo mes, ¿con que frecuencia has sentido que afrontas bien los cambios importantes en tu vida?",
    "6. En el ultimo mes, ¿con que frecuencia te has sentido seguro de poder resolver tus problemas personales?",
    "7. En el ultimo mes, ¿con que frecuencia has sentido que las cosas te estan saliendo bien?",
    "8. En el ultimo mes, ¿con que frecuencia has sentido que no podias hacer frente a todo lo que tenias pendiente?",
    "9. En el ultimo mes, ¿con que frecuencia has podido mantener bajo control las dificultades de tu vida?",
    "10. En el ultimo mes, ¿con que frecuencia has sentido que tenias la situacion bajo control?",
    "11. En el ultimo mes, ¿con que frecuencia te has molestado porque las cosas ocurrieron fuera de tu control?",
    "12. En el ultimo mes, ¿con que frecuencia te has quedado pensando en las tareas o pendientes que te faltan por hacer?",
    "13. En el ultimo mes, ¿con que frecuencia has podido decidir y organizar como pasar tu tiempo?",
    "14. En el ultimo mes, ¿con que frecuencia has sentido que los problemas se acumulan tanto que no puedes superarlos?"
]
OPCIONES_PSS = {"Nunca": 0, "Casi nunca": 1, "De vez en cuando": 2, "A menudo": 3, "Muy a menudo": 4}
ITEMS_INVERTIDOS_PSS = [3, 4, 5, 6, 8, 9, 12]

PREGUNTAS_BAI = [
    "1. Durante la ultima semana, ¿has sentido hormigueo, adormecimiento o sensacion de entumecimiento en alguna parte de tu cuerpo?",
    "2. Durante la ultima semana, ¿has sentido oleadas de calor o el cuerpo acalorado de repente?",
    "3. Durante la ultima semana, ¿has notado temblor o flojedad en las piernas al estar de pie o caminar?",
    "4. Durante la ultima semana, ¿te ha costado trabajo relajarte o descansar incluso cuando tenias tiempo libre?",
    "5. Durante la ultima semana, ¿has tenido miedo de que pase algo malo o de que ocurra lo peor?",
    "6. Durante la ultima semana, ¿has sentido mareo o la impresion de que se te va la cabeza?",
    "7. Durante la ultima semana, ¿has sentido que el corazon te late muy fuerte, rapido o con golpes notorios?",
    "8. Durante la ultima semana, ¿te has sentido inestable o con poca firmeza fisica?",
    "9. Durante la ultima semana, ¿has sentido susto intenso, temor o sensacion de alarma?",
    "10. Durante la ultima semana, ¿te has sentido nervioso o con los nervios de punta?",
    "11. Durante la ultima semana, ¿has tenido sensacion de nudo en la garganta o de estar bloqueado?",
    "12. Durante la ultima semana, ¿has notado que te tiemblan las manos?",
    "13. Durante la ultima semana, ¿te has sentido intranquilo, agitado o inseguro?",
    "14. Durante la ultima semana, ¿has tenido temor de perder el control de ti mismo o de tus actos?",
    "15. Durante la ultima semana, ¿has sentido falta de aire o sensacion de ahogo?",
    "16. Durante la ultima semana, ¿has sentido miedo a morir o a que tu salud corra peligro grave?",
    "17. Durante la ultima semana, ¿has sentido miedo o temor ante situaciones cotidianas?",
    "18. Durante la ultima semana, ¿has tenido molestias digestivas o malestar estomacal asociado a nervios?",
    "19. Durante la ultima semana, ¿has sentido que estabas a punto de desmayarte o desvanecerte?",
    "20. Durante la ultima semana, ¿has notado que se te enrojece la cara con facilidad?",
    "21. Durante la ultima semana, ¿has tenido sudoracion (fria o caliente) sin haber hecho ejercicio ni por el clima?"
]
OPCIONES_BAI = {"No en absoluto": 0, "Levemente": 1, "Moderadamente": 2, "Severamente": 3}

PREGUNTAS_BDI = [
    {"titulo": "1. Estado de animo y tristeza", "ops": [
        "0: No me siento triste la mayor parte del tiempo.",
        "1: Me siento triste o decaido buena parte del tiempo.",
        "2: Estoy triste casi todo el tiempo y me cuesta animarme.",
        "3: Estoy tan triste o infeliz que siento que ya no puedo soportarlo."
    ]},
    {"titulo": "2. Como ves tu futuro (pesimismo)", "ops": [
        "0: No me siento desanimado ni pesimista respecto a mi futuro.",
        "1: Me siento mas desanimado sobre lo que viene que antes.",
        "2: No espero que las cosas me salgan bien o mejoren.",
        "3: Siento que mi futuro no tiene esperanza y que solo ira a peor."
    ]},
    {"titulo": "3. Sensacion de haber fallado (fracaso)", "ops": [
        "0: No siento que haya fracasado en mi vida o actividades.",
        "1: Siento que he fallado mas veces de lo que deberia.",
        "2: Cuando pienso en lo que he hecho, veo muchos errores y fracasos.",
        "3: Siento que como persona soy un completo fracaso."
    ]},
    {"titulo": "4. Disfrute de tus actividades (perdida de placer)", "ops": [
        "0: Sigo disfrutando de las cosas que me gustan igual que antes.",
        "1: Ya no disfruto tanto como antes de lo que solia gustarme.",
        "2: Siento muy poco gusto o satisfaccion al hacer las cosas.",
        "3: Ya no disfruto absolutamente nada de lo que hago."
    ]},
    {"titulo": "5. Sentimientos de culpa", "ops": [
        "0: No me siento particularmente culpable por nada.",
        "1: Me siento culpable por varias cosas que hice o deje de hacer.",
        "2: Me siento culpable la mayor parte del tiempo.",
        "3: Me siento culpable todo el tiempo por casi cualquier cosa."
    ]},
    {"titulo": "6. Sensacion de estar siendo castigado", "ops": [
        "0: No siento que este recibiendo un castigo.",
        "1: Siento que tal vez podria ser castigado por algo.",
        "2: Espero o siento que merezco ser castigado.",
        "3: Siento que en este momento estoy siendo castigado."
    ]},
    {"titulo": "7. Como te sientes contigo mismo", "ops": [
        "0: Me siento igual de bien conmigo mismo que siempre.",
        "1: He perdido parte de la confianza que tenia en mi.",
        "2: Estoy decepcionado conmigo mismo por como soy o actuo.",
        "3: No me agrado ni me acepto a mi mismo."
    ]},
    {"titulo": "8. Critica hacia uno mismo (autocritica)", "ops": [
        "0: No me critico ni me culpo mas de lo normal.",
        "1: Me juzgo y me critico mas duro que antes por mis fallos.",
        "2: Me critico por cada error que cometo.",
        "3: Me culpo por todo lo malo que ocurre a mi alrededor."
    ]},
    {"titulo": "9. Pensamientos sobre hacerse daño o suicidio", "ops": [
        "0: No he tenido pensamientos de quitarme la vida.",
        "1: He tenido pensamientos de quitarme la vida, pero no lo haria.",
        "2: Me gustaria o he pensado seriamente en quitarme la vida.",
        "3: Me quitaria la vida si tuviera la oportunidad."
    ]},
    {"titulo": "10. Ganas de llorar o llanto", "ops": [
        "0: No lloro mas de lo que acostumbro.",
        "1: Lloro con mas frecuencia que antes.",
        "2: Tengo ganas de llorar o lloro por cualquier cosa.",
        "3: Antes podia llorar, pero ahora ya no puedo aunque lo necesite."
    ]},
    {"titulo": "11. Irritabilidad y mal humor", "ops": [
        "0: No me enojo ni me irrito mas de lo habitual.",
        "1: Me irrito o me molesto con mayor facilidad que antes.",
        "2: Estoy irritable o de mal humor gran parte del tiempo.",
        "3: Estoy irritable todo el tiempo y me cuesta tolerarlo."
    ]},
    {"titulo": "12. Interes por otras personas y actividades", "ops": [
        "0: No he perdido el interes por otras personas ni por mis actividades.",
        "1: Me interesa menos convivir o hacer cosas que antes.",
        "2: He perdido gran parte del interes por lo que antes me importaba.",
        "3: Ya casi nada me interesa ni me llama la atencion."
    ]},
    {"titulo": "13. Facilidad o dificultad para tomar decisiones", "ops": [
        "0: Tomo mis decisiones tan bien como siempre.",
        "1: Me cuesta un poco mas de trabajo tomar decisiones que antes.",
        "2: Tengo mucha dificultad para decidirme sobre cosas.",
        "3: Ya no puedo tomar ninguna decision por mi cuenta."
    ]},
    {"titulo": "14. Sensacion de utilidad o valia personal", "ops": [
        "0: No siento que sea inutil ni que no valga.",
        "1: No me siento tan util o valioso como solia sentirme.",
        "2: Me siento menos valioso en comparacion con los demas.",
        "3: Siento que no sirvo para nada."
    ]},
    {"titulo": "15. Nivel de energia diaria", "ops": [
        "0: Tengo tanta energia como siempre para mi dia a dia.",
        "1: Tengo menos energia que antes para hacer mis cosas.",
        "2: No tengo suficiente energia para hacer muchas actividades.",
        "3: Me siento sin energia para hacer casi nada."
    ]},
    {"titulo": "16. Cambios para dormir (patrones de sueño)", "ops": [
        "0: Duermo igual que siempre, sin cambios notables.",
        "1: Duermo un poco mas o un poco menos de lo habitual.",
        "2: Duermo mucho mas o mucho menos de lo que acostumbro.",
        "3: Duermo casi todo el dia o me cuesta muchisimo dormir."
    ]},
    {"titulo": "17. Inquietud fisica o sensacion de estar acelerado", "ops": [
        "0: No me siento mas inquieto o agitado de lo normal.",
        "1: Me siento algo mas inquieto que de costumbre.",
        "2: Estoy tan inquieto que me cuesta estar tranquilo.",
        "3: Estoy tan inquieto que necesito moverme o hacer algo sin parar."
    ]},
    {"titulo": "18. Cambios en el apetito", "ops": [
        "0: Mi apetito sigue igual que siempre.",
        "1: Tengo un poco menos o un poco mas de apetito que antes.",
        "2: Tengo mucho menos o mucho mas apetito de lo habitual.",
        "3: No tengo nada de hambre o siento ganas constantes de comer."
    ]},
    {"titulo": "19. Capacidad para concentrarte", "ops": [
        "0: Puedo concentrarme igual de bien que siempre.",
        "1: Me cuesta un poco mas concentrarme que antes.",
        "2: Me cuesta mucho mantener la atencion en algo por un rato.",
        "3: No logro concentrarme en absolutamente nada."
    ]},
    {"titulo": "20. Cansancio o agotamiento", "ops": [
        "0: No me siento mas cansado o agotado de lo habitual.",
        "1: Me canso o me agoto mas rapido que antes.",
        "2: Me siento cansado o agotado la mayor parte del tiempo.",
        "3: Estoy tan cansado que no puedo hacer la mayoria de mis actividades."
    ]},
    {"titulo": "21. Interes en temas o relaciones sexuales", "ops": [
        "0: No he notado cambios recientes en mi interes sexual.",
        "1: Tengo un poco menos de interes que antes.",
        "2: Tengo mucho menos interes que antes.",
        "3: He perdido por completo el interes."
    ]}
]

# ==========================================
# FUNCIONES DE SOPORTE
# ==========================================
def preparar_cuestionario(tests_asignados):
    lista = []
    if "PSS-14" in tests_asignados:
        for i, q in enumerate(PREGUNTAS_PSS):
            lista.append({
                "seccion_corta": "Seccion I: Estres (PSS-14)",
                "test": "Seccion I · Escala de Estres Percibido (PSS-14)",
                "id_orig": i,
                "total_sec": len(PREGUNTAS_PSS),
                "texto": q,
                "tipo": "PSS"
            })
    if "BAI" in tests_asignados:
        for i, q in enumerate(PREGUNTAS_BAI):
            lista.append({
                "seccion_corta": "Seccion II: Ansiedad (BAI)",
                "test": "Seccion II · Inventario de Ansiedad (BAI)",
                "id_orig": i,
                "total_sec": len(PREGUNTAS_BAI),
                "texto": q,
                "tipo": "BAI"
            })
    if "BDI-II" in tests_asignados:
        for i, q in enumerate(PREGUNTAS_BDI):
            lista.append({
                "seccion_corta": "Seccion III: Depresion (BDI-II)",
                "test": "Seccion III · Inventario de Depresion (BDI-II)",
                "id_orig": i,
                "total_sec": len(PREGUNTAS_BDI),
                "texto": q["titulo"],
                "ops": q["ops"],
                "tipo": "BDI"
            })
    return lista

def calcular_resultados_finales():
    score_pss, score_bai, score_bdi = 0, 0, 0
    for i, p in enumerate(st.session_state.wizard_data):
        resp = st.session_state.respuestas_wizard.get(i)
        if resp is None:
            continue
        if p['tipo'] == "PSS":
            valor = OPCIONES_PSS[resp]
            if p['id_orig'] in ITEMS_INVERTIDOS_PSS:
                valor = 4 - valor
            score_pss += valor
        elif p['tipo'] == "BAI":
            score_bai += OPCIONES_BAI[resp]
        elif p['tipo'] == "BDI":
            valor = int(resp.split(":")[0])
            score_bdi += valor
            
    tests = st.session_state.tests_seleccionados
    st.session_state.score_pss = score_pss if "PSS-14" in tests else -1
    st.session_state.score_bai = score_bai if "BAI" in tests else -1
    st.session_state.score_bdi = score_bdi if "BDI-II" in tests else -1

def iniciar_seguimiento_desde_historial(paciente_nombre):
    """Prepara el estado de sesion para dar seguimiento a un adolescente ya registrado."""
    st.session_state.paso_actual = 1
    st.session_state.modo_registro_init = "Seguimiento a Paciente Existente"
    st.session_state.paciente_seguimiento_pre = paciente_nombre
    st.session_state.nav_radio = "Evaluacion Clinica"

def renderizar_cabecera(etiqueta_modo, es_seguimiento=False):
    clase_pill = "app-pill seguimiento" if es_seguimiento else "app-pill"
    st.markdown(f"""
        <div class="app-header">
            <div class="app-brand">
                {obtener_logo_html(46)}
                <div>
                    <p class="app-title">SE-TEA · Valoracion Emocional en Adolescentes</p>
                    <p class="app-subtitle">Sistema Experto de Tamizaje Psicometrico y Seguimiento Clinico</p>
                </div>
            </div>
            <div class="{clase_pill}">{etiqueta_modo}</div>
        </div>
    """, unsafe_allow_html=True)

def renderizar_stepper(paso):
    pasos = [
        (1, "Perfil y Filtro Inicial"),
        (2, "Secciones de Evaluacion"),
        (3, "Diagnostico y Reporte PDF")
    ]
    html = '<div class="stepper">'
    for num, titulo in pasos:
        clase = "active" if num == paso else ("done" if num < paso else "")
        html += f'<div class="step-item {clase}"><span class="step-num">{num}</span><span>{titulo}</span></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

def renderizar_tarjetas_secciones_diagnostico(reg_dict, anterior_dict=None):
    """Renderiza el diagnostico dividido por secciones clinicas y compara con sesion previa si existe."""
    c1, c2, c3 = st.columns(3)

    score_pss = reg_dict.get("score_pss", -1)
    score_bai = reg_dict.get("score_bai", -1)
    score_bdi = reg_dict.get("score_bdi", -1)

    def _comp_txt(actual, clave_prev):
        if not anterior_dict or actual == -1:
            return ""
        prev = anterior_dict.get(clave_prev, -1)
        if prev is None or prev == -1:
            return ""
        diff = actual - prev
        if diff < 0:
            return f"  |  <span style='color:#2A688E;'>{diff} pts vs sesion previa</span>"
        elif diff > 0:
            return f"  |  <span style='color:#B03A6F;'>+{diff} pts vs sesion previa</span>"
        return "  |  Sin cambio vs sesion previa"

    with c1:
        st.markdown(f"""
            <div class="diag-section-card">
                <div class="result-card-label">Seccion I · Estres Percibido (PSS-14)</div>
                <div class="result-card-value">{reg_dict.get('diag_pss', 'No evaluado')}</div>
                <div class="result-card-score">{f'{score_pss} / 56 pts' if score_pss != -1 else 'No aplicada'}{_comp_txt(score_pss, 'score_pss')}</div>
                <p class="result-card-desc">Valoracion de sobrecarga cotidiana y capacidad de afrontamiento en el ultimo mes.</p>
            </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
            <div class="diag-section-card ansiedad">
                <div class="result-card-label">Seccion II · Ansiedad (BAI)</div>
                <div class="result-card-value">{reg_dict.get('diag_bai', 'No evaluado')}</div>
                <div class="result-card-score">{f'{score_bai} / 63 pts' if score_bai != -1 else 'No aplicada'}{_comp_txt(score_bai, 'score_bai')}</div>
                <p class="result-card-desc">Presencia e intensidad de sintomas somaticos y cognitivos de ansiedad en la ultima semana.</p>
            </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
            <div class="diag-section-card depresion">
                <div class="result-card-label">Seccion III · Depresion (BDI-II)</div>
                <div class="result-card-value">{reg_dict.get('diag_bdi', 'No evaluado')}</div>
                <div class="result-card-score">{f'{score_bdi} / 63 pts' if score_bdi != -1 else 'No aplicada'}{_comp_txt(score_bdi, 'score_bdi')}</div>
                <p class="result-card-desc">Indicadores de estado de animo, energia, motivacion y bienestar emocional.</p>
            </div>
        """, unsafe_allow_html=True)

# ==========================================
# NAVEGACION PRINCIPAL
# ==========================================
def main():
    if 'paso_actual' not in st.session_state:
        st.session_state.paso_actual = 1
        st.session_state.tests_seleccionados = []
    if 'nav_radio' not in st.session_state:
        st.session_state.nav_radio = "Evaluacion Clinica"

    with st.sidebar:
        st.markdown(f"""
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:18px; padding-bottom:14px; border-bottom:1px solid #EDE7F8;">
                {obtener_logo_html(40)}
                <div>
                    <div style="font-weight:700; color:#302944; font-size:1.05rem;">SE-TEA</div>
                    <div style="font-size:0.76rem; color:#6B6285;">Sistema Experto Clinico</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        modo = st.radio(
            "Navegacion",
            ["Evaluacion Clinica", "Historial y Reportes"],
            key="nav_radio",
            label_visibility="collapsed"
        )

        if modo == "Evaluacion Clinica":
            st.markdown("---")
            st.caption(f"Etapa actual: {st.session_state.paso_actual} de 3")
            st.progress(st.session_state.paso_actual / 3)
            if st.session_state.get("es_seguimiento"):
                st.info(f"Seguimiento activo:\n**{st.session_state.get('nombre', '')}**")
            if st.session_state.get("tests_seleccionados"):
                st.caption("Secciones asignadas:")
                nombres_sec = {
                    "PSS-14": "Seccion I: Estres (PSS-14)",
                    "BAI": "Seccion II: Ansiedad (BAI)",
                    "BDI-II": "Seccion III: Depresion (BDI-II)"
                }
                for t in st.session_state.tests_seleccionados:
                    st.markdown(f"- **{nombres_sec.get(t, t)}**")

    if modo == "Evaluacion Clinica":
        es_seg = st.session_state.get("es_seguimiento", False)
        etiqueta = f"Seguimiento · Etapa {st.session_state.paso_actual}/3" if es_seg else f"Evaluacion · Etapa {st.session_state.paso_actual}/3"
        renderizar_cabecera(etiqueta, es_seguimiento=es_seg)
        renderizar_stepper(st.session_state.paso_actual)

        if st.session_state.paso_actual == 1:
            pantalla_configuracion()
        elif st.session_state.paso_actual == 2:
            pantalla_evaluacion()
        elif st.session_state.paso_actual == 3:
            pantalla_resultados()
            
    elif modo == "Historial y Reportes":
        renderizar_cabecera("Historial Clinico & Seguimiento")
        pantalla_historial()

def pantalla_configuracion():
    registros_db = obtener_historial_pacientes()
    df_db = pd.DataFrame(registros_db) if registros_db else pd.DataFrame()
    pacientes_unicos = sorted(df_db["identificador"].dropna().unique().tolist()) if not df_db.empty else []

    opciones_tipo = ["Nuevo Paciente", "Seguimiento a Paciente Existente"]
    default_tipo_idx = 0
    if st.session_state.get("modo_registro_init") == "Seguimiento a Paciente Existente" and pacientes_unicos:
        default_tipo_idx = 1

    with st.container(border=True):
        st.markdown("""
            <div class="card-header">
                <p class="card-title">Modalidad de Atencion Clinica</p>
                <p class="card-subtitle">Elige si registras un adolescente por primera vez o si daras continuidad a un expediente existente.</p>
            </div>
        """, unsafe_allow_html=True)

        tipo_atencion = st.radio(
            "Tipo de sesion:",
            opciones_tipo,
            index=default_tipo_idx,
            horizontal=True,
            label_visibility="collapsed"
        )

        registro_previo = None
        num_sesiones_previas = 0

        if tipo_atencion == "Seguimiento a Paciente Existente":
            if not pacientes_unicos:
                st.warning("Aun no existen adolescentes registrados en la base de datos. Selecciona 'Nuevo Paciente'.")
            else:
                pre_pac = st.session_state.get("paciente_seguimiento_pre", pacientes_unicos[0])
                idx_pac = pacientes_unicos.index(pre_pac) if pre_pac in pacientes_unicos else 0
                paciente_sel = st.selectbox(
                    "Selecciona el adolescente registrado en MariaDB:",
                    pacientes_unicos,
                    index=idx_pac
                )
                hist_pac = df_db[df_db["identificador"] == paciente_sel].sort_values(by="id", ascending=False)
                num_sesiones_previas = len(hist_pac)
                registro_previo = hist_pac.iloc[0].to_dict()

                s_pss = f"{registro_previo['score_pss']}/56" if registro_previo['score_pss'] != -1 else "N/A"
                s_bai = f"{registro_previo['score_bai']}/63" if registro_previo['score_bai'] != -1 else "N/A"
                s_bdi = f"{registro_previo['score_bdi']}/63" if registro_previo['score_bdi'] != -1 else "N/A"

                st.markdown(f"""
                    <div class="antecedente-card">
                        <strong>Expediente localizado ({num_sesiones_previas} {'sesion previa' if num_sesiones_previas == 1 else 'sesiones previas'}):</strong>
                        Ultima valoracion el <strong>{str(registro_previo['fecha_evaluacion'])[:16]}</strong> (Folio #{registro_previo['id']}).<br>
                        <strong>Resultados previos:</strong> Estres: <em>{registro_previo['diag_pss']}</em> ({s_pss})  · 
                        Ansiedad: <em>{registro_previo['diag_bai']}</em> ({s_bai})  · 
                        Depresion: <em>{registro_previo['diag_bdi']}</em> ({s_bdi})
                    </div>
                """, unsafe_allow_html=True)

    # Valores precargados si es seguimiento
    def_nombre = registro_previo["identificador"] if registro_previo else ""
    def_edad = int(registro_previo["edad"]) if registro_previo and 10 <= int(registro_previo["edad"]) <= 19 else 15
    def_conv = OPCIONES_CONVIVENCIA.index(registro_previo["convivencia_familiar"]) if (registro_previo and registro_previo["convivencia_familiar"] in OPCIONES_CONVIVENCIA) else 0
    def_ocup = OPCIONES_OCUPACION.index(registro_previo["ocupacion"]) if (registro_previo and registro_previo["ocupacion"] in OPCIONES_OCUPACION) else 0
    def_med = OPCIONES_MEDICACION.index(registro_previo["estado_medicacion"]) if (registro_previo and registro_previo["estado_medicacion"] in OPCIONES_MEDICACION) else 0
    def_det_med = "" if (not registro_previo or registro_previo["detalle_medicacion"] == "Sin detalle adicional") else registro_previo["detalle_medicacion"]
    def_sust = OPCIONES_SUSTANCIAS.index(registro_previo["consumo_sustancias"]) if (registro_previo and registro_previo["consumo_sustancias"] in OPCIONES_SUSTANCIAS) else 0
    def_det_sust = "" if (not registro_previo or registro_previo["detalle_sustancias"] == "Sin detalle adicional") else registro_previo["detalle_sustancias"]

    with st.form("form_registro"):
        with st.container(border=True):
            st.markdown("""
                <div class="card-header">
                    <p class="card-title">1. Datos Personales y Entorno del Adolescente</p>
                    <p class="card-subtitle">Verifica o actualiza los datos actuales para esta sesion.</p>
                </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns([2.2, 1])
            nombre = c1.text_input(
                "Nombre completo del adolescente",
                value=def_nombre,
                placeholder="Ej. Sofia Martinez Lopez",
                disabled=(registro_previo is not None)
            )
            edad = c2.number_input("Edad (años)", min_value=10, max_value=19, value=def_edad, step=1)

            c3, c4 = st.columns(2)
            convivencia = c3.selectbox("¿Con quien vive habitualmente?", OPCIONES_CONVIVENCIA, index=def_conv)
            ocupacion = c4.selectbox("Actividad principal actual", OPCIONES_OCUPACION, index=def_ocup)

        with st.container(border=True):
            st.markdown("""
                <div class="card-header">
                    <p class="card-title">2. Antecedentes Farmacologicos y Consumo</p>
                    <p class="card-subtitle">Actualiza si hubo cambios en medicacion o consumo desde la ultima consulta.</p>
                </div>
            """, unsafe_allow_html=True)

            m1, m2 = st.columns(2)
            estado_medicacion = m1.selectbox("Medicacion actual", OPCIONES_MEDICACION, index=def_med)
            detalle_medicacion = m2.text_input("Farmaco y dosis (opcional)", value=def_det_med, placeholder="Ej. Sertralina 50 mg cada 24 h")

            s1, s2 = st.columns(2)
            consumo_sustancias = s1.selectbox("Consumo de sustancias", OPCIONES_SUSTANCIAS, index=def_sust)
            detalle_sustancias = s2.text_input("Frecuencia o precision (opcional)", value=def_det_sust, placeholder="Ej. Ocasional en fines de semana")

        with st.container(border=True):
            st.markdown("""
                <div class="card-header">
                    <p class="card-title">3. Filtro por Secciones de Diagnostico</p>
                    <p class="card-subtitle">Selecciona las secciones clinicas a evaluar en esta sesion.</p>
                </div>
            """, unsafe_allow_html=True)

            idx_pss = 1 if (registro_previo and registro_previo.get("score_pss", -1) != -1) else 0
            idx_bai = 1 if (registro_previo and registro_previo.get("score_bai", -1) != -1) else 0
            idx_bdi = 1 if (registro_previo and registro_previo.get("score_bdi", -1) != -1) else 0

            f_pss = st.radio(
                "Seccion I (Estres): En las ultimas semanas, ¿has sentido que tus pendientes, tareas o presiones diarias te superan o te cuesta organizarlas?",
                ["No", "Si"], index=idx_pss, horizontal=True
            )
            f_bai = st.radio(
                "Seccion II (Ansiedad): ¿Has notado reacciones fisicas repentinas como nerviosismo intenso, palpitaciones, falta de aire o tension sin motivo fisico claro?",
                ["No", "Si"], index=idx_bai, horizontal=True
            )
            f_bdi = st.radio(
                "Seccion III (Depresion): ¿Has sentido decaimiento persistente, falta de energia o dificultad para disfrutar las cosas que antes te gustaban?",
                ["No", "Si"], index=idx_bdi, horizontal=True
            )

        st.markdown("<br>", unsafe_allow_html=True)
        _, col_btn = st.columns([2.2, 1])
        with col_btn:
            texto_inicio = "Iniciar Sesion de Seguimiento" if registro_previo else "Comenzar Evaluacion"
            submit = st.form_submit_button(texto_inicio, use_container_width=True)
        
        if submit:
            nombre_final = def_nombre if registro_previo else nombre.strip()
            if not nombre_final:
                st.error("Por favor ingresa el nombre completo del adolescente.")
            else:
                st.session_state.nombre = nombre_final
                st.session_state.edad = edad
                st.session_state.convivencia = convivencia
                st.session_state.ocupacion = ocupacion
                st.session_state.estado_medicacion = estado_medicacion
                st.session_state.detalle_medicacion = detalle_medicacion.strip() if detalle_medicacion.strip() else "Sin detalle adicional"
                st.session_state.consumo_sustancias = consumo_sustancias
                st.session_state.detalle_sustancias = detalle_sustancias.strip() if detalle_sustancias.strip() else "Sin detalle adicional"
                st.session_state.es_seguimiento = (registro_previo is not None)
                st.session_state.registro_previo = registro_previo
                st.session_state.sesion_numero = num_sesiones_previas + 1
                
                tests = []
                if f_pss == "Si":
                    tests.append("PSS-14")
                if f_bai == "Si":
                    tests.append("BAI")
                if f_bdi == "Si":
                    tests.append("BDI-II")
                if not tests:
                    tests.append("PSS-14")
                
                st.session_state.tests_seleccionados = tests
                st.session_state.wizard_data = preparar_cuestionario(tests)
                st.session_state.wizard_idx = 0
                st.session_state.respuestas_wizard = {}
                st.session_state.paso_actual = 2
                st.rerun()

def pantalla_evaluacion():
    idx = st.session_state.wizard_idx
    datos = st.session_state.wizard_data
    total = len(datos)
    pregunta_actual = datos[idx]

    orden_tests = ["PSS-14", "BAI", "BDI-II"]
    etiquetas_sec = {
        "PSS-14": "Seccion I · Estres (PSS-14)",
        "BAI": "Seccion II · Ansiedad (BAI)",
        "BDI-II": "Seccion III · Depresion (BDI-II)"
    }
    tipo_actual_map = {"PSS": "PSS-14", "BAI": "BAI", "BDI": "BDI-II"}
    test_en_curso = tipo_actual_map[pregunta_actual["tipo"]]

    asignados = st.session_state.tests_seleccionados
    idx_test_curso = asignados.index(test_en_curso)

    barra_html = '<div class="diag-sections-bar">'
    for t in orden_tests:
        if t not in asignados:
            barra_html += f'<div class="diag-sec-pill" style="opacity:0.45;">{etiquetas_sec[t]} (Omitida)</div>'
        else:
            pos = asignados.index(t)
            if pos < idx_test_curso:
                barra_html += f'<div class="diag-sec-pill completed">✓ {etiquetas_sec[t]}</div>'
            elif pos == idx_test_curso:
                barra_html += f'<div class="diag-sec-pill current">● {etiquetas_sec[t]} (En curso)</div>'
            else:
                barra_html += f'<div class="diag-sec-pill">{etiquetas_sec[t]} (Pendiente)</div>'
    barra_html += '</div>'
    st.markdown(barra_html, unsafe_allow_html=True)

    col_izq, col_centro, col_der = st.columns([0.6, 4.8, 0.6])
    with col_centro:
        st.progress(
            (idx + 1) / total,
            text=f"Avance total: {idx + 1} de {total} | Item {pregunta_actual['id_orig'] + 1} de {pregunta_actual['total_sec']} en esta seccion"
        )

        st.markdown(f"""
            <div class="question-box">
                <div class="question-meta">
                    <span class="question-badge">{pregunta_actual['test']}</span>
                    <span class="question-counter">Item {pregunta_actual['id_orig'] + 1} / {pregunta_actual['total_sec']}</span>
                </div>
                <p class="question-text">{pregunta_actual['texto']}</p>
            </div>
        """, unsafe_allow_html=True)

        tipo = pregunta_actual['tipo']
        if tipo == "PSS":
            opciones = list(OPCIONES_PSS.keys())
        elif tipo == "BAI":
            opciones = list(OPCIONES_BAI.keys())
        elif tipo == "BDI":
            opciones = pregunta_actual["ops"]

        resp_previa = st.session_state.respuestas_wizard.get(idx, None)
        index_previa = opciones.index(resp_previa) if (resp_previa in opciones) else 0

        respuesta = st.radio(
            "Selecciona una opcion:",
            options=opciones,
            index=index_previa,
            label_visibility="collapsed"
        )

        st.markdown("<br>", unsafe_allow_html=True)
        b_prev, _, b_next = st.columns([1, 1.6, 1])

        with b_prev:
            if idx > 0:
                if st.button("Anterior", use_container_width=True):
                    st.session_state.respuestas_wizard[idx] = respuesta
                    st.session_state.wizard_idx -= 1
                    st.rerun()

        with b_next:
            es_ultimo = (idx == total - 1)
            texto_btn = "Generar Diagnostico" if es_ultimo else "Siguiente"
            if st.button(texto_btn, use_container_width=True):
                st.session_state.respuestas_wizard[idx] = respuesta
                if not es_ultimo:
                    st.session_state.wizard_idx += 1
                    st.rerun()
                else:
                    calcular_resultados_finales()
                    st.session_state.paso_actual = 3
                    st.rerun()

def pantalla_resultados():
    motor = MotorInferencia()
    resultados = motor.ejecutar_inferencia(st.session_state.score_bdi, st.session_state.score_bai, st.session_state.score_pss)
    diags = resultados["diagnosticos"]

    es_seg = st.session_state.get("es_seguimiento", False)
    reg_previo = st.session_state.get("registro_previo", None)
    etiqueta_sesion = f" · Sesion #{st.session_state.get('sesion_numero', 1)} (Seguimiento)" if es_seg else " · Valoracion Inicial"

    with st.container(border=True):
        st.markdown(f"""
            <div class="card-header" style="margin-bottom:4px; border-bottom:none; padding-bottom:0;">
                <p class="card-title">Reporte de Valoracion: {st.session_state.nombre} ({st.session_state.edad} años){etiqueta_sesion}</p>
                <p class="card-subtitle">
                    <strong>Convivencia:</strong> {st.session_state.convivencia}  · 
                    <strong>Actividad:</strong> {st.session_state.ocupacion}  · 
                    <strong>Medicacion:</strong> {st.session_state.estado_medicacion} ({st.session_state.detalle_medicacion})  · 
                    <strong>Sustancias:</strong> {st.session_state.consumo_sustancias} ({st.session_state.detalle_sustancias})
                </p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("#### Resultados por Seccion de Diagnostico")
    datos_reporte_actual = {
        "id": f"SESION-{st.session_state.get('sesion_numero', 1)}",
        "identificador": st.session_state.nombre,
        "edad": st.session_state.edad,
        "convivencia_familiar": st.session_state.convivencia,
        "ocupacion": st.session_state.ocupacion,
        "estado_medicacion": st.session_state.estado_medicacion,
        "detalle_medicacion": st.session_state.detalle_medicacion,
        "consumo_sustancias": st.session_state.consumo_sustancias,
        "detalle_sustancias": st.session_state.detalle_sustancias,
        "score_pss": st.session_state.score_pss,
        "score_bai": st.session_state.score_bai,
        "score_bdi": st.session_state.score_bdi,
        "diag_pss": diags["Estres (PSS-14)"],
        "diag_bai": diags["Ansiedad (BAI)"],
        "diag_bdi": diags["Depresion (BDI-II)"],
        "comorbilidad": resultados["comorbilidad"]
    }
    renderizar_tarjetas_secciones_diagnostico(datos_reporte_actual, anterior_dict=reg_previo)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Seccion IV · Dictamen Clinico Integrado y Comorbilidad")
    dictamen_html = str(resultados["comorbilidad"]).replace("\n\n", "<br><br>")
    st.markdown(f'<div class="dictamen-box">{dictamen_html}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_guardar, col_pdf, col_reiniciar = st.columns(3)
    with col_guardar:
        if st.button("Guardar en Base de Datos", use_container_width=True):
            exito = guardar_resultado_paciente(
                st.session_state.nombre, st.session_state.edad,
                st.session_state.convivencia, st.session_state.ocupacion,
                st.session_state.estado_medicacion, st.session_state.detalle_medicacion,
                st.session_state.consumo_sustancias, st.session_state.detalle_sustancias,
                st.session_state.score_bdi, st.session_state.score_bai, st.session_state.score_pss,
                diags["Depresion (BDI-II)"], diags["Ansiedad (BAI)"], diags["Estres (PSS-14)"], resultados["comorbilidad"]
            )
            if exito:
                st.success("Sesion guardada en el historial clinico.")

    with col_pdf:
        pdf_bytes = generar_pdf_expediente(datos_reporte_actual)
        nombre_archivo_pdf = f"Reporte_{st.session_state.nombre.replace(' ', '_')}.pdf"
        st.download_button(
            "Descargar Reporte en PDF",
            data=pdf_bytes,
            file_name=nombre_archivo_pdf,
            mime="application/pdf",
            use_container_width=True
        )
            
    with col_reiniciar:
        if st.button("Nueva Evaluacion", use_container_width=True):
            for k in list(st.session_state.keys()):
                if k != "nav_radio":
                    del st.session_state[k]
            st.session_state.paso_actual = 1
            st.rerun()

def pantalla_historial():
    datos = obtener_historial_pacientes()
    if not datos:
        st.info("No hay registros almacenados en el sistema.")
        return

    df = pd.DataFrame(datos)

    total_sesiones = len(df)
    total_adolescentes = df["identificador"].nunique()
    casos_alerta = df["comorbilidad"].fillna("").apply(
        lambda x: any(etiqueta in x for etiqueta in ["COMORBILIDAD CRITICA", "RIESGO ELEVADO", "ALERTA PREVENTIVA"])
    ).sum()
    casos_sustancias = df["consumo_sustancias"].fillna("").apply(
        lambda x: x not in ["Sin consumo reportado", "Prefiere no responder", ""]
    ).sum()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Adolescentes Unicos", total_adolescentes)
    m2.metric("Sesiones Registradas", total_sesiones)
    m3.metric("Sesiones con Alerta", int(casos_alerta))
    m4.metric("Consumo Reportado", int(casos_sustancias))

    st.markdown("<br>", unsafe_allow_html=True)

    f_col1, f_col2, f_col3 = st.columns([2, 1, 1])
    busqueda = f_col1.text_input("Buscar por nombre completo:", placeholder="Escribe el nombre del adolescente...")
    filtro_riesgo = f_col2.selectbox("Condicion clinica:", ["Todos", "Solo alertas / comorbilidad", "Con consumo de sustancias"])
    filtro_sustancia = f_col3.selectbox("Sustancia:", ["Todas"] + OPCIONES_SUSTANCIAS)

    df_filtrado = df.copy()
    if busqueda.strip():
        df_filtrado = df_filtrado[df_filtrado["identificador"].str.contains(busqueda.strip(), case=False, na=False)]
    if filtro_riesgo == "Solo alertas / comorbilidad":
        df_filtrado = df_filtrado[df_filtrado["comorbilidad"].fillna("").apply(
            lambda x: any(etiqueta in x for etiqueta in ["COMORBILIDAD CRITICA", "RIESGO ELEVADO", "ALERTA PREVENTIVA"])
        )]
    elif filtro_riesgo == "Con consumo de sustancias":
        df_filtrado = df_filtrado[~df_filtrado["consumo_sustancias"].isin(["Sin consumo reportado", "Prefiere no responder"])]
    if filtro_sustancia != "Todas":
        df_filtrado = df_filtrado[df_filtrado["consumo_sustancias"] == filtro_sustancia]

    if df_filtrado.empty:
        st.warning("No se encontraron expedientes con esos criterios.")
        return

    tab_seguimiento, tab_reporte_ind, tab_tabla_general = st.tabs([
        "Evolucion y Seguimiento por Adolescente",
        "Reporte Individual por Folio (PDF)",
        "Tabla Consolidada de Historial"
    ])

    # ------------------------------------------
    # PESTAÑA 1: SEGUIMIENTO LONGITUDINAL
    # ------------------------------------------
    with tab_seguimiento:
        lista_pacientes = sorted(df_filtrado["identificador"].dropna().unique().tolist())
        pac_elegido = st.selectbox(
            "Selecciona un adolescente para revisar su evolucion y darle seguimiento:",
            lista_pacientes
        )

        df_pac = df[df["identificador"] == pac_elegido].sort_values(by="id", ascending=True).reset_index(drop=True)
        ultima_sesion = df_pac.iloc[-1].to_dict()

        col_info_p, col_btn_seg = st.columns([2.4, 1])
        with col_info_p:
            st.markdown(f"""
                <div class="reporte-header-banner" style="margin-bottom:0;">
                    <div style="font-size:1.12rem; font-weight:700; color:#7353A6;">
                        Expediente Longitudinal · {pac_elegido}
                    </div>
                    <div style="font-size:0.85rem; color:#302944; margin-top:4px;">
                        <strong>Edad actual:</strong> {ultima_sesion['edad']} años  | 
                        <strong>Total de evaluaciones:</strong> {len(df_pac)}  | 
                        <strong>Ultima consulta:</strong> {str(ultima_sesion['fecha_evaluacion'])[:16]}
                    </div>
                </div>
            """, unsafe_allow_html=True)

        with col_btn_seg:
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            st.button(
                "Iniciar Nueva Sesion de Seguimiento",
                key=f"btn_seg_{pac_elegido}",
                on_click=iniciar_seguimiento_desde_historial,
                args=(pac_elegido,),
                use_container_width=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        if len(df_pac) >= 2:
            st.markdown("##### Evolucion de Puntajes Psicometricos por Sesion")
            df_chart = pd.DataFrame({
                "Sesion": [f"Sesion {i+1} ({str(r['fecha_evaluacion'])[:10]})" for i, r in df_pac.iterrows()],
                "Estres (PSS-14)": [r["score_pss"] if r["score_pss"] != -1 else None for _, r in df_pac.iterrows()],
                "Ansiedad (BAI)": [r["score_bai"] if r["score_bai"] != -1 else None for _, r in df_pac.iterrows()],
                "Depresion (BDI-II)": [r["score_bdi"] if r["score_bdi"] != -1 else None for _, r in df_pac.iterrows()]
            }).set_index("Sesion")
            st.line_chart(df_chart, color=["#7353A6", "#83B9DA", "#E9A4C5"])
        else:
            st.info("Este adolescente cuenta con 1 evaluacion registrada. Al aplicar una sesion de seguimiento se mostrara la grafica comparativa de evolucion.")

        st.markdown("##### Linea de Tiempo de Sesiones Clinicas")
        for idx_s, row_s in df_pac.iloc[::-1].iterrows():
            num_s = idx_s + 1
            s_pss = f"{row_s['score_pss']}/56" if row_s['score_pss'] != -1 else "No aplicada"
            s_bai = f"{row_s['score_bai']}/63" if row_s['score_bai'] != -1 else "No aplicada"
            s_bdi = f"{row_s['score_bdi']}/63" if row_s['score_bdi'] != -1 else "No aplicada"
            st.markdown(f"""
                <div class="timeline-item">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                        <strong style="color:#7353A6;">Sesion #{num_s} · Folio #{row_s['id']}</strong>
                        <span style="font-size:0.8rem; color:#6B6285;">{row_s['fecha_evaluacion']}</span>
                    </div>
                    <div style="font-size:0.86rem; color:#302944; margin-bottom:6px;">
                        <strong>Seccion I (Estres):</strong> {row_s['diag_pss']} ({s_pss})  | 
                        <strong>Seccion II (Ansiedad):</strong> {row_s['diag_bai']} ({s_bai})  | 
                        <strong>Seccion III (Depresion):</strong> {row_s['diag_bdi']} ({s_bdi})
                    </div>
                    <div style="font-size:0.82rem; color:#5D5475;">
                        <strong>Dictamen:</strong> {str(row_s['comorbilidad']).splitlines()[0]}
                    </div>
                </div>
            """, unsafe_allow_html=True)

    # ------------------------------------------
    # PESTAÑA 2: REPORTE INDIVIDUAL POR FOLIO
    # ------------------------------------------
    with tab_reporte_ind:
        opciones_expediente = [
            f"Folio #{row['id']} — {row['identificador']} ({row['edad']} años) | {str(row['fecha_evaluacion'])[:10]}"
            for _, row in df_filtrado.iterrows()
        ]
        seleccion = st.selectbox("Selecciona el folio para visualizar su reporte clinico:", opciones_expediente)
        indice_sel = opciones_expediente.index(seleccion)
        reg = df_filtrado.iloc[indice_sel].to_dict()

        with st.container(border=True):
            st.markdown(f"""
                <div class="reporte-header-banner">
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                        <div>
                            <div style="font-size:1.12rem; font-weight:700; color:#7353A6;">
                                Reporte Clinico · Folio #{reg['id']} — {reg['identificador']}
                            </div>
                            <div style="font-size:0.84rem; color:#6B6285; margin-top:3px;">
                                <strong>Edad:</strong> {reg['edad']} años  | 
                                <strong>Fecha de evaluacion:</strong> {reg['fecha_evaluacion']}
                            </div>
                        </div>
                        <span class="app-pill">Expediente Verificado</span>
                    </div>
                    <hr style="border:none; border-top:1px solid #E4DBF4; margin:10px 0;">
                    <div style="font-size:0.86rem; color:#302944; line-height:1.6;">
                        <strong>Convivencia familiar:</strong> {reg['convivencia_familiar']}  · 
                        <strong>Ocupacion:</strong> {reg['ocupacion']}<br>
                        <strong>Medicacion:</strong> {reg['estado_medicacion']} (<em>{reg['detalle_medicacion']}</em>)  · 
                        <strong>Sustancias:</strong> {reg['consumo_sustancias']} (<em>{reg['detalle_sustancias']}</em>)
                    </div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("##### Diagnostico Desglosado por Secciones")
            renderizar_tarjetas_secciones_diagnostico(reg)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("##### Dictamen Integrado y Comorbilidad")
            dictamen_reg = str(reg.get("comorbilidad", "")).replace("\n\n", "<br><br>")
            st.markdown(f'<div class="dictamen-box">{dictamen_reg}</div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            sesiones_mismo_paciente = df[df["identificador"] == reg["identificador"]].sort_values(by="id", ascending=True)
            total_sesiones_pac = len(sesiones_mismo_paciente)

            pdf_ind = generar_pdf_expediente(reg)
            nombre_pdf_ind = f"Reporte_Folio_{reg['id']}_{str(reg['identificador']).replace(' ', '_')}.pdf"

            if total_sesiones_pac > 1:
                st.info(
                    f"Este adolescente cuenta con **{total_sesiones_pac} sesiones registradas** en el historial. "
                    "Puedes descargar unicamente este folio o su expediente completo con todas las sesiones."
                )
                c_btn_folio, c_btn_todas = st.columns(2)
                with c_btn_folio:
                    st.download_button(
                        f"Descargar Solo Este Folio (#{reg['id']}) en PDF",
                        data=pdf_ind,
                        file_name=nombre_pdf_ind,
                        mime="application/pdf",
                        use_container_width=True
                    )
                with c_btn_todas:
                    pdf_todas = generar_pdf_expediente_completo(sesiones_mismo_paciente.to_dict(orient="records"))
                    nombre_pdf_todas = f"Expediente_Completo_{str(reg['identificador']).replace(' ', '_')}_{total_sesiones_pac}_Sesiones.pdf"
                    st.download_button(
                        f"Descargar Todas las Sesiones ({total_sesiones_pac}) en un PDF",
                        data=pdf_todas,
                        file_name=nombre_pdf_todas,
                        mime="application/pdf",
                        use_container_width=True
                    )
            else:
                st.download_button(
                    "Descargar Reporte Individual en PDF",
                    data=pdf_ind,
                    file_name=nombre_pdf_ind,
                    mime="application/pdf",
                    use_container_width=True
                )

    # ------------------------------------------
    # PESTAÑA 3: TABLA CONSOLIDADA
    # ------------------------------------------
    with tab_tabla_general:
        df_vista = df_filtrado.rename(columns={
            "id": "Folio",
            "fecha_evaluacion": "Fecha",
            "identificador": "Nombre completo",
            "edad": "Edad",
            "convivencia_familiar": "Convivencia",
            "ocupacion": "Ocupacion",
            "estado_medicacion": "Medicacion",
            "consumo_sustancias": "Sustancias",
            "diag_pss": "Seccion I: Estres",
            "diag_bai": "Seccion II: Ansiedad",
            "diag_bdi": "Seccion III: Depresion"
        })

        columnas_visibles = [
            "Folio", "Fecha", "Nombre completo", "Edad",
            "Seccion I: Estres", "Seccion II: Ansiedad", "Seccion III: Depresion",
            "Medicacion", "Sustancias"
        ]
        st.dataframe(df_vista[columnas_visibles], use_container_width=True, hide_index=True)

        st.markdown("<br>", unsafe_allow_html=True)
        c_pdf_all, c_csv_all = st.columns(2)
        with c_pdf_all:
            pdf_consolidado = generar_pdf_historial_general(df_filtrado.to_dict(orient="records"))
            st.download_button(
                "Descargar Reporte Consolidado del Historial (PDF)",
                data=pdf_consolidado,
                file_name="Historial_Clinico_SETEA.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        with c_csv_all:
            st.download_button(
                "Exportar Datos en CSV",
                data=df_filtrado.to_csv(index=False).encode("utf-8"),
                file_name="expedientes_clinicos_setea.csv",
                mime="text/csv",
                use_container_width=True
            )

if __name__ == "__main__":
    main()