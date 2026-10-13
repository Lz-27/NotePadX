# ==============================================================================
# Dockerfile - NotepadX (PyQt6 Desktop Application)
# ==============================================================================

# Imagen base optimizada con Python 3.11 sobre Debian Bookworm Slim
FROM python:3.11-slim-bookworm

# Variables de entorno para ejecución óptima de Python y Qt
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    QT_X11_NO_MITSHM=1 \
    DISPLAY=:0

# Instalación de dependencias del sistema requeridas por PyQt6 (X11 / XCB y OpenGL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libegl1 \
    libxkbcommon-x11-0 \
    libdbus-1-3 \
    libglib2.0-0 \
    libfontconfig1 \
    libxrender1 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxi6 \
    libxtst6 \
    libxrandr2 \
    libxcursor1 \
    libsm6 \
    libice6 \
    libxcb1 \
    libxcb-cursor0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-sync1 \
    libxcb-xfixes0 \
    libxcb-xinerama0 \
    libxcb-xkb1 \
    && rm -rf /var/lib/apt/lists/*

# Creación de usuario no root para seguridad y compatibilidad con X11
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -m -s /bin/bash appuser

# Directorio de trabajo
WORKDIR /app

# Copia e instalación de dependencias primero para aprovechar la caché de capas de Docker
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia del código fuente del proyecto
COPY . /app

# Asignación de permisos al usuario no root
RUN chown -R appuser:appuser /app

# Cambiar a usuario no root
USER appuser

# Comando de ejecución por defecto
CMD ["python", "main.py"]
