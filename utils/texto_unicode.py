import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


class TextoUnicode:
    """Clase para dibujar texto con caracteres Unicode (ñ, tildes, etc.) en OpenCV"""

    def __init__(self):
        # Intentar cargar fuente del sistema, si no existe usar fuente por defecto
        try:
            # Windows
            self.font_path = "C:/Windows/Fonts/arial.ttf"
            self.font_bold_path = "C:/Windows/Fonts/arialbd.ttf"
        except:
            try:
                # Linux
                self.font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
                self.font_bold_path = (
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
                )
            except:
                # Si no encuentra fuentes, usar por defecto
                self.font_path = None
                self.font_bold_path = None

    def put_text(
        self,
        frame,
        texto,
        posicion,
        tamano=30,
        color=(255, 255, 255),
        grosor=1,
        negrita=False,
    ):
        """
        Dibuja texto con soporte Unicode en un frame de OpenCV

        Args:
            frame: Frame de OpenCV (numpy array)
            texto: Texto a dibujar (str con soporte Unicode)
            posicion: Tupla (x, y) con la posición
            tamano: Tamaño de la fuente
            color: Color BGR como tupla (B, G, R)
            grosor: Grosor simulado (1=normal, 2=más grueso)
            negrita: Si usar fuente en negrita
        """
        # Convertir frame a PIL Image
        img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)

        # Cargar fuente
        try:
            font_path = self.font_bold_path if negrita else self.font_path
            if font_path:
                font = ImageFont.truetype(font_path, tamano)
            else:
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()

        # Convertir color de BGR a RGB
        color_rgb = (color[2], color[1], color[0])

        # Dibujar texto (con efecto de grosor si se especifica)
        x, y = posicion
        if grosor > 1:
            # Simular grosor dibujando varias veces con offset
            offsets = [
                (-1, -1),
                (-1, 0),
                (-1, 1),
                (0, -1),
                (0, 1),
                (1, -1),
                (1, 0),
                (1, 1),
            ]
            for offset_x, offset_y in offsets:
                draw.text(
                    (x + offset_x, y + offset_y), texto, font=font, fill=color_rgb
                )

        # Dibujar texto principal
        draw.text((x, y), texto, font=font, fill=color_rgb)

        # Convertir de vuelta a OpenCV
        frame_resultado = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

        # Copiar el resultado al frame original
        frame[:] = frame_resultado[:]

        return frame
