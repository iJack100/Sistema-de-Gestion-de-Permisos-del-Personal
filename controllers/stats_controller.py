from core.decoradores import decorador_interfaz, Color, Pantalla
from core.mixins import CalculosMixin


class StatsController(CalculosMixin):


    def __init__(self, emp_ctrl, tp_ctrl, per_ctrl):
        self._emp = emp_ctrl
        self._tp  = tp_ctrl
        self._per = per_ctrl

    @decorador_interfaz("RESUMEN GENERAL DEL SISTEMA")
    def resumen_general(self):
        empleados = self._emp.todos()
        tipos     = self._tp.todos()
        permisos  = self._per.todos()

        print(Pantalla.linea("─", 50))
        print(Color.titulo("  TOTALES", Color.CYAN))
        print(Pantalla.linea("─", 50))
        print(f"  {Color.texto('Empleados registrados   :', Color.AMARILLO)} {len(empleados)}")
        print(f"  {Color.texto('Tipos de permiso        :', Color.AMARILLO)} {len(tipos)}")
        print(f"  {Color.texto('Permisos registrados    :', Color.AMARILLO)} {len(permisos)}")

        if empleados:

            emp_max = max(empleados, key=lambda e: e.sueldo)
            emp_min = min(empleados, key=lambda e: e.sueldo)
            prom    = round(sum(map(lambda e: e.sueldo, empleados)) / len(empleados), 2)

            print(Pantalla.linea("─", 50))
            print(Color.titulo("  SUELDOS", Color.CYAN))
            print(Pantalla.linea("─", 50))
            print(
                f"  {Color.texto('Mayor sueldo :', Color.VERDE)} "
                f"{emp_max.nombre:<25} {Color.texto(self.formatear_moneda(emp_max.sueldo), Color.VERDE)}"
            )
            print(
                f"  {Color.texto('Menor sueldo :', Color.AMARILLO)} "
                f"{emp_min.nombre:<25} {Color.texto(self.formatear_moneda(emp_min.sueldo), Color.AMARILLO)}"
            )
            print(
                f"  {Color.texto('Promedio     :', Color.CYAN)} "
                f"{Color.texto(self.formatear_moneda(prom), Color.CYAN)}"
            )

        if permisos:
            total_desc = sum(map(lambda p: p.descuento, permisos))

            per_max = max(permisos, key=lambda p: p.descuento)
            emp_per = self._emp.buscar_por_id(per_max.id_empleado)
            nombre_per = emp_per.nombre if emp_per else "Desconocido"

            print(Pantalla.linea("─", 50))
            print(Color.titulo("  DESCUENTOS", Color.CYAN))
            print(Pantalla.linea("─", 50))
            print(
                f"  {Color.texto('Total descontado :', Color.ROJO)} "
                f"{Color.texto(self.formatear_moneda(total_desc), Color.ROJO)}"
            )
            print(
                f"  {Color.texto('Mayor descuento  :', Color.AMARILLO)} "
                f"{nombre_per:<25} {Color.texto(self.formatear_moneda(per_max.descuento), Color.AMARILLO)}"
            )

        print(Pantalla.linea("─", 50))
        Pantalla.pausar()
