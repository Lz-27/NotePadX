import os
from datetime import datetime
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtGui import QTextCharFormat, QFont, QTextCursor
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QVariantAnimation
from app.editor_widget import CustomTextEdit

class EditorController:
    """
    Controlador principal que conecta el Modelo (EditorModel) con la Vista (EditorView).
    Maneja eventos de usuario, señales de UI, lógica de guardado/apertura y control de estado.
    """
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.is_dark_mode = True
        self._is_updating = False
        self.current_font = QFont("Segoe UI", 11)
        
        # Set default values in UI
        self.view.combo_font.setCurrentFont(self.current_font)
        self.view.spin_size.setValue(11)
        
        # Diccionario para mapear el widget de la pestaña (editor) a su ruta de archivo
        self.tab_files = {} 
        
        # Load Stylesheets
        self.style_light = self._load_stylesheet("app/styles/light.qss")
        self.style_dark = self._load_stylesheet("app/styles/dark.qss")
        
        self._connect_signals()
        self._apply_theme()
        
        # Abrir primera pestaña vacía
        self.new_tab()
        
    def _load_stylesheet(self, filepath):
        try:
            with open(filepath, "r") as f:
                return f.read()
        except Exception:
            return ""

    def _connect_signals(self):
        # File operations
        self.view.action_new_tab.triggered.connect(self.new_tab)
        self.view.action_open.triggered.connect(self.open_file)
        self.view.action_save.triggered.connect(self.save_file)
        self.view.action_save_as.triggered.connect(self.save_file_as)
        self.view.action_close_tab.triggered.connect(lambda: self.close_tab(self.view.tabs.currentIndex()))
        self.view.action_exit.triggered.connect(self.view.close)
        
        # Edit operations (routed dynamically)
        self.view.action_undo.triggered.connect(self._route_to_editor("undo"))
        self.view.action_redo.triggered.connect(self._route_to_editor("redo"))
        self.view.action_cut.triggered.connect(self._route_to_editor("cut"))
        self.view.action_copy.triggered.connect(self._route_to_editor("copy"))
        self.view.action_paste.triggered.connect(self._route_to_editor("paste"))
        
        self.view.action_find.triggered.connect(self._toggle_find_bar)
        self.view.action_date_time.triggered.connect(self._insert_date_time)
        
        # View operations
        self.view.action_word_wrap.triggered.connect(self._toggle_word_wrap)
        self.view.action_toggle_status.triggered.connect(self._toggle_status_bar)
        
        # Theme Toggle
        self.view.btn_toggle_theme.clicked.connect(self.toggle_theme)
        
        # Tab closing
        self.view.tabs.tabCloseRequested.connect(self.close_tab)
        
        # Info Button
        self.view.btn_info.clicked.connect(self.show_about_dialog)
        
        # Formato
        self.view.btn_bold.clicked.connect(self._toggle_bold)
        self.view.btn_italic.clicked.connect(self._toggle_italic)
        self.view.btn_strike.clicked.connect(self._toggle_strike)
        
        # Tipografía
        self.view.combo_font.currentFontChanged.connect(self._change_font)
        self.view.spin_size.valueChanged.connect(self._change_font)
        
        # Add Tab Button
        self.view.btn_add_tab.clicked.connect(lambda: self.new_tab())
        self.view.combo_headers.currentTextChanged.connect(self._apply_header)
        
        # Binary Toggle
        self.view.btn_toggle_binary.clicked.connect(self._toggle_binary_mode)
        self.view.combo_binary_mode.currentIndexChanged.connect(self._update_translation_direction)
        self.view.binary_terminal.textChanged.connect(self._on_binary_text_changed)
        
        # Markdown Toggle
        self.view.btn_toggle_markdown.clicked.connect(self._toggle_markdown_mode)
        
        self.view.tabs.currentChanged.connect(self._on_tab_changed)
        
        # Find/Replace
        self.view.btn_close_find.clicked.connect(self.view.find_bar_widget.hide)
        self.view.btn_find_next.clicked.connect(self._find_next)
        self.view.btn_replace.clicked.connect(self._replace_text)

    def _route_to_editor(self, method_name):
        """Devuelve una función que llama al método dado en el editor actual."""
        def route():
            editor = self.view.get_current_editor()
            if editor and hasattr(editor, method_name):
                getattr(editor, method_name)()
        return route

    def _apply_theme(self):
        if self.is_dark_mode:
            self.view.setStyleSheet(self.style_dark)
            self.view.btn_toggle_theme.setText("☀️ Claro")
        else:
            self.view.setStyleSheet(self.style_light)
            self.view.btn_toggle_theme.setText("🌙 Oscuro")

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self._apply_theme()

    def show_about_dialog(self):
        about_text = (
            "<h2>Bloc de Notas Moderno</h2>"
            "<p><b>Desarrollado con:</b> Python (PyQt6)</p>"
            "<p><b>Autor:</b> Ing. Luis Adrian Castillo Alvarez</p>"
            "<p><b>Año de creación:</b> 2026</p>"
            "<p><b>Más información:</b> Un editor de texto moderno con soporte para pestañas, "
            "temas claro/oscuro, corrector ortográfico y formato de texto enriquecido básico.</p>"
        )
        QMessageBox.about(self.view, "Acerca del Proyecto", about_text)

    # --- Gestión de Pestañas ---
    
    def new_tab(self, content="", title="Sin Título", filepath=None):
        editor = CustomTextEdit()
        editor.setFont(self.current_font)
        
        # Si es texto enriquecido/HTML lo cargamos así, si no, texto plano.
        if content.startswith("<") and ">" in content:
            editor.setHtml(content)
        else:
            editor.setPlainText(content)
            
        # Configurar Line Wrap
        editor.setLineWrapMode(
            CustomTextEdit.LineWrapMode.WidgetWidth if self.view.action_word_wrap.isChecked() 
            else CustomTextEdit.LineWrapMode.NoWrap
        )
        
        index = self.view.tabs.addTab(editor, title)
        self.view.tabs.setCurrentIndex(index)
        self.tab_files[editor] = filepath
        
        # Conectar actualizaciones en vivo
        editor.textChanged.connect(self._update_live_stats)
        editor.textChanged.connect(self._on_editor_text_changed)
        editor.cursorPositionChanged.connect(self._update_live_stats)
        self._update_live_stats()
        if self.view.btn_toggle_binary.isChecked():
            self._update_translation_direction()

    def close_tab(self, index):
        if index < 0: return
        widget = self.view.tabs.widget(index)
        self.view.tabs.removeTab(index)
        if widget in self.tab_files:
            del self.tab_files[widget]
        widget.deleteLater()
        
        if self.view.tabs.count() == 0:
            self.new_tab() # Siempre tener al menos una pestaña

    # --- Operaciones de Archivo ---

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self.view, "Abrir Archivo", "", "Archivos de texto (*.txt *.md *.html);;Todos los archivos (*)"
        )
        if file_path:
            try:
                content = self.model.read_file(file_path)
                title = os.path.basename(file_path)
                self.new_tab(content, title, file_path)
                self.view.show_message(f"Abierto: {title}")
            except Exception as e:
                QMessageBox.critical(self.view, "Error", f"No se pudo abrir:\n{e}")

    def save_file(self):
        editor = self.view.get_current_editor()
        if not editor: return
        
        current_filepath = self.tab_files.get(editor)
        if current_filepath:
            self._save_to_path(editor, current_filepath)
        else:
            self.save_file_as()

    def save_file_as(self):
        editor = self.view.get_current_editor()
        if not editor: return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self.view, "Guardar Como", "", "Markdown/HTML (*.md *.html);;Texto Plano (*.txt);;Todos (*)"
        )
        if file_path:
            self._save_to_path(editor, file_path)

    def _save_to_path(self, editor, file_path):
        try:
            # Guardamos como HTML si la extensión lo permite para conservar formato, 
            # si es txt guardamos plano.
            if file_path.endswith('.txt'):
                content = editor.toPlainText()
            else:
                content = editor.toHtml()
                
            self.model.write_file(file_path, content)
            self.tab_files[editor] = file_path
            
            # Actualizar título de pestaña
            index = self.view.tabs.indexOf(editor)
            if index >= 0:
                self.view.tabs.setTabText(index, os.path.basename(file_path))
                
            self.view.show_message("Guardado correctamente")
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Fallo al guardar:\n{e}")

    # --- Otras Funciones ---
    
    def _toggle_word_wrap(self):
        checked = self.view.action_word_wrap.isChecked()
        for i in range(self.view.tabs.count()):
            editor = self.view.tabs.widget(i)
            if checked:
                editor.setLineWrapMode(CustomTextEdit.LineWrapMode.WidgetWidth)
            else:
                editor.setLineWrapMode(CustomTextEdit.LineWrapMode.NoWrap)

    def _toggle_status_bar(self):
        self.view.status_bar.setVisible(self.view.action_toggle_status.isChecked())

    def _insert_date_time(self):
        editor = self.view.get_current_editor()
        if editor:
            now = datetime.now().strftime("%I:%M %p %d/%m/%Y")
            editor.insertPlainText(now)

    def _update_live_stats(self):
        editor = self.view.get_current_editor()
        if not editor: return
        
        # Cursores y conteo
        cursor = editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        
        text = editor.toPlainText()
        words = len(text.split())
        chars = len(text)
        
        self.view.lbl_cursor_pos.setText(f"Ln {line}, Col {col}")
        self.view.lbl_word_count.setText(f"{words} palabras, {chars} caracteres")

    def _toggle_binary_mode(self):
        is_visible = self.view.btn_toggle_binary.isChecked()
        
        # Si se abre Binario, cerramos Markdown
        if is_visible and self.view.btn_toggle_markdown.isChecked():
            self.view.btn_toggle_markdown.setChecked(False)
            self._toggle_markdown_mode()
            
        self.view.combo_binary_action.setVisible(is_visible)
        
        if hasattr(self, 'binary_animation'):
            self.binary_animation.stop()
            
        splitter = self.view.splitter
        term = self.view.binary_terminal
        
        self.binary_animation = QVariantAnimation()
        self.binary_animation.setDuration(250)
        self.binary_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        current_sizes = splitter.sizes()
        total_width = sum(current_sizes)
        if total_width == 0: total_width = 800
        
        if is_visible:
            if current_sizes[1] == 0:
                start_sizes = [total_width, 0]
            else:
                start_sizes = current_sizes
            end_sizes = [total_width // 2, total_width - (total_width // 2)]
            
            term.show()
            self._update_translation_direction()
        else:
            start_sizes = current_sizes
            end_sizes = [total_width, 0]
            
            self.binary_animation.finished.connect(term.hide)
            
            editor = self.view.get_current_editor()
            if editor:
                editor.setReadOnly(False)
                
        def update_sizes(val):
            w1 = int(start_sizes[0] + (end_sizes[0] - start_sizes[0]) * val)
            w2 = int(start_sizes[1] + (end_sizes[1] - start_sizes[1]) * val)
            splitter.setSizes([w1, w2])
            
        self.binary_animation.valueChanged.connect(update_sizes)
        self.binary_animation.setStartValue(0.0)
        self.binary_animation.setEndValue(1.0)
        self.binary_animation.start()

    def _toggle_markdown_mode(self):
        is_visible = self.view.btn_toggle_markdown.isChecked()
        
        # Si se abre Markdown, cerramos Binario
        if is_visible and self.view.btn_toggle_binary.isChecked():
            self.view.btn_toggle_binary.setChecked(False)
            self._toggle_binary_mode()
            
        if hasattr(self, 'markdown_animation'):
            self.markdown_animation.stop()
            
        splitter = self.view.splitter
        preview = self.view.markdown_preview
        
        self.markdown_animation = QVariantAnimation()
        self.markdown_animation.setDuration(250)
        self.markdown_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        current_sizes = splitter.sizes()
        total_width = sum(current_sizes)
        if total_width == 0: total_width = 800
        
        if is_visible:
            # Índice 2 es el markdown_preview
            if current_sizes[2] == 0:
                start_sizes = [total_width, 0, 0]
            else:
                start_sizes = current_sizes
            end_sizes = [total_width // 2, 0, total_width - (total_width // 2)]
            
            preview.show()
            self._update_markdown_preview()
        else:
            start_sizes = current_sizes
            end_sizes = [total_width, 0, 0]
            
            self.markdown_animation.finished.connect(preview.hide)
                
        def update_sizes(val):
            w1 = int(start_sizes[0] + (end_sizes[0] - start_sizes[0]) * val)
            w2 = int(start_sizes[1] + (end_sizes[1] - start_sizes[1]) * val)
            w3 = int(start_sizes[2] + (end_sizes[2] - start_sizes[2]) * val)
            splitter.setSizes([w1, w2, w3])
            
        self.markdown_animation.valueChanged.connect(update_sizes)
        self.markdown_animation.setStartValue(0.0)
        self.markdown_animation.setEndValue(1.0)
        self.markdown_animation.start()

    def _update_markdown_preview(self):
        if not self.view.btn_toggle_markdown.isChecked():
            return
        editor = self.view.get_current_editor()
        if editor:
            html = self.model.markdown_to_html(editor.toPlainText())
            self.view.markdown_preview.setHtml(html)

    def _update_translation_direction(self):
        editor = self.view.get_current_editor()
        if not editor or not self.view.btn_toggle_binary.isChecked():
            return
            
        mode = self.view.combo_binary_mode.currentIndex()
        if mode == 0: # Texto -> Binario
            editor.setReadOnly(False)
            self.view.binary_terminal.setReadOnly(True)
            self._translate_to_binary()
        else: # Binario -> Texto
            self.view.binary_terminal.setReadOnly(False)
            editor.setReadOnly(True)
            self._translate_to_text()

    def _on_editor_text_changed(self):
        if self.view.btn_toggle_binary.isChecked() and self.view.combo_binary_mode.currentIndex() == 0:
            self._translate_to_binary()
        if self.view.btn_toggle_markdown.isChecked():
            self._update_markdown_preview()

    def _on_binary_text_changed(self):
        if self.view.btn_toggle_binary.isChecked() and self.view.combo_binary_mode.currentIndex() == 1:
            self._translate_to_text()

    def _translate_to_binary(self):
        if self._is_updating: return
        self._is_updating = True
        try:
            editor = self.view.get_current_editor()
            if editor:
                binary_text = self.model.text_to_binary(editor.toPlainText())
                self.view.binary_terminal.setPlainText(binary_text)
        finally:
            self._is_updating = False

    def _translate_to_text(self):
        if self._is_updating: return
        self._is_updating = True
        try:
            editor = self.view.get_current_editor()
            if editor:
                text = self.model.binary_to_text(self.view.binary_terminal.toPlainText())
                editor.setPlainText(text)
        finally:
            self._is_updating = False

    def _on_tab_changed(self, index):
        self._update_live_stats()
        if self.view.btn_toggle_binary.isChecked():
            self._update_translation_direction()
        if self.view.btn_toggle_markdown.isChecked():
            self._update_markdown_preview()

    # --- Formato Enriquecido ---
    
    def _change_font(self, *args):
        self.current_font = self.view.combo_font.currentFont()
        self.current_font.setPointSize(self.view.spin_size.value())
        
        for i in range(self.view.tabs.count()):
            editor = self.view.tabs.widget(i)
            editor.setFont(self.current_font)
            
    def _toggle_bold(self):
        editor = self.view.get_current_editor()
        if editor:
            fmt = QTextCharFormat()
            fmt.setFontWeight(QFont.Weight.Bold if self.view.btn_bold.isChecked() else QFont.Weight.Normal)
            editor.mergeCurrentCharFormat(fmt)

    def _toggle_italic(self):
        editor = self.view.get_current_editor()
        if editor:
            fmt = QTextCharFormat()
            fmt.setFontItalic(self.view.btn_italic.isChecked())
            editor.mergeCurrentCharFormat(fmt)
            
    def _toggle_strike(self):
        editor = self.view.get_current_editor()
        if editor:
            fmt = QTextCharFormat()
            fmt.setFontStrikeOut(self.view.btn_strike.isChecked())
            editor.mergeCurrentCharFormat(fmt)

    def _apply_header(self, text):
        editor = self.view.get_current_editor()
        if not editor: return
        
        cursor = editor.textCursor()
        cursor.select(QTextCursor.SelectionType.LineUnderCursor)
        fmt = QTextCharFormat()
        
        if "H1" in text:
            fmt.setFontPointSize(24)
            fmt.setFontWeight(QFont.Weight.Bold)
        elif "H2" in text:
            fmt.setFontPointSize(18)
            fmt.setFontWeight(QFont.Weight.Bold)
        elif "H3" in text:
            fmt.setFontPointSize(14)
            fmt.setFontWeight(QFont.Weight.Bold)
        else:
            fmt.setFontPointSize(11) # Tamaño normal
            fmt.setFontWeight(QFont.Weight.Normal)
            
        cursor.mergeCharFormat(fmt)
        # Volver el foco al editor
        editor.setFocus()

    # --- Buscar y Reemplazar ---
    
    def _toggle_find_bar(self):
        if hasattr(self, 'find_animation') and self.find_animation.state() == QPropertyAnimation.State.Running:
            return
            
        bar = self.view.find_bar_widget
        self.find_animation = QPropertyAnimation(bar, b"maximumHeight")
        self.find_animation.setDuration(250)
        self.find_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        if bar.isVisible():
            self.find_animation.setStartValue(bar.height())
            self.find_animation.setEndValue(0)
            self.find_animation.finished.connect(bar.hide)
            self.find_animation.start()
        else:
            bar.show()
            bar.setMaximumHeight(0)
            target_height = bar.sizeHint().height()
            self.find_animation.setStartValue(0)
            self.find_animation.setEndValue(target_height)
            self.find_animation.finished.connect(lambda: bar.setMaximumHeight(16777215))
            self.find_animation.start()
            self.view.find_input.setFocus()

    def _find_next(self):
        editor = self.view.get_current_editor()
        text_to_find = self.view.find_input.text()
        if editor and text_to_find:
            found = editor.find(text_to_find)
            if not found:
                # Volver al inicio
                cursor = editor.textCursor()
                cursor.setPosition(0)
                editor.setTextCursor(cursor)
                editor.find(text_to_find)

    def _replace_text(self):
        editor = self.view.get_current_editor()
        if editor:
            cursor = editor.textCursor()
            if cursor.hasSelection():
                cursor.insertText(self.view.replace_input.text())
            self._find_next()
