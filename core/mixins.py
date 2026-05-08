import re
from datetime import datetime


class CalculosMixin:


    def validar_fecha(self, fecha_str: str):
        try:
            return datetime.strptime(fecha_str, "%d/%m/%Y")
        except ValueError:
            return None

    def calcular_descuento(self, tipo: str, tiempo: float, valor_hora: float, remunerado: str) -> float:
        if remunerado == "S":
            return 0.0
        factor = 8 if tipo == "D" else 1
        return round(float(tiempo) * factor * valor_hora, 2)

    def formatear_moneda(self, valor: float) -> str:
        return f"$ {valor:,.2f}"


    @staticmethod
    def validar_no_vacio(valor: str, campo: str) -> str:
        v = valor.strip()
        if not v:
            raise ValueError(f"El campo '{campo}' no puede estar vacío.")
        return v

    @staticmethod
    def validar_solo_letras(valor: str, campo: str) -> str:
        v = valor.strip()
        if not v:
            raise ValueError(f"El campo '{campo}' no puede estar vacío.")
        if not re.fullmatch(r"[A-Za-záéíóúÁÉÍÓÚüÜñÑ\s]+", v):
            raise ValueError(f"'{campo}' solo puede contener letras y espacios, sin números ni símbolos.")
        return v

    @staticmethod
    def validar_texto_general(valor: str, campo: str, min_len: int = 3) -> str:
        v = valor.strip()
        if not v:
            raise ValueError(f"El campo '{campo}' no puede estar vacío.")
        if len(v) < min_len:
            raise ValueError(f"'{campo}' debe tener al menos {min_len} caracteres.")
        if v.isdigit():
            raise ValueError(f"'{campo}' no puede ser solo números.")
        return v

    @staticmethod
    def validar_entero_positivo(valor: str, campo: str) -> int:
        v = valor.strip()
        if not v.isdigit():
            raise ValueError(f"'{campo}' debe ser un número entero positivo (sin decimales ni letras).")
        n = int(v)
        if n <= 0:
            raise ValueError(f"'{campo}' debe ser mayor a 0.")
        return n

    @staticmethod
    def validar_positivo(valor: str, campo: str) -> float:
        v = valor.strip().replace(",", ".")
        try:
            n = float(v)
        except ValueError:
            raise ValueError(f"'{campo}' debe ser un número válido (ej: 1200.50).")
        if n <= 0:
            raise ValueError(f"'{campo}' debe ser mayor a 0.")
        return n

    @staticmethod
    def validar_si_no(valor: str) -> str:
        v = valor.strip().upper()
        if v not in ("S", "N"):
            raise ValueError("Respuesta debe ser 'S' o 'N'.")
        return v

    @staticmethod
    def validar_tipo_permiso(valor: str) -> str:
        v = valor.strip().upper()
        if v not in ("D", "H"):
            raise ValueError("Tipo debe ser 'D' (días) o 'H' (horas).")
        return v

    @staticmethod
    def validar_opcion_menu(valor: str, opciones_validas: tuple) -> str:
        v = valor.strip()
        if v not in opciones_validas:
            raise ValueError(f"Opción inválida. Ingrese una de: {', '.join(opciones_validas)}")
        return v



    @staticmethod
    def _pedir(prompt: str, validador, color_prompt=None, color_error=None) -> object:

        from core.decoradores import Color
        cp = color_prompt or Color.BLANCO
        ce = color_error  or Color.ROJO
        while True:
            try:
                raw = input(f"{cp}{prompt}{Color.RESET}")
                return validador(raw)
            except (ValueError, TypeError) as e:
                print(Color.texto(f"  ⚠  {e}", ce))

    @classmethod
    def pedir_nombre(cls, prompt: str = "  Nombre       : ") -> str:
        return cls._pedir(prompt, lambda v: cls.validar_solo_letras(v, "nombre"))

    @classmethod
    def pedir_descripcion(cls, prompt: str = "  Descripción  : ") -> str:
        return cls._pedir(prompt, lambda v: cls.validar_texto_general(v, "descripción"))

    @classmethod
    def pedir_sueldo(cls, prompt: str = "  Sueldo       : ") -> float:
        return cls._pedir(prompt, lambda v: cls.validar_positivo(v, "sueldo"))

    @classmethod
    def pedir_entero(cls, prompt: str, campo: str = "valor") -> int:
        return cls._pedir(prompt, lambda v: cls.validar_entero_positivo(v, campo))

    @classmethod
    def pedir_decimal(cls, prompt: str, campo: str = "valor") -> float:
        return cls._pedir(prompt, lambda v: cls.validar_positivo(v, campo))

    @classmethod
    def pedir_si_no(cls, prompt: str) -> str:
        return cls._pedir(prompt, lambda v: cls.validar_si_no(v))

    @classmethod
    def pedir_tipo_permiso(cls, prompt: str = "  Tipo (D/H)   : ") -> str:
        return cls._pedir(prompt, lambda v: cls.validar_tipo_permiso(v))

    @classmethod
    def pedir_fecha(cls, prompt: str) -> tuple:

        from core.decoradores import Color

        def _validar_fecha(raw: str):
            raw = raw.strip()
            if not raw:
                raise ValueError("La fecha no puede estar vacía.")
 
            if not re.fullmatch(r"\d{2}/\d{2}/\d{4}", raw):
                raise ValueError("Formato inválido. Use DD/MM/YYYY (ej: 25/04/2025).")
            try:
                dt = datetime.strptime(raw, "%d/%m/%Y")
            except ValueError:
                raise ValueError("Fecha inexistente (ej: 30/02/2025 no existe).")
            return (raw, dt)

        return cls._pedir(prompt, _validar_fecha)
