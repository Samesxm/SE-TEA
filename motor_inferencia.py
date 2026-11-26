class MotorInferencia:
    def __init__(self):
        pass

    def evaluar_depresion_bdi(self, puntaje):
        if puntaje == -1: return "No evaluado"
        elif puntaje <= 13: return "Minima depresion"
        elif puntaje <= 19: return "Depresion leve"
        elif puntaje <= 28: return "Depresion moderada"
        else: return "Depresion severa"

    def evaluar_ansiedad_bai(self, puntaje):
        if puntaje == -1: return "No evaluado"
        elif puntaje <= 21: return "Ansiedad muy baja"
        elif puntaje <= 35: return "Ansiedad moderada"
        else: return "Ansiedad severa"

    def evaluar_estres_pss(self, puntaje):
        if puntaje == -1: return "No evaluado"
        elif puntaje <= 14: return "Estres bajo"
        elif puntaje <= 28: return "Estres moderado"
        else: return "Estres alto"

    def evaluar_comorbilidad(self, nivel_depresion, nivel_ansiedad, nivel_estres):
        niveles_criticos_dep = ["Depresion moderada", "Depresion severa"]
        niveles_criticos_ans = ["Ansiedad moderada", "Ansiedad severa"]
        
        alertas = []
        if nivel_depresion in niveles_criticos_dep and nivel_ansiedad in niveles_criticos_ans:
            alertas.append("[COMORBILIDAD CRITICA] Se documenta un cuadro combinado de ansiedad y depresion clinicamente significativo que requiere atencion prioritaria.")
        
        if nivel_estres == "Estres alto":
            if nivel_depresion in niveles_criticos_dep or nivel_ansiedad in niveles_criticos_ans:
                alertas.append("[RIESGO ELEVADO] El nivel actual de estres percibido agudiza la vulnerabilidad emocional frente al cuadro clinico principal.")
            else:
                alertas.append("[ALERTA PREVENTIVA] Se detecta un nivel de estres percibido alto. Aunque la sintomatologia afectiva primaria es baja, se recomienda monitorizacion.")

        if not alertas:
            if "No evaluado" in [nivel_depresion, nivel_ansiedad, nivel_estres]:
                return "[EVALUACION PARCIAL] Los datos disponibles no sugieren riesgo critico inminente."
            return "[SIN HALLAZGOS CRITICOS] La sintomatologia evaluada se encuentra dentro de parametros manejables y no refleja patrones de comorbilidad."
        
        return "\n\n".join(alertas)

    def ejecutar_inferencia(self, score_bdi, score_bai, score_pss):
        diag_bdi = self.evaluar_depresion_bdi(score_bdi)
        diag_bai = self.evaluar_ansiedad_bai(score_bai)
        diag_pss = self.evaluar_estres_pss(score_pss)
        comorbilidad = self.evaluar_comorbilidad(diag_bdi, diag_bai, diag_pss)

        return {
            "diagnosticos": {
                "Depresion (BDI-II)": diag_bdi,
                "Ansiedad (BAI)": diag_bai,
                "Estres (PSS-14)": diag_pss
            },
            "comorbilidad": comorbilidad
        }