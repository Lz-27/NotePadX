from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QMenuBar, QMenu, 
    QToolBar, QPushButton, QStatusBar, QTabWidget, QLineEdit, QLabel, 
    QComboBox, QFontComboBox, QSpinBox, QSplitter, QTextEdit
)
from PyQt6.QtGui import QAction, QIcon, QFont, QTextCharFormat, QColor
from PyQt6.QtCore import Qt
#from app.editor_widget import CustomTextEdit

class EditorView(QMainWindow):
    """
    Define y construye la interfaz gráfica de usuario (GUI) del Bloc de Notas.
    Configura los componentes visuales como menús, barras de herramientas, editor y consola.
    """
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Bloc de Notas Moderno")
        self.resize(800, 600)
        
        # Base Layout
        self.central_widget = QWidget()
        self.central_widget.setObjectName("centralWidget")
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Find/Replace Bar (Hidden initially)
        self._setup_find_replace_bar()
        
        self.tabs = QTabWidget()
        self.tabs.setObjectName("mainTabs")
        self.tabs.setTabsClosable(True)
        self.tabs.setDocumentMode(True) # Modern look
        
        # New Tab Button in Corner
        from PyQt6.QtWidgets import QToolButton
        self.btn_add_tab = QToolButton()
        self.btn_add_tab.setText("+")
        self.btn_add_tab.setObjectName("addTabBtn")
        self.btn_add_tab.setToolTip("Nueva Pestaña")
        self.tabs.setCornerWidget(self.btn_add_tab, Qt.Corner.TopRightCorner)
        
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.tabs)
        
        self.binary_terminal = QTextEdit()
        self.binary_terminal.setObjectName("binaryTerminal")
        self.binary_terminal.hide()
        
        self.markdown_preview = QTextEdit()
        self.markdown_preview.setObjectName("markdownPreview")
        self.markdown_preview.setReadOnly(True)
        self.markdown_preview.hide()
        
        self.splitter.addWidget(self.binary_terminal)
        self.splitter.addWidget(self.markdown_preview)
        self.main_layout.addWidget(self.splitter)
        
        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Labels for live stats
        self.lbl_cursor_pos = QLabel("Ln 1, Col 1")
        self.lbl_word_count = QLabel("0 palabras")
        
        self.btn_info = QPushButton("Acerca de")
        self.btn_info.setObjectName("btnInfo")
        self.btn_info.setIcon(QIcon("app/icons/info.svg"))
        self.btn_info.setToolTip("Información del Proyecto")
        self.btn_info.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Add to the left side of the status bar
        self.status_bar.addWidget(self.btn_info)
        
        self.status_bar.addPermanentWidget(self.lbl_cursor_pos)
        self.status_bar.addPermanentWidget(self.lbl_word_count)
        
        # Menus & Toolbars setup
        self._setup_actions()
        self._setup_menu()
        self._setup_main_toolbar()
        
        # Theme Toggle Button (Pill button in top right of menuBar)
        self.btn_toggle_theme = QPushButton("Modo Oscuro")
        self.btn_toggle_theme.setIcon(QIcon("app/icons/moon.svg"))
        self.btn_toggle_theme.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle_theme.setObjectName("themeToggle")
        self.menuBar().setCornerWidget(self.btn_toggle_theme, Qt.Corner.TopRightCorner)

    def _setup_find_replace_bar(self):
        self.find_bar_widget = QWidget()
        self.find_bar_widget.setObjectName("findBarWidget")
        self.find_bar_layout = QHBoxLayout(self.find_bar_widget)
        self.find_bar_layout.setContentsMargins(12, 6, 12, 6)
        
        self.find_input = QLineEdit()
        self.find_input.setPlaceholderText("Buscar...")
        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("Reemplazar con...")
        
        self.btn_find_next = QPushButton("Siguiente")
        self.btn_replace = QPushButton("Reemplazar")
        self.btn_close_find = QPushButton("Cerrar")
        
        self.find_bar_layout.addWidget(QLabel("Buscar:"))
        self.find_bar_layout.addWidget(self.find_input)
        self.find_bar_layout.addWidget(self.btn_find_next)
        self.find_bar_layout.addWidget(QLabel("Reemplazar:"))
        self.find_bar_layout.addWidget(self.replace_input)
        self.find_bar_layout.addWidget(self.btn_replace)
        self.find_bar_layout.addWidget(self.btn_close_find)
        self.find_bar_layout.addStretch()
        
        self.main_layout.addWidget(self.find_bar_widget)
        self.find_bar_widget.hide()

    def _setup_actions(self):
        # File
        self.action_new_tab = QAction("Nueva Pestaña", self)
        self.action_new_tab.setShortcut("Ctrl+N")
        self.action_open = QAction("Abrir...", self)
        self.action_open.setShortcut("Ctrl+O")
        self.action_save = QAction("Guardar", self)
        self.action_save.setShortcut("Ctrl+S")
        self.action_save_as = QAction("Guardar Como...", self)
        self.action_save_as.setShortcut("Ctrl+Shift+S")
        self.action_close_tab = QAction("Cerrar Pestaña", self)
        self.action_close_tab.setShortcut("Ctrl+W")
        self.action_exit = QAction("Salir", self)
        self.action_exit.setShortcut("Ctrl+Q")
        
        # Edit
        self.action_undo = QAction("Deshacer", self)
        self.action_undo.setShortcut("Ctrl+Z")
        self.action_redo = QAction("Rehacer", self)
        self.action_redo.setShortcut("Ctrl+Y")
        self.action_cut = QAction("Cortar", self)
        self.action_cut.setShortcut("Ctrl+X")
        self.action_copy = QAction("Copiar", self)
        self.action_copy.setShortcut("Ctrl+C")
        self.action_paste = QAction("Pegar", self)
        self.action_paste.setShortcut("Ctrl+V")
        self.action_find = QAction("Buscar y Reemplazar", self)
        self.action_find.setShortcut("Ctrl+F")
        self.action_date_time = QAction("Fecha y Hora", self)
        self.action_date_time.setShortcut("F5")
        
        # View
        self.action_word_wrap = QAction("Ajuste de línea", self)
        self.action_word_wrap.setCheckable(True)
        self.action_word_wrap.setChecked(True) # On by default
        self.action_toggle_status = QAction("Barra de estado", self)
        self.action_toggle_status.setCheckable(True)
        self.action_toggle_status.setChecked(True)

    def _setup_menu(self):
        menu_bar = self.menuBar()
        
        file_menu = menu_bar.addMenu("Archivo")
        file_menu.addAction(self.action_new_tab)
        file_menu.addAction(self.action_open)
        file_menu.addAction(self.action_save)
        file_menu.addAction(self.action_save_as)
        file_menu.addSeparator()
        file_menu.addAction(self.action_close_tab)
        file_menu.addAction(self.action_exit)
        
        edit_menu = menu_bar.addMenu("Editar")
        edit_menu.addAction(self.action_undo)
        edit_menu.addAction(self.action_redo)
        edit_menu.addSeparator()
        edit_menu.addAction(self.action_cut)
        edit_menu.addAction(self.action_copy)
        edit_menu.addAction(self.action_paste)
        edit_menu.addSeparator()
        edit_menu.addAction(self.action_find)
        edit_menu.addAction(self.action_date_time)
        
        view_menu = menu_bar.addMenu("Ver")
        view_menu.addAction(self.action_word_wrap)
        view_menu.addAction(self.action_toggle_status)

    def _setup_main_toolbar(self):
        self.main_toolbar = QToolBar("Principal")
        self.main_toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.main_toolbar)
        
        # Fonts
        self.combo_font = QFontComboBox()
        self.combo_font.setToolTip("Tipo de Letra")
        self.combo_font.setMinimumWidth(120)
        self.combo_font.setMaximumWidth(180)
        self.combo_font.setEditable(True)
        
        self.spin_size = QSpinBox()
        self.spin_size.setRange(8, 72)
        self.spin_size.setValue(11)
        self.spin_size.setToolTip("Tamaño de Letra")
        self.spin_size.setMaximumWidth(60)
        
        self.main_toolbar.addWidget(self.combo_font)
        self.main_toolbar.addWidget(self.spin_size)
        
        self.main_toolbar.addSeparator()
        
        # Headers
        self.combo_headers = QComboBox()
        self.combo_headers.addItems(["Texto Normal", "H1 (Título)", "H2 (Subtítulo)", "H3"])
        self.main_toolbar.addWidget(self.combo_headers)
        
        self.main_toolbar.addSeparator()
        
        # Bold, Italic, Strikethrough
        self.btn_bold = QPushButton("B")
        self.btn_bold.setCheckable(True)
        self.btn_bold.setStyleSheet("font-weight: bold;")
        
        self.btn_italic = QPushButton("I")
        self.btn_italic.setCheckable(True)
        self.btn_italic.setStyleSheet("font-style: italic; font-family: serif;")
        
        self.btn_strike = QPushButton("S")
        self.btn_strike.setCheckable(True)
        self.btn_strike.setStyleSheet("text-decoration: line-through;")
        
        self.main_toolbar.addWidget(self.btn_bold)
        self.main_toolbar.addWidget(self.btn_italic)
        self.main_toolbar.addWidget(self.btn_strike)
        
        self.main_toolbar.addSeparator()
        self.btn_toggle_binary = QPushButton("Binario")
        self.btn_toggle_binary.setObjectName("btnToggleBinary")
        self.btn_toggle_binary.setToolTip("Alternar Panel Binario (Traducir texto a binario / binario a texto)")
        self.btn_toggle_binary.setCheckable(True)
        self.btn_toggle_binary.setCursor(Qt.CursorShape.PointingHandCursor)
        self.main_toolbar.addWidget(self.btn_toggle_binary)
        
        self.btn_toggle_markdown = QPushButton("Markdown")
        self.btn_toggle_markdown.setObjectName("btnToggleMarkdown")
        self.btn_toggle_markdown.setToolTip("Alternar Vista Previa Markdown")
        self.btn_toggle_markdown.setCheckable(True)
        self.btn_toggle_markdown.setCursor(Qt.CursorShape.PointingHandCursor)
        self.main_toolbar.addWidget(self.btn_toggle_markdown)
        
        self.combo_binary_mode = QComboBox()
        self.combo_binary_mode.addItems(["Texto ➔ Binario", "Binario ➔ Texto"])
        self.combo_binary_action = self.main_toolbar.addWidget(self.combo_binary_mode)
        self.combo_binary_action.setVisible(False)

    def _setup_format_toolbar(self):
        pass # Removed as we combined it

    def get_current_editor(self):
        return self.tabs.currentWidget()

    def show_message(self, message):
        self.status_bar.showMessage(message, 3000)
