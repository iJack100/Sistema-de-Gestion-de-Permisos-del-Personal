class Permiso:

    TIPOS_VALIDOS = ("D", "H")

    def __init__(
        self,
        id: int,
        id_empleado: int,
        id_tipo_permiso: int,
        fecha_desde: str,
        fecha_hasta: str,
        tipo: str,
        tiempo: float,
        descuento: float,
    ):
        self.id = id
        self.id_empleado = id_empleado
        self.id_tipo_permiso = id_tipo_permiso
        self.fecha_desde = fecha_desde
        self.fecha_hasta = fecha_hasta
        self.tipo = tipo.upper()
        if self.tipo not in self.TIPOS_VALIDOS:
            raise ValueError(f"El tipo debe ser D o H. Se recibió: '{tipo}'")
        self.tiempo = float(tiempo)
        self.descuento = round(float(descuento), 2)


    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "id_empleado": self.id_empleado,
            "id_tipo_permiso": self.id_tipo_permiso,
            "fecha_desde": self.fecha_desde,
            "fecha_hasta": self.fecha_hasta,
            "tipo": self.tipo,
            "tiempo": self.tiempo,
            "descuento": self.descuento,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Permiso":
        return cls(
            data["id"],
            data["id_empleado"],
            data["id_tipo_permiso"],
            data["fecha_desde"],
            data["fecha_hasta"],
            data["tipo"],
            data["tiempo"],
            data["descuento"],
        )

    def tipo_label(self) -> str:
        return "Días" if self.tipo == "D" else "Horas"

    def __str__(self) -> str:
        return (
            f"ID: {self.id:>3} | Emp: {self.id_empleado} | "
            f"Desde: {self.fecha_desde} → Hasta: {self.fecha_hasta} | "
            f"{self.tipo_label()}: {self.tiempo} | Descuento: $ {self.descuento:,.2f}"
        )
