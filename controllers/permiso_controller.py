import functools

from core.interfaces import ICrud
from core.mixins import CalculosMixin
from core.decoradores import decorador_interfaz, manejar_errores, Color, Pantalla
from core.json_manager import JsonManager
from models.permiso import Permiso


class PermisoController(ICrud, CalculosMixin):

    ARCHIVO = "permisos.json"

    def __init__(self, emp_ctrl, tp_ctrl):
        self._permisos: list[Permiso] = self._cargar()
        self._emp_ctrl = emp_ctrl
        self._tp_ctrl  = tp_ctrl


    def _cargar(self) -> list[Permiso]:
        return list(map(Permiso.from_dict, JsonManager.leer(self.ARCHIVO)))

    def _guardar(self) -> None:
        JsonManager.escribir(self.ARCHIVO, list(map(lambda p: p.to_dict(), self._permisos)))


    def todos(self) -> list[Permiso]:
        return self._permisos

    def buscar_por_id(self, per_id: int):
        return next((p for p in self._permisos if p.id == per_id), None)

    def siguiente_id(self) -> int:
        return max((p.id for p in self._permisos), default=0) + 1

    def eliminar_por_empleado(self, emp_id: int) -> None:
        self._permisos = list(filter(lambda p: p.id_empleado != emp_id, self._permisos))
        self._guardar()

    def eliminar_por_tipo(self, tp_id: int) -> None:
        self._permisos = list(filter(lambda p: p.id_tipo_permiso != tp_id, self._permisos))
        self._guardar()


    @decorador_interfaz("REGISTRO DE PERMISO")
    @manejar_errores
    def crear(self):
        nuevo_id = self.siguiente_id()
        Pantalla.gotoxy(2, 5)
        print(Color.texto(f"  ID asignado: {nuevo_id}", Color.AMARILLO))

        empleados = self._emp_ctrl.todos()
        if not empleados:
            print(Color.texto("  ⚠  No hay empleados registrados.", Color.ROJO))
            Pantalla.pausar()
            return

        print(Pantalla.linea("─", 55))
        print(Color.titulo("  EMPLEADOS DISPONIBLES", Color.CYAN))
        for e in empleados:
            print(f"  {Color.texto(f'ID {e.id:>3}', Color.AMARILLO)} | {e.nombre}")
        print(Pantalla.linea("─", 55))

        ids_emp_validos = tuple(str(e.id) for e in empleados)
        emp_id = self.pedir_entero(
            Color.texto("  ID Empleado     : ", Color.AMARILLO), "ID empleado")
        emp = self._emp_ctrl.buscar_por_id(emp_id)
        if not emp:
            print(Color.texto("  ⚠  Empleado no encontrado.", Color.ROJO))
            Pantalla.pausar()
            return

        tipos = self._tp_ctrl.todos()
        if not tipos:
            print(Color.texto("  ⚠  No hay tipos de permiso registrados.", Color.ROJO))
            Pantalla.pausar()
            return

        print(Pantalla.linea("─", 55))
        print(Color.titulo("  TIPOS DE PERMISO DISPONIBLES", Color.CYAN))
        for t in tipos:
            rem = Color.texto("Rem.", Color.VERDE) if t.remunerado == "S" \
                else Color.texto("No rem.", Color.AMARILLO)
            print(f"  {Color.texto(f'ID {t.id:>3}', Color.AMARILLO)} | {t.descripcion:<28} | {rem}")
        print(Pantalla.linea("─", 55))

        tp_id = self.pedir_entero(
            Color.texto("  ID Tipo Permiso : ", Color.AMARILLO), "ID tipo permiso")
        tp = self._tp_ctrl.buscar_por_id(tp_id)
        if not tp:
            print(Color.texto("  ⚠  Tipo de permiso no encontrado.", Color.ROJO))
            Pantalla.pausar()
            return

        f_desde_str, f_desde = self.pedir_fecha("  Fecha desde (DD/MM/YYYY) : ")

        while True:
            f_hasta_str, f_hasta = self.pedir_fecha("  Fecha hasta (DD/MM/YYYY) : ")
            if f_hasta >= f_desde:
                break
            print(Color.texto(
                "  ⚠  La fecha hasta no puede ser anterior a la fecha desde.", Color.ROJO))

        tipo = self.pedir_tipo_permiso("  Tipo (D=Días / H=Horas)  : ")

        tiempo = self.pedir_decimal(
            Color.texto("  Tiempo (cantidad)        : ", Color.AMARILLO), "tiempo")

        descuento = self.calcular_descuento(tipo, tiempo, emp.valor_hora, tp.remunerado)

        print(Pantalla.linea())
        print(Color.titulo("  RESUMEN DEL PERMISO", Color.CYAN))
        print(Pantalla.linea("─", 50))
        print(f"  Empleado       : {Color.texto(emp.nombre, Color.BLANCO)}")
        print(f"  Tipo permiso   : {Color.texto(tp.descripcion, Color.BLANCO)}")
        print(f"  Fecha desde    : {Color.texto(f_desde_str, Color.AMARILLO)}")
        print(f"  Fecha hasta    : {Color.texto(f_hasta_str, Color.AMARILLO)}")
        print(f"  Tipo           : {Color.texto('Días' if tipo == 'D' else 'Horas', Color.CYAN)}")
        print(f"  Tiempo         : {Color.texto(str(tiempo), Color.CYAN)}")
        print(f"  ¿Remunerado?   : {Color.texto(tp.remunerado, Color.VERDE if tp.remunerado == 'S' else Color.AMARILLO)}")
        print(f"  Descuento      : {Color.texto(self.formatear_moneda(descuento), Color.ROJO if descuento > 0 else Color.VERDE)}")
        print(Pantalla.linea())

        confirmacion = self.pedir_si_no(
            Color.texto("  ¿Confirmar? (S/N): ", Color.AMARILLO))
        if confirmacion == "S":
            permiso = Permiso(nuevo_id, emp_id, tp_id, f_desde_str, f_hasta_str, tipo, tiempo, descuento)
            self._permisos.append(permiso)
            self._guardar()
            print(Color.texto("  ✔  Permiso registrado correctamente.", Color.VERDE))
        else:
            print(Color.texto("  ✖  Registro cancelado.", Color.ROJO))

        Pantalla.pausar()


    @decorador_interfaz("CONSULTA DE PERMISOS")
    def consultar(self):
        if not self._permisos:
            print(Color.texto("  No hay permisos registrados.", Color.AMARILLO))
            Pantalla.pausar()
            return

        def detalle(p: Permiso) -> str:
            emp = self._emp_ctrl.buscar_por_id(p.id_empleado)
            tp  = self._tp_ctrl.buscar_por_id(p.id_tipo_permiso)
            nombre_emp = emp.nombre if emp else "Desconocido"
            desc_tp    = tp.descripcion if tp else "Desconocido"
            desc_color = Color.texto(self.formatear_moneda(p.descuento),
                                    Color.ROJO if p.descuento > 0 else Color.VERDE)
            return (
                f"  {Color.texto(f'ID {p.id}', Color.AMARILLO)}\n"
                f"    Empleado      : {Color.texto(nombre_emp, Color.BLANCO)}\n"
                f"    Tipo permiso  : {Color.texto(desc_tp, Color.CYAN)}\n"
                f"    Desde         : {p.fecha_desde}  →  Hasta: {p.fecha_hasta}\n"
                f"    Tipo / Tiempo : {p.tipo_label()} — {p.tiempo}\n"
                f"    Descuento     : {desc_color}"
            )

        lineas = list(map(detalle, self._permisos))
        for linea in lineas:
            print(linea)
            print(Pantalla.linea("─", 50))

        print(Color.texto(f"  Total permisos: {len(self._permisos)}", Color.CYAN))
        Pantalla.pausar()


    @decorador_interfaz("ELIMINAR PERMISO")
    @manejar_errores
    def eliminar(self):
        if not self._permisos:
            print(Color.texto("  No hay permisos registrados.", Color.AMARILLO))
            Pantalla.pausar()
            return

        self._listar_simple()
        per_id = self.pedir_entero(
            Color.texto("\n  ID del permiso a eliminar: ", Color.AMARILLO), "ID permiso")
        per = self.buscar_por_id(per_id)

        if not per:
            print(Color.texto("  ⚠  Permiso no encontrado.", Color.ROJO))
            Pantalla.pausar()
            return

        emp = self._emp_ctrl.buscar_por_id(per.id_empleado)
        nombre = emp.nombre if emp else "Desconocido"

        print(Pantalla.linea())
        print(f"  Permiso   : {Color.texto(f'ID {per.id}', Color.AMARILLO)}")
        print(f"  Empleado  : {Color.texto(nombre, Color.CYAN)}")
        print(f"  Desde     : {per.fecha_desde}  →  Hasta: {per.fecha_hasta}")
        print(f"  Descuento : {Color.texto(self.formatear_moneda(per.descuento), Color.ROJO)}")
        print(Pantalla.linea())

        confirmacion = self.pedir_si_no(
            Color.texto("  ¿Confirmar eliminación? (S/N): ", Color.ROJO))
        if confirmacion == "S":
            self._permisos = list(filter(lambda p: p.id != per_id, self._permisos))
            self._guardar()
            print(Color.texto("  ✔  Permiso eliminado correctamente.", Color.VERDE))

        Pantalla.pausar()


    @decorador_interfaz("ESTADÍSTICAS DE PERMISOS")
    def estadisticas(self):
        tipos    = self._tp_ctrl.todos()
        permisos = self._permisos

        if not permisos:
            print(Color.texto("  No hay permisos registrados.", Color.AMARILLO))
            Pantalla.pausar()
            return

        remunerados = list(filter(
            lambda p: next((t.remunerado for t in tipos if t.id == p.id_tipo_permiso), "N") == "S",
            permisos
        ))
        no_remunerados = list(filter(
            lambda p: next((t.remunerado for t in tipos if t.id == p.id_tipo_permiso), "N") == "N",
            permisos
        ))

        total_tiempo     = functools.reduce(lambda acc, p: acc + p.tiempo, permisos, 0.0)
        total_descuentos = sum(map(lambda p: p.descuento, permisos))

        print(Pantalla.linea("─", 50))
        print(f"  {Color.texto('Total permisos registrados   :', Color.CYAN)} {len(permisos)}")
        print(f"  {Color.texto('Permisos remunerados         :', Color.VERDE)} {len(remunerados)}")
        print(f"  {Color.texto('Permisos no remunerados      :', Color.AMARILLO)} {len(no_remunerados)}")
        print(f"  {Color.texto('Total tiempo solicitado      :', Color.CYAN)} {total_tiempo}")
        print(f"  {Color.texto('Monto total descontado       :', Color.ROJO)} {self.formatear_moneda(total_descuentos)}")
        print(Pantalla.linea("─", 50))
        Pantalla.pausar()


    def _listar_simple(self):
        print(Pantalla.linea("─", 60))
        for p in self._permisos:
            emp    = self._emp_ctrl.buscar_por_id(p.id_empleado)
            nombre = emp.nombre if emp else "Desconocido"
            print(
                f"  {Color.texto(f'ID {p.id:>3}', Color.AMARILLO)} | "
                f"{nombre:<25} | "
                f"{p.fecha_desde} → {p.fecha_hasta} | "
                f"{Color.texto(self.formatear_moneda(p.descuento), Color.ROJO)}"
            )
        print(Pantalla.linea("─", 60))


    @decorador_interfaz("BUSCAR PERMISO")
    @manejar_errores
    def buscar(self, id: int = None):
        if not self._permisos:
            print(Color.texto("  No hay permisos registrados.", Color.AMARILLO))
            Pantalla.pausar()
            return

        if id is None:
            self._listar_simple()
            id = self.pedir_entero(
                Color.texto("\n  ID del permiso a buscar: ", Color.AMARILLO), "ID")

        p = self.buscar_por_id(id)
        if not p:
            print(Color.texto("  ⚠  Permiso no encontrado.", Color.ROJO))
            Pantalla.pausar()
            return

        emp = self._emp_ctrl.buscar_por_id(p.id_empleado)
        tp  = self._tp_ctrl.buscar_por_id(p.id_tipo_permiso)
        nombre_emp = emp.nombre if emp else "Desconocido"
        desc_tp    = tp.descripcion if tp else "Desconocido"

        print(Pantalla.linea("─", 55))
        print(f"  {Color.texto('ID            :', Color.AMARILLO)} {p.id}")
        print(f"  {Color.texto('Empleado      :', Color.AMARILLO)} {nombre_emp}")
        print(f"  {Color.texto('Tipo permiso  :', Color.AMARILLO)} {desc_tp}")
        print(f"  {Color.texto('Desde         :', Color.AMARILLO)} {p.fecha_desde}")
        print(f"  {Color.texto('Hasta         :', Color.AMARILLO)} {p.fecha_hasta}")
        print(f"  {Color.texto('Tipo          :', Color.AMARILLO)} {p.tipo_label()}")
        print(f"  {Color.texto('Tiempo        :', Color.AMARILLO)} {p.tiempo}")
        print(f"  {Color.texto('Descuento     :', Color.AMARILLO)} {self.formatear_moneda(p.descuento)}")
        print(Pantalla.linea("─", 55))
        Pantalla.pausar()


    @decorador_interfaz("ACTUALIZAR PERMISO")
    @manejar_errores
    def actualizar(self, id: int = None):
        if not self._permisos:
            print(Color.texto("  No hay permisos registrados.", Color.AMARILLO))
            Pantalla.pausar()
            return

        self._listar_simple()
        if id is None:
            id = self.pedir_entero(
                Color.texto("\n  ID del permiso a actualizar: ", Color.AMARILLO), "ID")

        p = self.buscar_por_id(id)
        if not p:
            print(Color.texto("  ⚠  Permiso no encontrado.", Color.ROJO))
            Pantalla.pausar()
            return

        emp = self._emp_ctrl.buscar_por_id(p.id_empleado)
        tp  = self._tp_ctrl.buscar_por_id(p.id_tipo_permiso)

        print(Pantalla.linea())
        print(Color.texto("  Datos actuales:", Color.CYAN))
        print(f"  Fecha desde  : {p.fecha_desde}")
        print(f"  Fecha hasta  : {p.fecha_hasta}")
        print(f"  Tipo (D/H)   : {p.tipo}")
        print(f"  Tiempo       : {p.tiempo}")
        print(Pantalla.linea())
        print(Color.texto("  Ingrese nuevos datos (Enter para mantener el valor actual):", Color.AMARILLO))

        raw = input(f"  Fecha desde (DD/MM/YYYY)  [{p.fecha_desde}]: ").strip()
        if raw:
            nueva_f_desde_str, nueva_f_desde = self.pedir_fecha("  Fecha desde (DD/MM/YYYY): ") if not raw else \
                (raw, self.validar_fecha(raw))
            if not nueva_f_desde:
                print(Color.texto("  ⚠  Fecha inválida, se mantiene la anterior.", Color.ROJO))
                nueva_f_desde_str = p.fecha_desde
        else:
            nueva_f_desde_str = p.fecha_desde

        raw = input(f"  Fecha hasta (DD/MM/YYYY)  [{p.fecha_hasta}]: ").strip()
        if raw:
            nueva_f_hasta = self.validar_fecha(raw)
            if not nueva_f_hasta:
                print(Color.texto("  ⚠  Fecha inválida, se mantiene la anterior.", Color.ROJO))
                nueva_f_hasta_str = p.fecha_hasta
            else:
                nueva_f_hasta_str = raw
        else:
            nueva_f_hasta_str = p.fecha_hasta

        raw = input(f"  Tipo D/H  [{p.tipo}]: ").strip()
        nuevo_tipo = self.validar_tipo_permiso(raw) if raw else p.tipo

        raw = input(f"  Tiempo    [{p.tiempo}]: ").strip()
        nuevo_tiempo = self.validar_positivo(raw, "tiempo") if raw else p.tiempo

        nuevo_descuento = self.calcular_descuento(
            nuevo_tipo, nuevo_tiempo,
            emp.valor_hora if emp else 0,
            tp.remunerado  if tp  else "N"
        )

        print(Pantalla.linea())
        print(Color.titulo("  RESUMEN DE CAMBIOS", Color.CYAN))
        print(f"  Fecha desde  : {Color.texto(nueva_f_desde_str, Color.AMARILLO)}")
        print(f"  Fecha hasta  : {Color.texto(nueva_f_hasta_str, Color.AMARILLO)}")
        print(f"  Tipo         : {Color.texto(nuevo_tipo, Color.CYAN)}")
        print(f"  Tiempo       : {Color.texto(str(nuevo_tiempo), Color.CYAN)}")
        print(f"  Descuento    : {Color.texto(self.formatear_moneda(nuevo_descuento), Color.ROJO if nuevo_descuento > 0 else Color.VERDE)}")
        print(Pantalla.linea())

        confirmacion = self.pedir_si_no(Color.texto("  ¿Confirmar cambios? (S/N): ", Color.AMARILLO))
        if confirmacion == "S":
            p.fecha_desde = nueva_f_desde_str
            p.fecha_hasta = nueva_f_hasta_str
            p.tipo        = nuevo_tipo
            p.tiempo      = nuevo_tiempo
            p.descuento   = nuevo_descuento
            self._guardar()
            print(Color.texto("  ✔  Permiso actualizado correctamente.", Color.VERDE))
        else:
            print(Color.texto("  ✖  Actualización cancelada.", Color.ROJO))

        Pantalla.pausar()
