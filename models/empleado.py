class Empleado:

    def __init__(self, id: int, nombre: str, cedula: str, sueldo: float):
        self.id = id
        self.nombre = nombre.strip()
        self.cedula = str(cedula).strip()
        self.sueldo = round(float(sueldo), 2)
        self.valor_hora = round(self.sueldo / 240, 2)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "cedula": self.cedula,
            "sueldo": self.sueldo,
            "valor_hora": self.valor_hora,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Empleado":
        return cls(
            data["id"],
            data["nombre"],
            data.get("cedula", ""),   
            data["sueldo"]
        )

    def __str__(self) -> str:
        return (
            f"ID: {self.id:>3} | {self.nombre:<25} | "
            f"Cédula: {self.cedula} | "
            f"Sueldo: $ {self.sueldo:>9,.2f} | V/H: $ {self.valor_hora:>6.2f}"
        )
