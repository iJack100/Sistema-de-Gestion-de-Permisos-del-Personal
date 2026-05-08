import os
import functools


class Color:
    RESET    = "\033[0m"
    BOLD     = "\033[1m"
    ROJO     = "\033[31m"
    VERDE    = "\033[32m"
    AMARILLO = "\033[33m"
    AZUL     = "\033[34m"
    MAGENTA  = "\033[35m"
    CYAN     = "\033[36m"
    BLANCO   = "\033[37m"

    @staticmethod
    def texto(texto, color):
        return f"{color}{texto}{Color.RESET}"

    @staticmethod
    def titulo(texto, color=None):
        color = color or Color.CYAN
        return f"{Color.BOLD}{color}{texto}{Color.RESET}"



class Pantalla:

    @staticmethod
    def limpiar():
        os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def gotoxy(x, y):
        """Mueve el cursor a la posición (columna x, fila y)."""
        print(f"\033[{y};{x}H", end="", flush=True)

    @staticmethod
    def pausar():
        input(f"\n  {Color.texto('Presione ENTER para continuar...', Color.AMARILLO)}")

    @staticmethod
    def linea(caracter="─", ancho=50, color=None):
        return Color.texto(caracter * ancho, color or Color.AZUL)

    @staticmethod
    def encabezado(titulo, color=None):
        color = color or Color.CYAN
        ancho = 50
        Pantalla.limpiar()
        print(Color.texto("═" * ancho, color))
        print(Color.titulo(titulo.center(ancho), color))
        print(Color.texto("═" * ancho, color))



def decorador_interfaz(titulo: str):

    def wrapper(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            Pantalla.encabezado(titulo)
            return func(*args, **kwargs)
        return inner
    return wrapper


def manejar_errores(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            print(Color.texto(f"\n  ⚠  Error de valor: {e}", Color.ROJO))
        except FileNotFoundError as e:
            print(Color.texto(f"\n  ⚠  Error de archivo: {e}", Color.ROJO))
        except Exception as e:
            print(Color.texto(f"\n  ⚠  Error inesperado: {type(e).__name__} — {e}", Color.ROJO))
    return wrapper



def validar_cedula(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        cedula = kwargs.get("cedula") or (args[1] if len(args) > 1 else None)

        if cedula is not None:
            cedula = str(cedula).strip()

            if not cedula.isdigit() or len(cedula) != 10:
                print(Color.texto(
                    "\n  ⚠  Cédula inválida: debe tener exactamente 10 dígitos numéricos.",
                    Color.ROJO))
                return None

            provincia = int(cedula[:2])
            if provincia < 1 or provincia > 24:
                print(Color.texto(
                    f"\n  ⚠  Cédula inválida: provincia '{cedula[:2]}' no existe (rango 01-24).",
                    Color.ROJO))
                return None

            coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
            total = 0
            for i in range(9):
                val = int(cedula[i]) * coeficientes[i]
                if val >= 10:
                    val -= 9
                total += val

            digito_esperado = (10 - (total % 10)) % 10
            digito_real = int(cedula[9])

            if digito_esperado != digito_real:
                print(Color.texto(
                    f"\n  ⚠  Cédula inválida: dígito verificador incorrecto "
                    f"(esperado {digito_esperado}, recibido {digito_real}).",
                    Color.ROJO))
                return None

        return func(*args, **kwargs)

    return wrapper