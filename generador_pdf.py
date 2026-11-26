import os
from datetime import datetime
from fpdf import FPDF


def _limpiar_texto(texto):
    """Convierte caracteres Unicode a Latin-1 seguro para FPDF estandar."""
    if texto is None:
        return ""
    reemplazos = {
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
        "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U",
        "ñ": "n", "Ñ": "N", "ü": "u", "Ü": "U",
        "¿": "?", "¡": "!", "—": "-", "–": "-", "•": "-", "·": "|"
    }
    res = str(texto)
    for k, v in reemplazos.items():
        res = res.replace(k, v)
    return res.encode("latin-1", "replace").decode("latin-1")


class ReporteClinicoPDF(FPDF):
    def header(self):
        # Barra superior morada SE-TEA (#7353A6 -> RGB 115, 83, 166)
        self.set_fill_color(115, 83, 166)
        self.rect(0, 0, self.w, 22, "F")

        # Si existe logo.png o logo.jpg lo inserta en la esquina
        base_dir = os.path.dirname(os.path.abspath(__file__))
        for logo_name in ["logo.png", "logo.jpg", "logo.jpeg"]:
            logo_path = os.path.join(base_dir, logo_name)
            if os.path.exists(logo_path):
                self.image(logo_path, x=12, y=3.5, h=15)
                break

        self.set_xy(32, 5)
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(255, 255, 255)
        self.cell(self.w - 42, 6, "SE-TEA | Reporte Clinico de Tamizaje Emocional", ln=True)

        self.set_x(32)
        self.set_font("Helvetica", "", 8.5)
        self.set_text_color(240, 235, 250)
        self.cell(self.w - 42, 5, "Sistema Experto de Apoyo en Salud Mental Adolescente", ln=True)
        self.ln(8)
        self.set_x(self.l_margin)

    def footer(self):
        self.set_y(-15)
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(110, 101, 135)
        fecha_imp = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.cell(self.epw, 10, f"Documento de apoyo al tamizaje clinico - Generado el {fecha_imp} | Pagina {self.page_no()}", align="C")


def generar_pdf_expediente(datos_paciente: dict) -> bytes:
    """Genera el reporte PDF individual dividido por secciones de diagnostico."""
    pdf = ReporteClinicoPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    ancho_util = pdf.epw

    # Titulo del documento
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(48, 41, 68)
    folio = _limpiar_texto(datos_paciente.get("id", "N/A"))
    fecha_eval = _limpiar_texto(datos_paciente.get("fecha_evaluacion", datetime.now().strftime("%Y-%m-%d %H:%M")))
    pdf.cell(ancho_util, 8, f"INFORME DE VALORACION PSICOMETRICA (FOLIO: {folio})", ln=True)

    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(107, 98, 133)
    pdf.cell(ancho_util, 5, f"Fecha de aplicacion: {fecha_eval}", ln=True)
    pdf.ln(4)

    # SECCION 1: DATOS GENERALES Y CONTEXTO PSICOSOCIAL
    pdf.set_x(pdf.l_margin)
    pdf.set_fill_color(247, 245, 252)
    pdf.set_draw_color(185, 163, 220)
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_text_color(115, 83, 166)
    pdf.cell(ancho_util, 8, "  1. DATOS GENERALES Y CONTEXTO PSICOSOCIAL", border=1, ln=True, fill=True)

    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(48, 41, 68)
    nombre = _limpiar_texto(datos_paciente.get("identificador", ""))
    edad = _limpiar_texto(datos_paciente.get("edad", ""))
    convivencia = _limpiar_texto(datos_paciente.get("convivencia_familiar", ""))
    ocupacion = _limpiar_texto(datos_paciente.get("ocupacion", ""))
    med = _limpiar_texto(f"{datos_paciente.get('estado_medicacion', '')} ({datos_paciente.get('detalle_medicacion', '')})")
    sust = _limpiar_texto(f"{datos_paciente.get('consumo_sustancias', '')} ({datos_paciente.get('detalle_sustancias', '')})")

    pdf.ln(2)
    pdf.set_x(pdf.l_margin)
    pdf.cell(ancho_util * 0.68, 6, f"Nombre completo: {nombre}", border=0)
    pdf.cell(ancho_util * 0.32, 6, f"Edad: {edad} anos", ln=True)

    pdf.set_x(pdf.l_margin)
    pdf.cell(ancho_util * 0.52, 6, f"Convivencia: {convivencia}", border=0)
    pdf.cell(ancho_util * 0.48, 6, f"Ocupacion: {ocupacion}", ln=True)

    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(ancho_util, 6, f"Medicacion actual: {med}")

    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(ancho_util, 6, f"Consumo de sustancias: {sust}")
    pdf.ln(4)

    # SECCION 2: RESULTADOS POR SECCION DE DIAGNOSTICO
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_text_color(115, 83, 166)
    pdf.cell(ancho_util, 8, "  2. RESULTADOS POR SECCION DE DIAGNOSTICO", border=1, ln=True, fill=True)
    pdf.ln(3)

    secciones = [
        {
            "titulo": "Seccion I. Estres Percibido (Escala PSS-14)",
            "diag": _limpiar_texto(datos_paciente.get("diag_pss", "No evaluado")),
            "score": f"{datos_paciente.get('score_pss')} / 56 puntos" if datos_paciente.get("score_pss", -1) != -1 else "No aplicada en esta sesion",
            "nota": "Evalua el grado en que las situaciones cotidianas se perciben como impredecibles o sobrecargadas."
        },
        {
            "titulo": "Seccion II. Sintomatologia Ansiosa (Inventario BAI)",
            "diag": _limpiar_texto(datos_paciente.get("diag_bai", "No evaluado")),
            "score": f"{datos_paciente.get('score_bai')} / 63 puntos" if datos_paciente.get("score_bai", -1) != -1 else "No aplicada en esta sesion",
            "nota": "Mide manifestaciones somaticas y subjetivas de ansiedad durante la ultima semana."
        },
        {
            "titulo": "Seccion III. Sintomatologia Depresiva (Inventario BDI-II)",
            "diag": _limpiar_texto(datos_paciente.get("diag_bdi", "No evaluado")),
            "score": f"{datos_paciente.get('score_bdi')} / 63 puntos" if datos_paciente.get("score_bdi", -1) != -1 else "No aplicada en esta sesion",
            "nota": "Valora indicadores afectivos, cognitivos y somaticos vinculados al estado de animo."
        }
    ]

    for sec in secciones:
        pdf.set_x(pdf.l_margin)
        pdf.set_fill_color(255, 255, 255)
        pdf.set_draw_color(131, 185, 218)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(48, 41, 68)
        pdf.cell(ancho_util, 7, f"  {sec['titulo']}", border="LTR", ln=True)

        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", "B", 9.5)
        pdf.set_text_color(115, 83, 166)
        pdf.cell(ancho_util * 0.58, 6, f"  Clasificacion: {sec['diag']}", border="L")
        pdf.set_font("Helvetica", "", 9.5)
        pdf.set_text_color(48, 41, 68)
        pdf.cell(ancho_util * 0.42, 6, f"Puntaje: {sec['score']}", border="R", ln=True)

        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", "I", 8.5)
        pdf.set_text_color(107, 98, 133)
        pdf.multi_cell(ancho_util, 5.5, f"  {sec['nota']}", border="LBR")
        pdf.ln(3)

    # SECCION 3: DICTAMEN DE COMORBILIDAD E INFERENCIA CLINICA
    pdf.set_x(pdf.l_margin)
    pdf.set_fill_color(247, 245, 252)
    pdf.set_draw_color(233, 164, 197)
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_text_color(115, 83, 166)
    pdf.cell(ancho_util, 8, "  3. DICTAMEN CLINICO INTEGRADO Y COMORBILIDAD", border=1, ln=True, fill=True)
    pdf.ln(2)

    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(48, 41, 68)
    dictamen = _limpiar_texto(datos_paciente.get("comorbilidad", ""))
    pdf.multi_cell(ancho_util, 6, dictamen, border=1)
    pdf.ln(6)

    # Espacio para observaciones y firma del profesional
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.set_text_color(115, 83, 166)
    pdf.cell(ancho_util, 6, "Observaciones del especialista / orientador:", ln=True)

    pdf.set_x(pdf.l_margin)
    pdf.set_draw_color(185, 163, 220)
    pdf.cell(ancho_util, 18, "", border=1, ln=True)
    pdf.ln(10)

    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(48, 41, 68)
    pdf.cell(ancho_util, 5, "_____________________________________________", align="C", ln=True)
    pdf.set_x(pdf.l_margin)
    pdf.cell(ancho_util, 5, "Nombre y Firma del Profesional Responsable", align="C", ln=True)

    return bytes(pdf.output())


def generar_pdf_historial_general(registros: list) -> bytes:
    """Genera un reporte consolidado en PDF con el historial de expedientes y diagnosticos."""
    pdf = ReporteClinicoPDF(orientation="L", unit="mm", format="A4")
    pdf.set_margins(12, 12, 12)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(48, 41, 68)
    pdf.cell(pdf.epw, 7, f"REPORTE CONSOLIDADO DE EXPEDIENTES CLINICOS (Total: {len(registros)} registros)", ln=True)
    pdf.ln(3)

    # Encabezados de tabla
    pdf.set_x(pdf.l_margin)
    pdf.set_fill_color(115, 83, 166)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 8.5)

    anchos = [14, 26, 56, 14, 41, 41, 41, 40]
    headers = ["Folio", "Fecha", "Nombre Completo", "Edad", "Estres (PSS-14)", "Ansiedad (BAI)", "Depresion (BDI-II)", "Sustancias"]

    for w, h in zip(anchos, headers):
        pdf.cell(w, 8, h, border=1, align="C", fill=True)
    pdf.ln()

    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(48, 41, 68)

    for idx, reg in enumerate(registros):
        pdf.set_x(pdf.l_margin)
        fill = (idx % 2 == 1)
        pdf.set_fill_color(247, 245, 252) if fill else pdf.set_fill_color(255, 255, 255)

        fila = [
            str(reg.get("id", "")),
            _limpiar_texto(str(reg.get("fecha_evaluacion", ""))[:10]),
            _limpiar_texto(reg.get("identificador", ""))[:30],
            f"{reg.get('edad', '')} a.",
            _limpiar_texto(reg.get("diag_pss", ""))[:22],
            _limpiar_texto(reg.get("diag_bai", ""))[:22],
            _limpiar_texto(reg.get("diag_bdi", ""))[:22],
            _limpiar_texto(reg.get("consumo_sustancias", ""))[:20],
        ]
        for w, val in zip(anchos, fila):
            pdf.cell(w, 7, val, border=1, align="C", fill=fill)
        pdf.ln()

    return bytes(pdf.output())


def generar_pdf_expediente_completo(sesiones: list) -> bytes:
    """
    Genera un solo PDF longitudinal con todas las sesiones registradas de un mismo adolescente:
    - Datos generales actualizados
    - Tabla comparativa de evolucion entre sesiones
    - Desglose clinico por seccion diagnostica de cada sesion
    """
    if not sesiones:
        return b""

    sesiones_ord = sorted(sesiones, key=lambda x: x.get("id", 0))
    ultima = sesiones_ord[-1]

    pdf = ReporteClinicoPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    ancho_util = pdf.epw
    nombre = _limpiar_texto(ultima.get("identificador", ""))
    total_ses = len(sesiones_ord)

    # Encabezado del expediente longitudinal
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "B", 13.5)
    pdf.set_text_color(48, 41, 68)
    pdf.cell(ancho_util, 8, f"EXPEDIENTE CLINICO LONGITUDINAL ({total_ses} SESIONES)", ln=True)

    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(107, 98, 133)
    f_ini = _limpiar_texto(str(sesiones_ord[0].get("fecha_evaluacion", ""))[:10])
    f_fin = _limpiar_texto(str(ultima.get("fecha_evaluacion", ""))[:10])
    pdf.cell(ancho_util, 5, f"Periodo de seguimiento: {f_ini} al {f_fin}", ln=True)
    pdf.ln(4)

    # 1. DATOS DEL ADOLESCENTE (ULTIMA ACTUALIZACION)
    pdf.set_x(pdf.l_margin)
    pdf.set_fill_color(247, 245, 252)
    pdf.set_draw_color(185, 163, 220)
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_text_color(115, 83, 166)
    pdf.cell(ancho_util, 8, "  1. DATOS GENERALES Y CONTEXTO ACTUAL", border=1, ln=True, fill=True)

    pdf.ln(2)
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(48, 41, 68)
    pdf.set_x(pdf.l_margin)
    pdf.cell(ancho_util * 0.68, 6, f"Nombre completo: {nombre}", border=0)
    pdf.cell(ancho_util * 0.32, 6, f"Edad actual: {_limpiar_texto(ultima.get('edad', ''))} anos", ln=True)

    pdf.set_x(pdf.l_margin)
    pdf.cell(ancho_util * 0.52, 6, f"Convivencia: {_limpiar_texto(ultima.get('convivencia_familiar', ''))}", border=0)
    pdf.cell(ancho_util * 0.48, 6, f"Ocupacion: {_limpiar_texto(ultima.get('ocupacion', ''))}", ln=True)

    med = _limpiar_texto(f"{ultima.get('estado_medicacion', '')} ({ultima.get('detalle_medicacion', '')})")
    sust = _limpiar_texto(f"{ultima.get('consumo_sustancias', '')} ({ultima.get('detalle_sustancias', '')})")
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(ancho_util, 6, f"Medicacion reciente: {med}")
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(ancho_util, 6, f"Consumo de sustancias reciente: {sust}")
    pdf.ln(4)

    # 2. TABLA COMPARATIVA DE EVOLUCION ENTRE SESIONES
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_text_color(115, 83, 166)
    pdf.cell(ancho_util, 8, "  2. RESUMEN COMPARATIVO DE EVOLUCION POR SESION", border=1, ln=True, fill=True)
    pdf.ln(2)

    pdf.set_x(pdf.l_margin)
    pdf.set_fill_color(115, 83, 166)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 8.5)

    anchos = [18, 16, 26, 40, 40, 40]
    headers = ["Sesion", "Folio", "Fecha", "Estres (PSS-14)", "Ansiedad (BAI)", "Depresion (BDI-II)"]
    for w, h in zip(anchos, headers):
        pdf.cell(w, 7.5, h, border=1, align="C", fill=True)
    pdf.ln()

    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(48, 41, 68)
    for idx, s in enumerate(sesiones_ord):
        pdf.set_x(pdf.l_margin)
        fill = (idx % 2 == 1)
        pdf.set_fill_color(247, 245, 252) if fill else pdf.set_fill_color(255, 255, 255)

        p_txt = f"{s.get('score_pss')} pts" if s.get("score_pss", -1) != -1 else "N/A"
        b_txt = f"{s.get('score_bai')} pts" if s.get("score_bai", -1) != -1 else "N/A"
        d_txt = f"{s.get('score_bdi')} pts" if s.get("score_bdi", -1) != -1 else "N/A"

        fila = [
            f"#{idx + 1}",
            f"#{s.get('id', '')}",
            _limpiar_texto(str(s.get("fecha_evaluacion", ""))[:10]),
            _limpiar_texto(f"{s.get('diag_pss', '')} ({p_txt})")[:24],
            _limpiar_texto(f"{s.get('diag_bai', '')} ({b_txt})")[:24],
            _limpiar_texto(f"{s.get('diag_bdi', '')} ({d_txt})")[:24],
        ]
        for w, val in zip(anchos, fila):
            pdf.cell(w, 7, val, border=1, align="C", fill=fill)
        pdf.ln()

    pdf.ln(5)

    # 3. DETALLE CRONOLOGICO DE DIAGNOSTICO Y DICTAMEN POR SESION
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_text_color(115, 83, 166)
    pdf.cell(ancho_util, 8, "  3. DESGLOSE CLINICO DETALLADO POR SESION", border=1, ln=True, fill=True)
    pdf.ln(3)

    for idx, s in enumerate(sesiones_ord):
        pdf.set_x(pdf.l_margin)
        pdf.set_fill_color(241, 248, 253)
        pdf.set_draw_color(131, 185, 218)
        pdf.set_font("Helvetica", "B", 9.5)
        pdf.set_text_color(48, 41, 68)
        fecha_s = _limpiar_texto(str(s.get("fecha_evaluacion", ""))[:16])
        pdf.cell(ancho_util, 7, f"  Sesion #{idx + 1} | Folio #{s.get('id', '')} | Fecha: {fecha_s} | Edad: {s.get('edad', '')} anos", border="LTR", ln=True, fill=True)

        p_full = f"{s.get('diag_pss')} ({s.get('score_pss')}/56)" if s.get("score_pss", -1) != -1 else "No evaluado"
        b_full = f"{s.get('diag_bai')} ({s.get('score_bai')}/63)" if s.get("score_bai", -1) != -1 else "No evaluado"
        d_full = f"{s.get('diag_bdi')} ({s.get('score_bdi')}/63)" if s.get("score_bdi", -1) != -1 else "No evaluado"

        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", "", 8.8)
        pdf.set_text_color(48, 41, 68)
        pdf.multi_cell(
            ancho_util, 5.5,
            _limpiar_texto(f"  - Seccion I (Estres): {p_full}   |   Seccion II (Ansiedad): {b_full}   |   Seccion III (Depresion): {d_full}"),
            border="LR"
        )

        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", "", 8.8)
        dictamen_s = _limpiar_texto(s.get("comorbilidad", "")).replace("\n\n", " | ")
        pdf.multi_cell(ancho_util, 5.5, f"  Dictamen: {dictamen_s}", border="LBR")
        pdf.ln(3)

    # Firma final
    pdf.ln(6)
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(48, 41, 68)
    pdf.cell(ancho_util, 5, "_____________________________________________", align="C", ln=True)
    pdf.set_x(pdf.l_margin)
    pdf.cell(ancho_util, 5, "Nombre y Firma del Profesional Responsable", align="C", ln=True)

    return bytes(pdf.output())