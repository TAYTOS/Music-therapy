import cv2
import numpy as np
import math


class GeneradorPatrones:
    def __init__(self):
        self.patrones = []
        self.tipo_actual = ""
        self.puntos_clave = []
        self.generar_patron()

    def generar_patron(self):
        if not hasattr(self, "indice_patron"):
            self.indice_patron = 0

        orden_patrones = ["zigzag","curva","triangulo","circulo","espiral"]

        self.tipo_actual = orden_patrones[self.indice_patron]
        self.indice_patron = (self.indice_patron + 1) % len(orden_patrones)

        puntos = []
        puntos_clave = []

        if self.tipo_actual == "circulo":
            cx, cy = 320, 240
            radio = 120
            for i in range(0, 360, 8):
                ang = math.radians(i)
                x = int(cx + radio * math.cos(ang))
                y = int(cy + radio * math.sin(ang))
                puntos.append((x, y))
                if i % 90 == 0:
                    puntos_clave.append((x, y))

        elif self.tipo_actual == "triangulo":
            cx, cy = 320, 280
            size = 180
            vertices = [
                (cx - size // 2, cy + size // 3),
                (cx + size // 2, cy + size // 3),
                (cx, cy - 2 * size // 3),
                (cx - size // 2, cy + size // 3),
            ]

            for i in range(len(vertices) - 1):
                x1, y1 = vertices[i]
                x2, y2 = vertices[i + 1]
                steps = 20
                for j in range(steps):
                    t = j / steps
                    x = int(x1 + (x2 - x1) * t)
                    y = int(y1 + (y2 - y1) * t)
                    puntos.append((x, y))

            puntos_clave = vertices[:-1]

        elif self.tipo_actual == "curva":
            for t in np.linspace(0, 2 * np.pi, 80):
                x = int(200 + t * 60)
                y = int(240 + 100 * math.sin(2 * t))
                puntos.append((x, y))
                if abs(math.sin(2 * t)) > 0.95:
                    puntos_clave.append((x, y))

        elif self.tipo_actual == "zigzag":
            x_inicio, y_inicio = 150, 240
            amplitud = 80
            for i in range(8):
                x = x_inicio + i * 60
                y = y_inicio + (amplitud if i % 2 == 0 else -amplitud)
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
            cx, cy = 320, 240
            for i in range(0, 360 * 4, 10):
                ang = math.radians(i)
                radio = i / 10
                x = int(cx + radio * math.cos(ang))
                y = int(cy + radio * math.sin(ang))
                puntos.append((x, y))
                if i % 360 == 0:
                    puntos_clave.append((x, y))

        self.patrones = puntos
        self.puntos_clave = (
            puntos_clave
            if puntos_clave
            else [puntos[0], puntos[len(puntos) // 2], puntos[-1]]
        )

    def calcular_distancia_a_inicio(self, pos):
        if not self.patrones or pos[0] is None:
            return float("inf")

        inicio = self.patrones[0]
        dx = pos[0] - inicio[0]
        dy = pos[1] - inicio[1]
        return math.sqrt(dx * dx + dy * dy)

    def calcular_progreso_detallado(self, rastro_usuario):
        if not rastro_usuario or not self.patrones:
            return 0.0, False, 0.0

        umbral_cercania = 40

        puntos_patron_cubiertos = set()
        for idx, punto_patron in enumerate(self.patrones):
            for punto_usuario in rastro_usuario:
                dx = punto_usuario[0] - punto_patron[0]
                dy = punto_usuario[1] - punto_patron[1]
                if math.sqrt(dx * dx + dy * dy) < umbral_cercania:
                    puntos_patron_cubiertos.add(idx)
                    break

        cobertura = len(puntos_patron_cubiertos) / len(self.patrones)

        punto_final = self.patrones[-1]
        distancia_al_final = float("inf")
        for punto_usuario in rastro_usuario[-10:]:
            dx = punto_usuario[0] - punto_final[0]
            dy = punto_usuario[1] - punto_final[1]
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < distancia_al_final:
                distancia_al_final = dist

        llegado_al_final = distancia_al_final < 60

        max_indice_alcanzado = 0
        for idx, punto_patron in enumerate(self.patrones):
            for punto_usuario in rastro_usuario:
                dx = punto_usuario[0] - punto_patron[0]
                dy = punto_usuario[1] - punto_patron[1]
                if math.sqrt(dx * dx + dy * dy) < umbral_cercania:
                    max_indice_alcanzado = max(max_indice_alcanzado, idx)

        porcentaje_patron = (max_indice_alcanzado / len(self.patrones)) * 100

        return cobertura, llegado_al_final, porcentaje_patron

    def dibujar_patron_en_frame(self, frame, rastro_usuario=[]):
        if not self.patrones:
            return frame

        umbral = 40
        puntos_cubiertos = set()

        for idx, punto_patron in enumerate(self.patrones):
            for punto_usuario in rastro_usuario:
                dx = punto_usuario[0] - punto_patron[0]
                dy = punto_usuario[1] - punto_patron[1]
                if math.sqrt(dx * dx + dy * dy) < umbral:
                    puntos_cubiertos.add(idx)
                    break

        for i in range(len(self.patrones) - 1):
            color = (0, 255, 0) if i in puntos_cubiertos else (255, 200, 0)
            grosor = 3 if i in puntos_cubiertos else 4
            cv2.line(frame, self.patrones[i], self.patrones[i + 1], color, grosor)

        for i, punto in enumerate(self.patrones):
            if i % 8 == 0:
                color = (0, 255, 0) if i in puntos_cubiertos else (255, 150, 0)
                cv2.circle(frame, punto, 6, color, -1)
                cv2.circle(frame, punto, 8, (255, 255, 255), 1)

        for punto_clave in self.puntos_clave:
            if any(
                math.sqrt((p[0] - punto_clave[0]) ** 2 + (p[1] - punto_clave[1]) ** 2)
                < umbral
                for p in rastro_usuario
            ):
                color = (0, 255, 0)
            else:
                color = (255, 100, 0)
            cv2.circle(frame, punto_clave, 12, color, 2)
            cv2.circle(frame, punto_clave, 15, (255, 255, 255), 1)

        if self.patrones:
            cv2.circle(frame, self.patrones[0], 20, (0, 255, 0), -1)
            cv2.circle(frame, self.patrones[0], 22, (255, 255, 255), 3)

        if len(self.patrones) > 1:
            cv2.circle(frame, self.patrones[-1], 20, (0, 0, 255), -1)
            cv2.circle(frame, self.patrones[-1], 22, (255, 255, 255), 3)

        return frame