

# Music Therapy

## Descripción del Proyecto

**Music Therapy** es una aplicación interactiva desarrollada en **Python** que combina música, visión por computadora y gamificación para asistir en terapias de rehabilitación motora, especialmente de las **extremidades superiores**.

El sistema permite al usuario realizar movimientos rítmicos con las manos siguiendo patrones visuales sincronizados con la música, fomentando una experiencia **didáctica, motivadora y terapéutica**.

---

## Propósito

El objetivo del proyecto es hacer que las terapias de rehabilitación sean más **entretenidas y accesibles**, reduciendo la monotonía de los ejercicios tradicionales mediante un enfoque lúdico y musical. No reemplaza la terapia profesional, sino que actúa como una **herramienta complementaria** para uso en casa.

---

## Integrantes

* **Betanzos Rosas Taylor Anthony**
* **García Valdivia Ronald Pablo**
* **Zapana Romero Pedro Luis Christian**

Docente asesor: **Mg. Diego Alonso Iquira Becerra**
Universidad Nacional de San Agustín – Escuela Profesional de Ingeniería de Sistemas
Curso: *Construcción de Software* (2025B)

---

## Arquitectura del Sistema

El proyecto está estructurado bajo el patrón **MVC (Modelo–Vista–Controlador)**:

* **Modelo:** Gestión de puntajes, sesiones y configuraciones del usuario.
* **Vista:** Interfaz visual creada con *Pygame*, donde se muestran los patrones musicales, menús y retroalimentación.
* **Controlador:** Procesa la detección de movimientos usando *OpenCV* y *MediaPipe*, interpretando gestos en tiempo real.

---

## Tecnologías y Herramientas

| Herramienta      | Descripción                                       |
| ---------------- | ------------------------------------------------- |
| **Python**       | Lenguaje principal de desarrollo                  |
| **OpenCV**       | Captura y procesamiento de video en tiempo real   |
| **MediaPipe**    | Detección y seguimiento de manos                  |
| **CVZone**       | Simplificación de detección de gestos             |
| **Pygame**       | Creación del entorno visual y musical del juego   |
| **GitHub**       | Control de versiones y colaboración               |
| **Jira / Canva** | Planificación de tareas y cronograma del proyecto |

---

## Instalación y Ejecución

### Requisitos previos

* Python 3.8 - 3.11
* Cámara web (o cámara IP)
* Paquetes:

  ```bash
  pip install opencv-python mediapipe pygame cvzone
  ```

### ▶️ Ejecución

1. Clona el repositorio:

   ```bash
   git clone https://github.com/TAYTOS/Music-therapy.git
   ```
2. Accede al directorio:

   ```bash
   cd Music-therapy
   ```
3. Ejecuta el programa principal:

   ```bash
   python controlador.py
   ```
4. Usa tu mano frente a la cámara y sigue los patrones musicales en pantalla.

---

## Funcionalidades Principales

* Detección de gestos de mano (puño cerrado, direcciones).
* Movimientos sincronizados con canciones de fondo.
* Cálculo de puntajes según precisión y ritmo.
* Interfaz visual intuitiva y colorida.
* Registro y visualización de puntajes anteriores.
* Posibilidad de pausar/reanudar sesiones.

---

## Usuarios Objetivo

Dirigido principalmente a:

* Pacientes con limitaciones motoras en miembros superiores.
* Niños y adolescentes con parálisis cerebral u otras lesiones neurológicas.
* Personas que buscan realizar terapias de movimiento de forma autónoma y divertida.

---

## Metodología de Desarrollo

* **Modelo Cascada:** para la planificación y definición de requisitos.
* **Kanban:** para la gestión ágil de avances semanales y entregas parciales.


---

## Resultados Esperados

* Baja latencia en detección de movimientos.
* Alta precisión en el reconocimiento de gestos.
* Experiencia interactiva, fluida y motivadora.
* Interfaz accesible y amigable para todo tipo de usuarios.

---

## Enlaces Relacionados

* **Repositorio:** [https://github.com/TAYTOS/Music-therapy](https://github.com/TAYTOS/Music-therapy)
* **Cronograma:** [Canva](https://www.canva.com/design/DAG0fDDCsE0/29IcpZ8O6aRdz1swFk9VYQ/edit?locale=es-CO)
* **Jira Board:** [Ver tablero](https://unsa-team-esiyms20.atlassian.net/jira/software/projects/SCRUM/boards/1/backlog)

---
