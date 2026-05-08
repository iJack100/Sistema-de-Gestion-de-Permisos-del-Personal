class TipoPermiso:


    OPCIONES_VALIDAS = ("S", "N")

    def __init__(self, id: int, descripcion: str, remunerado: str):
        self.id = id
        self.descripcion = descripcion.strip()
        self.remunerado = remunerado.upper()
        if self.remunerado not in self.OPCIONES_VALIDAS:
            raise ValueError(
                f"El campo 'remunerado' debe ser S o N. Se recibió: '{remunerado}'"
            )


    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "descripcion": self.descripcion,
            "remunerado": self.remunerado,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TipoPermiso":
        return cls(data["id"], data["descripcion"], data["remunerado"])

    def __str__(self) -> str:
        etiqueta = "Remunerado" if self.remunerado == "S" else "No remunerado"
        return f"ID: {self.id:>3} | {self.descripcion:<30} | {etiqueta}"
