from core.interfaces import ICrud
from core.mixins import CalculosMixin
from core.decoradores import decorador_interfaz, manejar_errores, validar_cedula, Color, Pantalla
from core.json_manager import JsonManager
from models.empleado import Empleado


class EmpleadoController(ICrud, CalculosMixin):
    
    ARCHIVO = "empleados.json"

    def __init__(self):
        self._empleados: list[Empleado] = self._cargar()


    def _cargar(self) -> list[Empleado]:
        return list(map(Empleado.from_dict, JsonManager.leer(self.ARCHIVO)))

    def _guardar(self) -> None:
        JsonManager.escribir(self.ARCHIVO, list(map(lambda e: e.to_dict(), self._empleados)))


    def todos(self) -> list[Empleado]:
        return self._empleados

    def buscar_por_id(self, emp_id: int):
        return next((e for e in self._empleados if e.id == emp_id), None)

    def siguiente_id(self) -> int:
        return max((e.id for e in self._empleados), default=0) + 1


    @decorador_interfaz("REGISTRO DE EMPLEADO")
    @manejar_errores
    def crear(self):
        print(Color.texto("  Complete los datos del nuevo empleado:\n", Color.CYAN))

        nombre = self.pedir_nombre("  Nombre   : ")

        cedula = None
        while cedula is None:
            raw = input("  Cédula   : ").strip()
            if self._verificar_cedula(raw) is None:
                opcion = input(Color.texto("  ¿Intentar de nuevo? (S/N): ", Color.AMARILLO)).strip().upper()
                if opcion != "S":
                    print(Color.texto("\n  ✖  Registro cancelado.", Color.ROJO))
                    Pantalla.pausar()
                    return
            elif any(e.cedula == raw for e in self._empleados):
                print(Color.texto("  ⚠  Ya existe un empleado registrado con esa cédula.", Color.ROJO))
                opcion = input(Color.texto("  ¿Intentar de nuevo? (S/N): ", Color.AMARILLO)).strip().upper()
                if opcion != "S":
                    print(Color.texto("\n  ✖  Registro cancelado.", Color.ROJO))
                    Pantalla.pausar()
                    return
            else:
                print(Color.texto(f"  ✔  Cédula {raw} verificada correctamente.", Color.VERDE))
                cedula = raw  

        sueldo = self.pedir_sueldo("  Sueldo   : ")
        valor_hora = round(sueldo / 240, 2)

        print(Pantalla.linea())
        print(Color.texto("  RESUMEN DEL NUEVO EMPLEADO", Color.CYAN))
        print(Pantalla.linea())
        print(f"  Nombre    : {Color.texto(nombre, Color.BLANCO)}")
        print(f"  Cédula    : {Color.texto(cedula, Color.BLANCO)}")
        print(f"  Sueldo    : {Color.texto(self.formatear_moneda(sueldo), Color.VERDE)}")
        print(f"  V/Hora    : {Color.texto(self.formatear_moneda(valor_hora), Color.CYAN)}")
        print(Pantalla.linea())

        confirmacion = self.pedir_si_no(Color.texto("  ¿Desea guardar? (S/N): ", Color.AMARILLO))
        if confirmacion == "S":
            nuevo_id = self.siguiente_id()
            emp = Empleado(nuevo_id, nombre, cedula, sueldo)
            self._empleados.append(emp)
            self._guardar()
            print(Color.texto(f"\n  ✔  Empleado '{nombre}' guardado con éxito.", Color.VERDE))
        else:
            print(Color.texto("\n  ✖  Registro cancelado.", Color.ROJO))

        Pantalla.pausar()


    @validar_cedula
    def _verificar_cedula(self, cedula: str):
        return True


    @decorador_interfaz("LISTADO DE EMPLEADOS")
    def consultar(self):
        if not self._empleados:
            print(Color.texto("  (Sin registros)", Color.AMARILLO))
            Pantalla.pausar()
            return

        print(Pantalla.linea("─", 75))
        for emp in self._empleados:
            print(f"  {Color.texto(str(emp), Color.BLANCO)}")
        print(Pantalla.linea("─", 75))
        print(Color.texto(f"  Total empleados: {len(self._empleados)}", Color.CYAN))
        Pantalla.pausar()


    @decorador_interfaz("ELIMINAR EMPLEADO")
    @manejar_errores
    def eliminar(self):
        if not self._empleados:
            print(Color.texto("  No hay empleados registrados.", Color.AMARILLO))
            Pantalla.pausar()
            return

        self._listar_simple()
        emp_id = self.pedir_entero(
            Color.texto("\n  ID del empleado a eliminar: ", Color.AMARILLO), "ID")
        emp = self.buscar_por_id(emp_id)

        if not emp:
            print(Color.texto("  ⚠  Empleado no encontrado.", Color.ROJO))
            Pantalla.pausar()
            return

        print(Pantalla.linea())
        print(f"  Empleado  : {Color.texto(emp.nombre, Color.CYAN)}")
        print(f"  Cédula    : {emp.cedula}")
        print(f"  Sueldo    : {Color.texto(self.formatear_moneda(emp.sueldo), Color.VERDE)}")
        print(Pantalla.linea())

        confirmacion = self.pedir_si_no(
            Color.texto("  ¿Confirmar eliminación? (S/N): ", Color.ROJO))
        if confirmacion == "S":
            self._empleados = list(filter(lambda e: e.id != emp_id, self._empleados))
            self._guardar()
            print(Color.texto("\n  ✔  Empleado eliminado.", Color.VERDE))
            Pantalla.pausar()
            return emp_id

        Pantalla.pausar()
        return None

    def eliminar_por_id(self, emp_id: int) -> None:
        self._empleados = list(filter(lambda e: e.id != emp_id, self._empleados))
        self._guardar()

    def _listar_simple(self):
        print(Pantalla.linea())
        for emp in self._empleados:
            print(
                f"  {Color.texto(f'ID {emp.id:>3}', Color.AMARILLO)} | "
                f"{emp.nombre:<25} | {emp.cedula}"
            )
        print(Pantalla.linea())


    @decorador_interfaz("BUSCAR EMPLEADO")
    @manejar_errores
    def buscar(self, id: int = None):
        if not self._empleados:
            print(Color.texto("  No hay empleados registrados.", Color.AMARILLO))
            Pantalla.pausar()
            return

        if id is None:
            self._listar_simple()
            id = self.pedir_entero(
                Color.texto("\n  ID del empleado a buscar: ", Color.AMARILLO), "ID")

        emp = self.buscar_por_id(id)
        if not emp:
            print(Color.texto("  ⚠  Empleado no encontrado.", Color.ROJO))
            Pantalla.pausar()
            return

        print(Pantalla.linea("─", 60))
        print(f"  {Color.texto('ID      :', Color.AMARILLO)} {emp.id}")
        print(f"  {Color.texto('Nombre  :', Color.AMARILLO)} {emp.nombre}")
        print(f"  {Color.texto('Cédula  :', Color.AMARILLO)} {emp.cedula}")
        print(f"  {Color.texto('Sueldo  :', Color.AMARILLO)} {self.formatear_moneda(emp.sueldo)}")
        print(f"  {Color.texto('V/Hora  :', Color.AMARILLO)} {self.formatear_moneda(emp.valor_hora)}")
        print(Pantalla.linea("─", 60))
        Pantalla.pausar()


    @decorador_interfaz("ACTUALIZAR EMPLEADO")
    @manejar_errores
    def actualizar(self, id: int = None):
        if not self._empleados:
            print(Color.texto("  No hay empleados registrados.", Color.AMARILLO))
            Pantalla.pausar()
            return

        self._listar_simple()
        if id is None:
            id = self.pedir_entero(
                Color.texto("\n  ID del empleado a actualizar: ", Color.AMARILLO), "ID")

        emp = self.buscar_por_id(id)
        if not emp:
            print(Color.texto("  ⚠  Empleado no encontrado.", Color.ROJO))
            Pantalla.pausar()
            return

        print(Pantalla.linea())
        print(Color.texto("  Datos actuales:", Color.CYAN))
        print(f"  Nombre  : {emp.nombre}")
        print(f"  Cédula  : {emp.cedula}")
        print(f"  Sueldo  : {self.formatear_moneda(emp.sueldo)}")
        print(Pantalla.linea())
        print(Color.texto("  Ingrese nuevos datos (Enter para mantener el valor actual):\n", Color.AMARILLO))

        raw_nombre = input(f"  Nombre   [{emp.nombre}]: ").strip()
        nuevo_nombre = self.validar_solo_letras(raw_nombre, "nombre") if raw_nombre else emp.nombre

        nueva_cedula = emp.cedula
        raw_cedula = input(f"  Cédula   [{emp.cedula}]: ").strip()
        if raw_cedula:
            resultado = self._verificar_cedula(raw_cedula)
            if resultado is True:
                if any(e.cedula == raw_cedula and e.id != emp.id for e in self._empleados):
                    print(Color.texto("  ⚠  Esa cédula ya pertenece a otro empleado, se mantiene la anterior.", Color.ROJO))
                else:
                    nueva_cedula = raw_cedula
            else:
                print(Color.texto("  ⚠  Cédula inválida, se mantiene la anterior.", Color.ROJO))

        raw_sueldo = input(f"  Sueldo   [{emp.sueldo}]: ").strip()
        nuevo_sueldo = self.validar_positivo(raw_sueldo, "sueldo") if raw_sueldo else emp.sueldo
        nuevo_valor_hora = round(nuevo_sueldo / 240, 2)

        print(Pantalla.linea())
        print(Color.texto("  RESUMEN DE CAMBIOS", Color.CYAN))
        print(Pantalla.linea())
        print(f"  Nombre  : {Color.texto(nuevo_nombre, Color.BLANCO)}")
        print(f"  Cédula  : {Color.texto(nueva_cedula, Color.BLANCO)}")
        print(f"  Sueldo  : {Color.texto(self.formatear_moneda(nuevo_sueldo), Color.VERDE)}")
        print(f"  V/Hora  : {Color.texto(self.formatear_moneda(nuevo_valor_hora), Color.CYAN)}")
        print(Pantalla.linea())

        confirmacion = self.pedir_si_no(Color.texto("  ¿Confirmar cambios? (S/N): ", Color.AMARILLO))
        if confirmacion == "S":
            emp.nombre     = nuevo_nombre
            emp.cedula     = nueva_cedula
            emp.sueldo     = nuevo_sueldo
            emp.valor_hora = nuevo_valor_hora
            self._guardar()
            print(Color.texto("\n  ✔  Empleado actualizado correctamente.", Color.VERDE))
        else:
            print(Color.texto("\n  ✖  Actualización cancelada.", Color.ROJO))

        Pantalla.pausar()