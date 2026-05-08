from core.interfaces import ICrud
from core.mixins import CalculosMixin
from core.decoradores import decorador_interfaz, manejar_errores, Color, Pantalla
from core.json_manager import JsonManager
from models.tipo_permiso import TipoPermiso


class TipoPermisoController(ICrud, CalculosMixin):

    ARCHIVO = "tipos_permisos.json"

    def __init__(self):
        self._tipos: list[TipoPermiso] = self._cargar()


    def _cargar(self) -> list[TipoPermiso]:
        return list(map(TipoPermiso.from_dict, JsonManager.leer(self.ARCHIVO)))

    def _guardar(self) -> None:
        JsonManager.escribir(self.ARCHIVO, list(map(lambda t: t.to_dict(), self._tipos)))


    def todos(self) -> list[TipoPermiso]:
        return self._tipos

    def buscar_por_id(self, tp_id: int):
        return next((t for t in self._tipos if t.id == tp_id), None)

    def siguiente_id(self) -> int:
        return max((t.id for t in self._tipos), default=0) + 1


    @decorador_interfaz("REGISTRO DE TIPO DE PERMISO")
    @manejar_errores
    def crear(self):
        nuevo_id = self.siguiente_id()
        Pantalla.gotoxy(2, 5)
        print(Color.texto(f"  ID asignado: {nuevo_id}", Color.AMARILLO))

        descripcion = self.pedir_descripcion("  Descripción        : ")

        remunerado = self.pedir_si_no(
            Color.texto("  ¿Remunerado? (S/N) : ", Color.AMARILLO))

        etiqueta = Color.texto("Remunerado", Color.VERDE) if remunerado == "S" \
                   else Color.texto("No remunerado (genera descuento)", Color.AMARILLO)

        print(Pantalla.linea())
        print(f"  Descripción  : {Color.texto(descripcion, Color.CYAN)}")
        print(f"  Tipo         : {etiqueta}")
        print(Pantalla.linea())

        confirmacion = self.pedir_si_no(
            Color.texto("  ¿Guardar? (S/N): ", Color.AMARILLO))
        if confirmacion == "S":
            tp = TipoPermiso(nuevo_id, descripcion, remunerado)
            self._tipos.append(tp)
            self._guardar()
            print(Color.texto(f"  ✔  Tipo de permiso '{descripcion}' registrado.", Color.VERDE))
        else:
            print(Color.texto("  ✖  Registro cancelado.", Color.ROJO))

        Pantalla.pausar()

    @decorador_interfaz("TIPOS DE PERMISO")
    def consultar(self):
        if not self._tipos:
            print(Color.texto("  (Sin registros)", Color.AMARILLO))
            Pantalla.pausar()
            return

        print(Pantalla.linea("─", 55))
        for tp in self._tipos:
            etiqueta = Color.texto("Remunerado    ", Color.VERDE) if tp.remunerado == "S" \
                       else Color.texto("No remunerado", Color.AMARILLO)
            print(
                f"  {Color.texto(f'ID {tp.id:>3}', Color.AMARILLO)} | "
                f"{tp.descripcion:<30} | {etiqueta}"
            )
        print(Pantalla.linea("─", 55))
        print(Color.texto(f"  Total tipos: {len(self._tipos)}", Color.CYAN))
        Pantalla.pausar()


    @decorador_interfaz("ELIMINAR TIPO DE PERMISO")
    @manejar_errores
    def eliminar(self):
        if not self._tipos:
            print(Color.texto("  No hay tipos de permiso registrados.", Color.AMARILLO))
            Pantalla.pausar()
            return

        self._listar_simple()
        tp_id = self.pedir_entero(
            Color.texto("\n  ID del tipo a eliminar: ", Color.AMARILLO), "ID")
        tp = self.buscar_por_id(tp_id)

        if not tp:
            print(Color.texto("  ⚠  Tipo de permiso no encontrado.", Color.ROJO))
            Pantalla.pausar()
            return

        print(Pantalla.linea())
        print(f"  Descripción  : {Color.texto(tp.descripcion, Color.CYAN)}")
        print(f"  Remunerado   : {Color.texto(tp.remunerado, Color.AMARILLO)}")
        print(Pantalla.linea())

        confirmacion = self.pedir_si_no(
            Color.texto("  ¿Confirmar eliminación? (S/N): ", Color.ROJO))
        if confirmacion == "S":
            self._tipos = list(filter(lambda t: t.id != tp_id, self._tipos))
            self._guardar()
            print(Color.texto("  ✔  Tipo de permiso eliminado.", Color.VERDE))
            Pantalla.pausar()
            return tp_id

        Pantalla.pausar()
        return None

    def eliminar_por_id(self, tp_id: int) -> None:
        self._tipos = list(filter(lambda t: t.id != tp_id, self._tipos))
        self._guardar()

    def _listar_simple(self):
        print(Pantalla.linea())
        for tp in self._tipos:
            etiqueta = "Rem." if tp.remunerado == "S" else "No rem."
            print(
                f"  {Color.texto(f'ID {tp.id:>3}', Color.AMARILLO)} | "
                f"{tp.descripcion:<30} | {Color.texto(etiqueta, Color.CYAN)}"
            )
        print(Pantalla.linea())


    @decorador_interfaz("BUSCAR TIPO DE PERMISO")
    @manejar_errores
    def buscar(self, id: int = None):
        if not self._tipos:
            print(Color.texto("  No hay tipos de permiso registrados.", Color.AMARILLO))
            Pantalla.pausar()
            return

        if id is None:
            self._listar_simple()
            id = self.pedir_entero(
                Color.texto("\n  ID del tipo a buscar: ", Color.AMARILLO), "ID")

        tp = self.buscar_por_id(id)
        if not tp:
            print(Color.texto("  ⚠  Tipo de permiso no encontrado.", Color.ROJO))
            Pantalla.pausar()
            return

        etiqueta = Color.texto("Remunerado", Color.VERDE) if tp.remunerado == "S" \
                   else Color.texto("No remunerado (genera descuento)", Color.AMARILLO)
        print(Pantalla.linea("─", 55))
        print(f"  {Color.texto('ID          :', Color.AMARILLO)} {tp.id}")
        print(f"  {Color.texto('Descripción :', Color.AMARILLO)} {tp.descripcion}")
        print(f"  {Color.texto('Tipo        :', Color.AMARILLO)} {etiqueta}")
        print(Pantalla.linea("─", 55))
        Pantalla.pausar()


    @decorador_interfaz("ACTUALIZAR TIPO DE PERMISO")
    @manejar_errores
    def actualizar(self, id: int = None):
        if not self._tipos:
            print(Color.texto("  No hay tipos de permiso registrados.", Color.AMARILLO))
            Pantalla.pausar()
            return

        self._listar_simple()
        if id is None:
            id = self.pedir_entero(
                Color.texto("\n  ID del tipo a actualizar: ", Color.AMARILLO), "ID")

        tp = self.buscar_por_id(id)
        if not tp:
            print(Color.texto("  ⚠  Tipo de permiso no encontrado.", Color.ROJO))
            Pantalla.pausar()
            return

        print(Pantalla.linea())
        print(Color.texto("  Datos actuales:", Color.CYAN))
        print(f"  Descripción  : {tp.descripcion}")
        print(f"  Remunerado   : {tp.remunerado}")
        print(Pantalla.linea())
        print(Color.texto("  Ingrese nuevos datos (Enter para mantener el valor actual):", Color.AMARILLO))

        raw_desc = input(f"  Descripción  [{tp.descripcion}]: ").strip()
        nueva_desc = self.validar_texto_general(raw_desc, "descripción") if raw_desc else tp.descripcion

        raw_rem = input(f"  ¿Remunerado? S/N  [{tp.remunerado}]: ").strip()
        nuevo_rem = self.validar_si_no(raw_rem) if raw_rem else tp.remunerado

        etiqueta = Color.texto("Remunerado", Color.VERDE) if nuevo_rem == "S" \
                   else Color.texto("No remunerado", Color.AMARILLO)

        print(Pantalla.linea())
        print(f"  Descripción  : {Color.texto(nueva_desc, Color.CYAN)}")
        print(f"  Tipo         : {etiqueta}")
        print(Pantalla.linea())

        confirmacion = self.pedir_si_no(Color.texto("  ¿Confirmar cambios? (S/N): ", Color.AMARILLO))
        if confirmacion == "S":
            tp.descripcion = nueva_desc
            tp.remunerado  = nuevo_rem
            self._guardar()
            print(Color.texto("  ✔  Tipo de permiso actualizado correctamente.", Color.VERDE))
        else:
            print(Color.texto("  ✖  Actualización cancelada.", Color.ROJO))

        Pantalla.pausar()


