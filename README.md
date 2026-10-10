# Bloc de Notas Moderno (Python + PyQt6)

Una aplicación de bloc de notas moderna, limpia y minimalista, desarrollada en Python utilizando el framework PyQt6. Este proyecto implementa el patrón de arquitectura **Modelo-Vista-Controlador (MVC)**, garantizando un código modular, escalable y fácil de mantener.

La interfaz está fuertemente inspirada en las líneas de diseño del Bloc de Notas de Windows 11, añadiendo mejoras exclusivas en la experiencia de usuario, diseño UI/UX (modo oscuro dinámico, bordes redondeados, formato de texto) y herramientas para desarrolladores/escritores.

## 🚀 Características Principales

*   **Pestañas Múltiples:** Soporte para trabajar con varios documentos simultáneamente. Incluye un botón rápido `+` para nuevas pestañas.
*   **Modo Claro / Oscuro (Dinámico):** Alterna instantáneamente entre dos temas profesionales y elegantes utilizando un botón ovalado de diseño moderno ubicado en la barra de menús.
*   **Editor de Texto Enriquecido:** Soporte para texto con formato. Incluye herramientas para aplicar Negrita (B), Cursiva (I), Tachado (S), y diferentes niveles de Títulos (H1, H2, H3).
*   **Corrector Ortográfico Inteligente (Español):** Subrayado de palabras mal escritas en tiempo real y sugerencias de corrección directamente en el menú contextual.
*   **Numeración de Líneas Avanzada:** Un panel lateral integrado que muestra los números de línea y resalta visualmente la línea en la que se encuentra el cursor.
*   **Barra de Estado Inteligente:** Muestra estadísticas en tiempo real como el número total de palabras y la posición exacta del cursor (Línea y Columna).
*   **Buscar y Reemplazar:** Panel de búsqueda y reemplazo dinámico.
*   **Ajuste de Línea (Word Wrap):** Opción para alternar el ajuste automático de texto desde el menú Ver.
*   **Arquitectura MVC:** Código separado lógicamente en Modelo (datos y lógica de estado), Vista (interfaz gráfica) y Controlador (eventos y acciones).

## 🛠️ Tecnologías Utilizadas

*   **Lenguaje:** Python 3.10+
*   **Framework UI:** PyQt6
*   **Corrector Ortográfico:** pyspellchecker
*   **Estilos:** Qt Style Sheets (QSS) avanzados.

## 📂 Estructura del Proyecto

```text
BLOC DE NOTAS/
│
├── main.py                   # Punto de entrada de la aplicación
├── requirements.txt          # Dependencias (PyQt6)
├── README.md                 # Documentación del proyecto
│
└── app/
    ├── __init__.py
    ├── model.py              # Lógica de datos (manejo de archivos y estado de pestañas)
    ├── view.py               # Configuración de la UI (Menús, Barras, Layouts)
    ├── controller.py         # Intermediario (Eventos, atajos de teclado, interacciones)
    ├── editor_widget.py      # Widget personalizado (QTextEdit + Área de números de línea)
    │
    └── styles/
        ├── light.qss         # Hoja de estilos para el Tema Claro
        └── dark.qss          # Hoja de estilos para el Tema Oscuro
```

## ⚙️ Instalación y Uso

1. **Clonar o descargar** el repositorio.
2. **Crear un entorno virtual** (opcional pero recomendado):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # En Windows: .venv\Scripts\activate
   ```
3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Ejecutar la aplicación:**
   ```bash
   python main.py
   ```

## 🎨 Decisiones de Diseño (UI/UX)

- **Layout y QSS:** Se han ajustado al milímetro los espacios (`spacing`) y los márgenes de la barra de herramientas para asegurar compacidad.
- **Botón de Temas:** Emplazado en la Barra de Menú (esquina superior derecha) en forma de píldora (ovalado) para separar las acciones de formato de la aplicación.
- **Manejo de QTabBar:** Solución personalizada en QSS para asegurar que las pestañas inactivas se integren armónicamente tanto en modo oscuro como claro.
