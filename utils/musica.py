# -*- coding: utf-8 -*-
import pygame
import time


class GestorMusica:
    """Modelo para gestionar la música y el ritmo del juego"""

    def __init__(self):
        # Inicializar pygame mixer para audio
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

        # Configuración de ritmo
        self.bpm = 90  # Beats por minuto (ritmo medio para seguir)
        self.beat_interval = 60.0 / self.bpm  # Tiempo entre beats en segundos
        self.last_beat_time = time.time()
        self.beat_count = 0

        # Configuración de compás (cuántos beats por patrón)
        self.beats_por_patron = 16  # 16 beats = 4 compases de 4/4
        self.tiempo_por_patron = self.beats_por_patron * self.beat_interval

        # Control de sincronización (bailar al ritmo)
        self.ventana_sincronizacion = 0.3  # Ventana de 0.3 seg antes/después del beat
        self.beats_perdidos_consecutivos = 0
        self.max_beats_perdidos = 3  # Perder 3 beats seguidos = cambio de patrón
        self.ultimo_movimiento_tiempo = time.time()

        # Estado de la música
        self.musica_activa = True
        self.volumen = 0.4  # Volumen más alto

        # Control de patrones
        self.tiempo_inicio_compas = time.time()

        # Estadísticas
        self.total_beats = 0
        self.beats_acertados = 0

        # Generar sonidos de beat
        self._generar_sonidos()

    def _generar_sonidos(self):
        """Genera sonidos sintéticos para el beat"""
        sample_rate = 22050
        duration = 0.15  # Duración del beat

        # Beat principal (tono claro y distintivo)
        self.beat_principal = self._crear_tono(
            523, duration, sample_rate, volumen=0.4
        )  # Do

        # Beat acento (tono más fuerte para cada 4 beats)
        self.beat_acento = self._crear_tono(
            659, duration, sample_rate, volumen=0.6
        )  # Mi

        # Beat de éxito (melodía ascendente)
        self.beat_exito = self._crear_melodia(
            [523, 659, 784], 0.2, sample_rate, volumen=0.5
        )

        # Sonido de error (tono bajo)
        self.beat_error = self._crear_tono(220, 0.3, sample_rate, volumen=0.3)

    def _crear_tono(self, frecuencia, duracion, sample_rate, volumen=0.3):
        """Crea un tono sintético simple"""
        import numpy as np

        n_samples = int(duracion * sample_rate)
        t = np.linspace(0, duracion, n_samples)

        # Generar onda con armónicos para sonido más rico
        onda = np.sin(2 * np.pi * frecuencia * t)
        onda += 0.3 * np.sin(4 * np.pi * frecuencia * t)  # Segundo armónico

        # Aplicar envolvente ADSR
        attack = int(n_samples * 0.05)
        decay = int(n_samples * 0.15)
        sustain_level = 0.7
        release = int(n_samples * 0.3)

        envolvente = np.ones(n_samples)
        envolvente[:attack] = np.linspace(0, 1, attack)
        envolvente[attack : attack + decay] = np.linspace(1, sustain_level, decay)
        envolvente[-release:] = np.linspace(sustain_level, 0, release)

        onda = onda * envolvente * volumen

        # Convertir a formato pygame
        onda_stereo = np.column_stack([onda, onda])
        onda_int16 = (onda_stereo * 32767).astype(np.int16)

        sound = pygame.sndarray.make_sound(onda_int16)
        return sound

    def _crear_melodia(self, frecuencias, duracion_total, sample_rate, volumen=0.3):
        """Crea una melodía con múltiples tonos"""
        import numpy as np

        duracion_nota = duracion_total / len(frecuencias)
        ondas = []

        for freq in frecuencias:
            n_samples = int(duracion_nota * sample_rate)
            t = np.linspace(0, duracion_nota, n_samples)
            onda = np.sin(2 * np.pi * freq * t)

            # Envolvente suave
            envolvente = np.ones(n_samples)
            fade = int(n_samples * 0.1)
            envolvente[:fade] = np.linspace(0, 1, fade)
            envolvente[-fade:] = np.linspace(1, 0, fade)

            onda = onda * envolvente
            ondas.append(onda)

        onda_completa = np.concatenate(ondas) * volumen
        onda_stereo = np.column_stack([onda_completa, onda_completa])
        onda_int16 = (onda_stereo * 32767).astype(np.int16)

        sound = pygame.sndarray.make_sound(onda_int16)
        return sound

    def actualizar(self):
        """Actualiza el sistema de música y devuelve True si hay un beat"""
        if not self.musica_activa:
            return False

        tiempo_actual = time.time()
        if tiempo_actual - self.last_beat_time >= self.beat_interval:
            self.last_beat_time = tiempo_actual
            self.beat_count += 1
            self.total_beats += 1

            # Reproducir sonido
            if self.beat_count % 4 == 1:  # Acento cada 4 beats
                self.beat_acento.play()
            else:
                self.beat_principal.play()

            return True
        return False

    def verificar_sincronizacion(self, hay_movimiento):
        """
        Verifica si el usuario está siguiendo el ritmo
        Returns: (en_sincronizacion, perdio_ritmo)
        """
        tiempo_actual = time.time()
        tiempo_desde_ultimo_beat = tiempo_actual - self.last_beat_time
        tiempo_hasta_proximo_beat = self.beat_interval - tiempo_desde_ultimo_beat

        # Calcular si estamos en la "ventana de sincronización"
        en_ventana = (
            tiempo_desde_ultimo_beat <= self.ventana_sincronizacion
            or tiempo_hasta_proximo_beat <= self.ventana_sincronizacion
        )

        if hay_movimiento:
            self.ultimo_movimiento_tiempo = tiempo_actual

            if en_ventana:
                # ¡Movimiento sincronizado con el beat!
                self.beats_perdidos_consecutivos = 0
                self.beats_acertados += 1
                return True, False
            else:
                # Movimiento fuera de ritmo
                self.beats_perdidos_consecutivos += 1
                return (
                    False,
                    self.beats_perdidos_consecutivos >= self.max_beats_perdidos,
                )

        # Si no hay movimiento cerca de un beat, también cuenta como perdido
        if (
            en_ventana
            and (tiempo_actual - self.ultimo_movimiento_tiempo) > self.beat_interval
        ):
            self.beats_perdidos_consecutivos += 1
            return False, self.beats_perdidos_consecutivos >= self.max_beats_perdidos

        return False, False

    def reproducir_exito(self):
        """Reproduce sonido de éxito al completar patrón"""
        self.beat_exito.play()

    def reproducir_error(self):
        """Reproduce sonido de error al perder el ritmo"""
        self.beat_error.play()

    def cambiar_bpm(self, nuevo_bpm):
        """Cambia la velocidad del ritmo"""
        self.bpm = max(60, min(120, nuevo_bpm))  # Entre 60 y 120 BPM
        self.beat_interval = 60.0 / self.bpm
        self.tiempo_por_patron = self.beats_por_patron * self.beat_interval

    def activar_musica(self):
        """Activa la música"""
        self.musica_activa = True
        self.last_beat_time = time.time()

    def desactivar_musica(self):
        """Desactiva la música"""
        self.musica_activa = False
        pygame.mixer.stop()

    def cambiar_volumen(self, volumen):
        """Cambia el volumen (0.0 a 1.0)"""
        self.volumen = max(0.0, min(1.0, volumen))
        self.beat_principal.set_volume(self.volumen)
        self.beat_acento.set_volume(self.volumen * 1.2)
        self.beat_exito.set_volume(self.volumen)
        self.beat_error.set_volume(self.volumen * 0.8)

    def obtener_progreso_beat(self):
        """Devuelve el progreso del beat actual (0.0 a 1.0)"""
        tiempo_transcurrido = time.time() - self.last_beat_time
        return min(1.0, tiempo_transcurrido / self.beat_interval)

    def esta_en_ventana_sincronizacion(self):
        """Verifica si estamos en la ventana de sincronización"""
        tiempo_actual = time.time()
        tiempo_desde_ultimo_beat = tiempo_actual - self.last_beat_time
        tiempo_hasta_proximo_beat = self.beat_interval - tiempo_desde_ultimo_beat

        return (
            tiempo_desde_ultimo_beat <= self.ventana_sincronizacion
            or tiempo_hasta_proximo_beat <= self.ventana_sincronizacion
        )

    def reiniciar_beat(self):
        """Reinicia el contador de beats"""
        self.beat_count = 0
        self.last_beat_time = time.time()
        self.tiempo_inicio_compas = time.time()
        self.beats_perdidos_consecutivos = 0
        self.ultimo_movimiento_tiempo = time.time()

    def es_momento_de_nuevo_patron(self):
        """Verifica si es momento de generar un nuevo patrón según el ritmo"""
        tiempo_transcurrido = time.time() - self.tiempo_inicio_compas
        return tiempo_transcurrido >= self.tiempo_por_patron

    def obtener_tiempo_restante_patron(self):
        """Devuelve el tiempo restante para completar el patrón actual"""
        tiempo_transcurrido = time.time() - self.tiempo_inicio_compas
        return max(0, self.tiempo_por_patron - tiempo_transcurrido)

    def obtener_beats_restantes(self):
        """Devuelve cuántos beats faltan para completar el patrón"""
        return max(0, self.beats_por_patron - (self.beat_count % self.beats_por_patron))

    def reiniciar_compas(self):
        """Reinicia el compás para un nuevo patrón"""
        self.tiempo_inicio_compas = time.time()
        self.beat_count = 0
        self.beats_perdidos_consecutivos = 0
        self.ultimo_movimiento_tiempo = time.time()

    def obtener_precision_ritmo(self):
        """Devuelve la precisión del ritmo (0-100%)"""
        if self.total_beats == 0:
            return 100
        return int((self.beats_acertados / self.total_beats) * 100)

    def reiniciar_estadisticas(self):
        """Reinicia las estadísticas de ritmo"""
        self.total_beats = 0
        self.beats_acertados = 0
