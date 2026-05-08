
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from views.menu_principal import MenuPrincipal


def main():
    app = MenuPrincipal()
    app.ejecutar()


if __name__ == "__main__":
    main()
