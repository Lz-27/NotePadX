import sys
from PyQt6.QtWidgets import QApplication
from app.model import EditorModel
from app.view import EditorView
from app.controller import EditorController

"""
Punto de entrada principal para el Bloc de Notas Moderno.
Inicializa la aplicación y configura la arquitectura Modelo-Vista-Controlador.
"""

def main():
    """Inicializa y ejecuta la aplicación PyQt6."""
    app = QApplication(sys.argv)
    
    # MVC Setup
    model = EditorModel()
    view = EditorView()
    controller = EditorController(model, view)
    
    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()