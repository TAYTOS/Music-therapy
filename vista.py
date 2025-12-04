import cv2
from utils.texto_unicode import TextoUnicode


class Vista:
    def __init__(self):
        self.texto_renderer = TextoUnicode()
        self.colores = {
            "fondo_panel": (20, 20, 40),
            "texto_principal": (255, 255, 255),
            "texto_score": (0, 255, 100),
            "texto_tiempo": (100, 200, 255),
            "borde": (100, 100, 200),
            "combo": (0, 255, 255),
        }

    def dibujar_interfaz(
        self,
        frame,
        score,
        tiempo_restante,
        estado,
        num_puntos,
        bpm,
        musica_activa,
        beats_restantes,
        combo,
        max_combo,
        precision_ritmo,
    ):
        """Dibuja la interfaz del juego sobre el frame"""
        h, w, _ = frame.shape

        # Crear overlay semi-transparente para el panel superior
        overlay = frame.copy()

        # Panel superior con información (más grande para más datos)
        cv2.rectangle(overlay, (0, 0), (w, 120), (30, 30, 60), -1)
        frame = cv2.addWeighted(frame, 0.6, overlay, 0.4, 0)

        # Borde decorativo
        cv2.rectangle(frame, (5, 5), (w - 5, 115), self.colores["borde"], 3)

        # FILA 1: Puntaje y Combo
        cv2.putText(
            frame,
            f"Puntaje: {score}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            self.colores["texto_score"],
            3,
        )

        # Combo con efecto visual
        if combo > 0:
            color_combo = self.colores["combo"]
            tamano_combo = 1.0 + (min(combo, 20) * 0.02)  # Crece con el combo
            cv2.putText(
                frame,
                f"COMBO x{combo}!",
                (w - 280, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                tamano_combo,
                color_combo,
                3,
            )

        # FILA 2: Tiempo/Beats restantes
        if tiempo_restante > 5:
            color_tiempo = (0, 255, 0)
        elif tiempo_restante > 2:
            color_tiempo = (0, 255, 255)
        else:
            color_tiempo = (0, 0, 255)

        cv2.putText(
            frame,
            f"Tiempo: {tiempo_restante}s | Beats: {beats_restantes}",
            (20, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            color_tiempo,
            2,
        )

        # Precisión de ritmo
        color_precision = (
            (0, 255, 0)
            if precision_ritmo >= 80
            else (0, 255, 255) if precision_ritmo >= 60 else (0, 0, 255)
        )
        cv2.putText(
            frame,
            f"Ritmo: {precision_ritmo}%",
            (w - 200, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            color_precision,
            2,
        )

        # FILA 3: Info musical y max combo
        color_musica = (0, 255, 0) if musica_activa else (100, 100, 100)
        cv2.putText(
            frame,
            f"BPM: {bpm} | Max Combo: {max_combo}",
            (20, 105),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color_musica,
            2,
        )

        # Instrucciones según el estado
        instrucciones = {
            "esperando": "Coloca el PUÑO en el circulo VERDE para comenzar a bailar",
            "trazando": "Mueve tu mano AL RITMO de los beats - NO pierdas 3 beats seguidos",
            "completado": "¡PERFECTO! Bailaste con ritmo",
            "fallido": "Tiempo agotado - Intenta otra vez",
            "fuera_ritmo": "¡Perdiste el ritmo! Nuevo patron",
        }

        texto_estado = instrucciones.get(estado, "")

        # Panel inferior con instrucciones
        overlay2 = frame.copy()
        cv2.rectangle(overlay2, (0, h - 70), (w, h), (30, 30, 60), -1)
        frame = cv2.addWeighted(frame, 0.6, overlay2, 0.4, 0)

        # Color del texto según el estado
        if estado == "completado":
            color_texto = (0, 255, 0)
        elif estado == "fuera_ritmo":
            color_texto = (0, 100, 255)
        elif estado == "fallido":
            color_texto = (0, 0, 255)
        elif estado == "trazando":
            color_texto = (0, 255, 255)
        else:
            color_texto = self.colores["texto_principal"]

        # Usar TextoUnicode para dibujar con soporte de ñ
        self.texto_renderer.put_text(
            frame, texto_estado, (20, h - 50), tamano=22, color=color_texto, grosor=2
        )

        return frame

    def dibujar_indicador_beat(
        self, frame, progreso_beat, hay_beat, en_sincronizacion, combo
    ):
        # Dibuja un indicador visual del beat con feedback de sincronización #
        h, w, _ = frame.shape

        # Posición del indicador (esquina superior derecha, más grande)
        centro_x = w - 80
        centro_y = 160
        radio_base = 35

        # Efecto de pulso cuando hay beat
        if hay_beat or progreso_beat < 0.2:
            factor_pulso = 1.8 - (progreso_beat * 3)
            radio = int(radio_base * factor_pulso)
            intensidad = 255
        else:
            radio = radio_base
            intensidad = int(100 + (155 * (1 - progreso_beat)))

        # Color según sincronización
        if en_sincronizacion:
            color = (0, 255, 0)  # Verde: ¡Perfecto!
            grosor_borde = 4
        elif progreso_beat < 0.3 or progreso_beat > 0.7:
            color = (0, 255, 255)  # Cian: Cerca del beat
            grosor_borde = 3
        else:
            color = (0, intensidad, 0)  # Verde oscuro: Espera el beat
            grosor_borde = 2

        # Dibujar círculo del beat
        cv2.circle(frame, (centro_x, centro_y), radio, color, -1)
        cv2.circle(
            frame, (centro_x, centro_y), radio + 2, (255, 255, 255), grosor_borde
        )

        # Barra de progreso circular (cuenta regresiva al próximo beat)
        angulo_inicio = -90
        angulo_fin = int(-90 + (360 * progreso_beat))
        cv2.ellipse(
            frame,
            (centro_x, centro_y),
            (radio_base + 12, radio_base + 12),
            0,
            angulo_inicio,
            angulo_fin,
            (100, 200, 255),
            4,
        )

        # Texto "BEAT!" cuando hay beat
        if hay_beat or progreso_beat < 0.15:
            cv2.putText(
                frame,
                "BEAT!",
                (centro_x - 35, centro_y + 8),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2,
            )

        # Indicador de combo debajo del beat
        if combo > 0:
            cv2.putText(
                frame,
                f"x{combo}",
                (centro_x - 20, centro_y + 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 255, 255),
                2,
            )

        return frame

    def mostrar(self, frame):
        """Muestra el frame en pantalla"""
        cv2.namedWindow("Terapia de Rehabilitacion-Music Therapy", cv2.WINDOW_NORMAL)
        cv2.imshow("Terapia de Rehabilitacion-Music Therapy", frame)
