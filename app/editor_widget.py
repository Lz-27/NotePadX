from PyQt6.QtWidgets import QWidget, QTextEdit, QHBoxLayout, QFrame, QMenu
from PyQt6.QtGui import QPainter, QColor, QFont, QTextFormat, QTextCharFormat, QSyntaxHighlighter, QTextCursor
from PyQt6.QtCore import Qt, QRect
import re
from spellchecker import SpellChecker

# Inicializar spellchecker en español
spell = SpellChecker(language='es')

class SpellCheckHighlighter(QSyntaxHighlighter):
    """
    Subclase de QSyntaxHighlighter que aplica subrayado rojo a las palabras
    que no se encuentren en el diccionario español (errores ortográficos).
    """
    def __init__(self, document):
        super().__init__(document)
        self.format = QTextCharFormat()
        self.format.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SpellCheckUnderline)
        self.format.setUnderlineColor(QColor(Qt.GlobalColor.red))

    def highlightBlock(self, text):
        # Encontrar todas las palabras en el texto (letras)
        for match in re.finditer(r'\b[^\W\d_]+\b', text, re.UNICODE):
            word = match.group()
            # Ignorar corrección si la palabra parece correcta
            if not spell.known([word.lower()]):
                self.setFormat(match.start(), match.end() - match.start(), self.format)

class LineNumberArea(QWidget):
    """
    Widget personalizado que se dibuja en el margen izquierdo del editor
    para mostrar los números de línea.
    """
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def sizeHint(self):
        return self.editor.line_number_area_size_hint()

    def paintEvent(self, event):
        from PyQt6.QtWidgets import QStyleOption, QStyle
        from PyQt6.QtGui import QPainter
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, painter, self)
        
        self.editor.line_number_area_paint_event(event, painter)

class CustomTextEdit(QTextEdit):
    """
    Editor de texto personalizado enriquecido con funcionalidades extra:
    - Números de línea en el margen izquierdo.
    - Resaltado de errores ortográficos en tiempo real.
    - Menú contextual personalizado con sugerencias de corrección.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName("editor")
        
        # Ocultar el marco por defecto
        self.setFrameStyle(QFrame.Shape.NoFrame)
        
        # Configurar el margen izquierdo para los números de línea
        self.line_number_area = LineNumberArea(self)
        
        # Activar el resaltador de sintaxis ortográfica
        self.highlighter = SpellCheckHighlighter(self.document())
        
        # Conectar señales para actualizar el área de números
        self.document().blockCountChanged.connect(self.update_line_number_area_width)
        self.verticalScrollBar().valueChanged.connect(self.line_number_area.update)
        self.textChanged.connect(self.line_number_area.update)
        self.cursorPositionChanged.connect(self.line_number_area.update)
        
        self.update_line_number_area_width(0)
        
    def line_number_area_width(self):
        digits = 1
        max_num = max(1, self.document().blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
            
        # Calculamos el ancho basándonos en la fuente actual
        space = 20 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, newBlockCount):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
            
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def line_number_area_size_hint(self):
        from PyQt6.QtCore import QSize
        return QSize(self.line_number_area_width(), 0)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        
        undo_action = menu.addAction("Deshacer")
        undo_action.triggered.connect(self.undo)
        undo_action.setEnabled(self.document().isUndoAvailable())
        undo_action.setShortcut("Ctrl+Z")
        
        redo_action = menu.addAction("Rehacer")
        redo_action.triggered.connect(self.redo)
        redo_action.setEnabled(self.document().isRedoAvailable())
        redo_action.setShortcut("Ctrl+Y")
        
        menu.addSeparator()
        
        cut_action = menu.addAction("Cortar")
        cut_action.triggered.connect(self.cut)
        cut_action.setEnabled(self.textCursor().hasSelection())
        cut_action.setShortcut("Ctrl+X")
        
        copy_action = menu.addAction("Copiar")
        copy_action.triggered.connect(self.copy)
        copy_action.setEnabled(self.textCursor().hasSelection())
        copy_action.setShortcut("Ctrl+C")
        
        paste_action = menu.addAction("Pegar")
        paste_action.triggered.connect(self.paste)
        paste_action.setEnabled(self.canPaste())
        paste_action.setShortcut("Ctrl+V")
        
        delete_action = menu.addAction("Eliminar")
        delete_action.triggered.connect(lambda: self.textCursor().removeSelectedText())
        delete_action.setEnabled(self.textCursor().hasSelection())
        
        menu.addSeparator()
        
        select_all_action = menu.addAction("Seleccionar todo")
        select_all_action.triggered.connect(self.selectAll)
        select_all_action.setShortcut("Ctrl+A")
        
        cursor = self.cursorForPosition(event.pos())
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        word = cursor.selectedText()
        
        if word and not spell.known([word.lower()]):
            candidates = spell.candidates(word.lower())
            if candidates:
                menu.addSeparator()
                # Mostrar hasta 5 sugerencias
                for candidate in list(candidates)[:5]:
                    # Preservar la capitalización si la original empezaba con mayúscula
                    if word[0].isupper():
                        candidate = candidate.capitalize()
                    
                    action = menu.addAction(f"✨ {candidate}")
                    action.triggered.connect(lambda checked=False, c=candidate, curs=cursor: self.replace_word(curs, c))
                    
        menu.exec(event.globalPos())

    def replace_word(self, cursor, new_word):
        cursor.insertText(new_word)

    def line_number_area_paint_event(self, event, painter):
        block = self.document().begin()
        
        from PyQt6.QtGui import QTextCursor, QPalette
        from PyQt6.QtCore import Qt
        
        text_color = self.line_number_area.palette().color(QPalette.ColorRole.WindowText)
        
        while block.isValid():
            block_number = block.blockNumber()
            
            cursor = QTextCursor(block)
            rect = self.cursorRect(cursor)
            top = rect.top()
            bottom = top + rect.height()
            
            # Si estamos por debajo de lo que se ve, rompemos el bucle
            if top > event.rect().bottom():
                break
                
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(text_color)
                
                # Resaltar la línea actual si se desea
                if self.textCursor().blockNumber() == block_number:
                    font = painter.font()
                    font.setBold(True)
                    painter.setFont(font)
                    painter.setPen(QColor("#38BDF8")) # Azul acento Fluent
                else:
                    font = painter.font()
                    font.setBold(False)
                    painter.setFont(font)

                painter.drawText(0, top, self.line_number_area.width() - 5, self.fontMetrics().height(),
                                 Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop, number)
            
            block = block.next()
