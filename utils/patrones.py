import cv2
import numpy as np
import random
import math


class GeneradorPatrones:
    def __init__(self):
        self.patrones = []
        self.tipo_actual = ""
        self.puntos_clave = []  # Puntos importantes que se deben pasar
        self.generar_patron()

    def generar_patron(self):
        """Genera un patrón aleatorio adaptado al tamaño del frame"""
        self.tipo_actual = random.choice(
            ["circulo", "triangulo", "curva", "zigzag", "espiral"]
        )
        puntos = []
        puntos_clave = []

        if self.tipo_actual == "circulo":
            # Círculo más grande y centrado
            cx, cy = 320, 240
            radio = 120
            for i in range(0, 360, 8):
                ang = math.radians(i)
                x = int(cx + radio * math.cos(ang))
                y = int(cy + radio * math.sin(ang))
                puntos.append((x, y))
                # Puntos clave cada 90 grados
                if i % 90 == 0:
                    puntos_clave.append((x, y))

        elif self.tipo_actual == "triangulo":
            # Triángulo equilátero con más puntos intermedios
            cx, cy = 320, 280
            size = 180
            vertices = [
                (cx - size // 2, cy + size // 3),
                (cx + size // 2, cy + size // 3),
                (cx, cy - 2 * size // 3),
                (cx - size // 2, cy + size // 3),
            ]

            # Interpolar puntos entre vértices
            for i in range(len(vertices) - 1):
                x1, y1 = vertices[i]
                x2, y2 = vertices[i + 1]
                steps = 20
                for j in range(steps):
                    t = j / steps
                    x = int(x1 + (x2 - x1) * t)
                    y = int(y1 + (y2 - y1) * t)
                    puntos.append((x, y))

            puntos_clave = vertices[:-1]  # Los 3 vértices

        elif self.tipo_actual == "curva":
            # Curva sinusoidal con más resolución
            for t in np.linspace(0, 2 * np.pi, 80):
                x = int(200 + t * 60)
                y = int(240 + 100 * math.sin(2 * t))
                puntos.append((x, y))
                # Puntos clave en máximos y mínimos
                if abs(math.sin(2 * t)) > 0.95:
                    puntos_clave.append((x, y))

        elif self.tipo_actual == "zigzag":
            # Zigzag horizontal con más puntos
            x_inicio, y_inicio = 150, 240
            amplitud = 80
            for i in range(8):
                x = x_inicio + i * 60
                y = y_inicio + (amplitud if i % 2 == 0 else -amplitud)
                # Interpolar entre puntos
                if i > 0:
                    x_prev = x_inicio + (i - 1) * 60
                    y_prev = y_inicio + (amplitud if (i - 1) % 2 == 0 else -amplitud)
                    steps = 10
                    for j in range(steps):
                        t = j / steps
                        px = int(x_prev + (x - x_prev) * t)
                        py = int(y_prev + (y - y_prev) * t)
                        puntos.append((px, py))
                puntos_clave.append((x, y))

        elif self.tipo_actual == "espiral":
            # Espiral desde el centro con más puntos
            cx, cy = 320, 240
            for i in range(0, 360 * 2, 10):
                ang = math.radians(i)
                radio = i / 10
                x = int(cx + radio * math.cos(ang))
                y = int(cy + radio * math.sin(ang))
                puntos.append((x, y))
                # Puntos clave cada vuelta
                if i % 360 == 0:
                    puntos_clave.append((x, y))

        self.patrones = puntos
        self.puntos_clave = (
            puntos_clave
            if puntos_clave
            else [puntos[0], puntos[len(puntos) // 2], puntos[-1]]
        )

    def calcular_distancia_a_inicio(self, pos):
        """Calcula la distancia del punto dado al inicio del patrón"""
        if not self.patrones or pos[0] is None:
            return float("inf")

        inicio = self.patrones[0]
        dx = pos[0] - inicio[0]
        dy = pos[1] - inicio[1]
        return math.sqrt(dx * dx + dy * dy)

    def calcular_progreso_detallado(self, rastro_usuario):
        """
        Calcula el progreso detallado del usuario en el patrón
        Retorna: (cobertura_total, llegado_al_final, porcentaje_del_patron)
        """
        if not rastro_usuario or not self.patrones:
            return 0.0, False, 0.0

        umbral_cercania = 40  # Píxeles de tolerancia (más estricto)

        # 1. COBERTURA: Verificar qué porcentaje del patrón fue cubierto
        puntos_patron_cubiertos = set()
        for idx, punto_patron in enumerate(self.patrones):
            for punto_usuario in rastro_usuario:
                dx = punto_usuario[0] - punto_patron[0]
                dy = punto_usuario[1] - punto_patron[1]
                distancia = math.sqrt(dx * dx + dy * dy)
                if distancia < umbral_cercania:
                    puntos_patron_cubiertos.add(idx)
                    break

        cobertura = (
            len(puntos_patron_cubiertos) / len(self.patrones) if self.patrones else 0
        )

        # 2. VERIFICAR SI LLEGÓ AL FINAL
        punto_final = self.patrones[-1]
        distancia_al_final = float("inf")
        for punto_usuario in rastro_usuario[-10:]:  # Revisar últimos 10 puntos
            dx = punto_usuario[0] - punto_final[0]
            dy = punto_usuario[1] - punto_final[1]
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < distancia_al_final:
                distancia_al_final = dist

        llegado_al_final = distancia_al_final < 60  # Debe estar cerca del final

        # 3. CALCULAR PORCENTAJE DEL PATRÓN RECORRIDO (secuencial)
        # Encontrar el punto más lejano del patrón que fue alcanzado
        max_indice_alcanzado = 0
        for idx, punto_patron in enumerate(self.patrones):
            for punto_usuario in rastro_usuario:
                dx = punto_usuario[0] - punto_patron[0]
                dy = punto_usuario[1] - punto_patron[1]
                distancia = math.sqrt(dx * dx + dy * dy)
                if distancia < umbral_cercania:
                    max_indice_alcanzado = max(max_indice_alcanzado, idx)

        porcentaje_patron = (
            (max_indice_alcanzado / len(self.patrones)) * 100 if self.patrones else 0
        )

        return cobertura, llegado_al_final, porcentaje_patron

    def dibujar_patron_en_frame(self, frame, rastro_usuario=[]):
        """Dibuja el patrón objetivo con indicadores de progreso"""
        if not self.patrones:
            return frame

        umbral = 40

        # Identificar qué puntos del patrón ya fueron cubiertos
        puntos_cubiertos = set()
        if rastro_usuario:
            for idx, punto_patron in enumerate(self.patrones):
                for punto_usuario in rastro_usuario:
                    dx = punto_usuario[0] - punto_patron[0]
                    dy = punto_usuario[1] - punto_patron[1]
                    if math.sqrt(dx * dx + dy * dy) < umbral:
                        puntos_cubiertos.add(idx)
                        break

        # Dibujar líneas del patrón
        for i in range(len(self.patrones) - 1):
            # Color según si ya fue cubierto
            if i in puntos_cubiertos:
                color = (0, 255, 0)  # Verde = ya pasaste por aquí
                grosor = 3
            else:
                color = (255, 200, 0)  # Azul/amarillo = falta pasar
                grosor = 4
            cv2.line(frame, self.patrones[i], self.patrones[i + 1], color, grosor)

        # Dibujar puntos del patrón
        for i, punto in enumerate(self.patrones):
            if i % 8 == 0:  # Cada 8 puntos
                if i in puntos_cubiertos:
                    cv2.circle(frame, punto, 6, (0, 255, 0), -1)  # Verde
                else:
                    cv2.circle(frame, punto, 6, (255, 150, 0), -1)  # Naranja
                cv2.circle(frame, punto, 8, (255, 255, 255), 1)

        # Marcar PUNTOS CLAVE con círculos grandes
        for i, punto_clave in enumerate(self.puntos_clave):
            if any(
                math.sqrt((p[0] - punto_clave[0]) ** 2 + (p[1] - punto_clave[1]) ** 2)
                < umbral
                for p in rastro_usuario
            ):
                color = (0, 255, 0)  # Verde = completado
            else:
                color = (255, 100, 0)  # Naranja = pendiente
            cv2.circle(frame, punto_clave, 12, color, 2)
            cv2.circle(frame, punto_clave, 15, (255, 255, 255), 1)

        # Marcar punto de INICIO
        if len(self.patrones) > 0:
            overlay = frame.copy()
            cv2.circle(overlay, self.patrones[0], 50, (0, 255, 0), 2)
            cv2.circle(overlay, self.patrones[0], 48, (0, 255, 0), -1)
            frame = cv2.addWeighted(frame, 0.85, overlay, 0.15, 0)

            cv2.circle(frame, self.patrones[0], 20, (0, 255, 0), -1)
            cv2.circle(frame, self.patrones[0], 22, (255, 255, 255), 3)
            cv2.putText(
                frame,
                "INICIO",
                (self.patrones[0][0] - 40, self.patrones[0][1] - 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
            )

        # Marcar punto FINAL con área grande
        if len(self.patrones) > 1:
            overlay = frame.copy()
            cv2.circle(overlay, self.patrones[-1], 60, (0, 0, 255), 2)
            cv2.circle(overlay, self.patrones[-1], 58, (0, 0, 255), -1)
            frame = cv2.addWeighted(frame, 0.85, overlay, 0.15, 0)

            cv2.circle(frame, self.patrones[-1], 20, (0, 0, 255), -1)
            cv2.circle(frame, self.patrones[-1], 22, (255, 255, 255), 3)
            cv2.putText(
                frame,
                "FIN",
                (self.patrones[-1][0] - 25, self.patrones[-1][1] - 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2,
            )

        return frame
