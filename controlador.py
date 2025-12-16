import cv2
import numpy as np
import time
from utils.camara import Camara
from utils.patrones import GeneradorPatrones
from utils.musica import GestorMusica
from vista import Vista


def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("No se pudo acceder a la cámara IP.")
        return

    cam = Camara()
    vista = Vista()
    generador = GeneradorPatrones()
    musica = GestorMusica()

    score = 0
    estado = "esperando"

    rastro_usuario = []
    posicion_anterior = None

    combo_ritmo = 0
    max_combo = 0
    fallos_ritmo = 0
    MAX_FALLOS_RITMO = 3

    puntos_minimos = 30
    mensaje_temporal = ""
    tiempo_mensaje = 0

    musica.reiniciar_compas()

    while True:
        frame, is_fist, pos = cam.obtener_frame(cap)
        if frame is None:
            continue

        hay_beat = musica.actualizar()
        progreso_beat = musica.obtener_progreso_beat()
        en_ventana = musica.esta_en_ventana_sincronizacion()

        hay_movimiento = (
            is_fist
            and pos[0] is not None
            and posicion_anterior is not None
            and np.linalg.norm(np.array(pos) - np.array(posicion_anterior)) > 8
        )

        en_ritmo, fallo_instantaneo = musica.verificar_sincronizacion(hay_movimiento)

        # ================= RITMO (UN SOLO LUGAR) =================
        perdio_ritmo = False

        if en_ritmo:
            combo_ritmo += 1
            max_combo = max(max_combo, combo_ritmo)
            fallos_ritmo = max(0, fallos_ritmo - 1)
        elif fallo_instantaneo:
            fallos_ritmo += 1
            combo_ritmo = max(0, combo_ritmo - 1)
            if fallos_ritmo >= MAX_FALLOS_RITMO:
                perdio_ritmo = True

        tiempo_restante = int(musica.obtener_tiempo_restante_patron())
        beats_restantes = musica.obtener_beats_restantes()

        # ================= ESTADOS =================

        if estado == "esperando":
            rastro_usuario.clear()
            combo_ritmo = 0
            fallos_ritmo = 0

            if is_fist and pos[0] is not None:
                if generador.calcular_distancia_a_inicio(pos) < 50:
                    estado = "trazando"
                    rastro_usuario.append(pos)
                    musica.reiniciar_compas()
                    musica.reiniciar_estadisticas()

        elif estado == "trazando":
            if is_fist and pos[0] is not None:
                if not rastro_usuario or np.linalg.norm(
                    np.array(pos) - np.array(rastro_usuario[-1])
                ) > 5:
                    rastro_usuario.append(pos)

            if perdio_ritmo:
                estado = "fuera_ritmo"
                mensaje_temporal = "¡Perdiste el ritmo!"
                tiempo_mensaje = time.time()
                musica.reproducir_error()

            if len(rastro_usuario) >= 10:
                cobertura, llegado_final, _ = (
                    generador.calcular_progreso_detallado(rastro_usuario)
                )

                if (
                    cobertura >= 0.75
                    and llegado_final
                    and len(rastro_usuario) >= puntos_minimos
                ):
                    estado = "completado"

                    puntos = int(cobertura * 10)
                    puntos += min(combo_ritmo * 2, 20)
                    puntos += int(musica.obtener_precision_ritmo() / 10)

                    score += puntos
                    mensaje_temporal = f"¡PERFECTO! +{puntos} pts"
                    tiempo_mensaje = time.time()
                    musica.reproducir_exito()

            if musica.es_momento_de_nuevo_patron() and estado == "trazando":
                estado = "fallido"
                mensaje_temporal = "Tiempo agotado"
                tiempo_mensaje = time.time()

        elif estado in ("completado", "fallido", "fuera_ritmo"):
            generador.generar_patron()
            musica.reiniciar_compas()
            rastro_usuario.clear()
            fallos_ritmo = 0
            estado = "esperando"

        # ================= DIBUJO =================

        frame = generador.dibujar_patron_en_frame(
            frame, rastro_usuario if estado == "trazando" else []
        )

        # Mano (círculo restaurado)
        if pos[0] is not None:
            if is_fist:
                color = (0, 255, 255) if en_ventana else (0, 150, 255)
                radio = 25 if hay_beat else 20
                cv2.circle(frame, pos, radio, color, -1)
                cv2.circle(frame, pos, radio + 3, (255, 255, 255), 3)
            else:
                cv2.circle(frame, pos, 12, (255, 0, 0), -1)
                cv2.circle(frame, pos, 16, (255, 255, 255), 2)

        if musica.musica_activa:
            frame = vista.dibujar_indicador_beat(
                frame, progreso_beat, hay_beat, en_ritmo, combo_ritmo
            )

        frame = vista.dibujar_interfaz(
            frame,
            score,
            tiempo_restante,
            estado,
            len(rastro_usuario),
            musica.bpm,
            musica.musica_activa,
            beats_restantes,
            combo_ritmo,
            max_combo,
            musica.obtener_precision_ritmo(),
        )

        vista.mostrar(frame)

        if pos[0] is not None:
            posicion_anterior = pos

        key = cv2.waitKey(1) & 0xFF
        if key == ord(" "):
            break
        elif key in (ord("m"), ord("M")):
            musica.desactivar_musica() if musica.musica_activa else musica.activar_musica()
        elif key in (ord("+"), ord("=")):
            musica.cambiar_bpm(musica.bpm + 10)
        elif key in (ord("-"), ord("_")):
            musica.cambiar_bpm(musica.bpm - 10)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()