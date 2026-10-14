import os
import markdown

class EditorModel:
    """
    Gestiona la lógica de datos y las conversiones de formato.
    Actúa como la capa de abstracción para leer y escribir archivos, y transformar texto.
    """
    def __init__(self):
        pass

    def markdown_to_html(self, text):
        """Convierte texto Markdown a HTML."""
        if not text:
            return ""
        return markdown.markdown(text)

    def read_file(self, file_path):
        """Reads content from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise e

    def write_file(self, file_path, content):
        """Writes content to a file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
        except Exception as e:
            raise e

    def text_to_binary(self, text, chunk_size=4096):
        """Converts normal text to binary string, preserving newlines efficiently."""
        if not text:
            return ""
        # Procesa eficientemente línea por línea y carácter por carácter
        binary_lines = []
        for line in text.split('\n'):
            binary_line = ' '.join(f"{ord(c):08b}" for c in line)
            binary_lines.append(binary_line)
        return '\n'.join(binary_lines)

    def binary_to_text(self, binary_text, chunk_size=4096):
        """Converts binary string back to normal text efficiently."""
        if not binary_text:
            return ""
        text_lines = []
        for line in binary_text.split('\n'):
            blocks = line.split(' ')
            chars = []
            for b in blocks:
                if len(b) == 8 and all(c in '01' for c in b):
                    try:
                        chars.append(chr(int(b, 2)))
                    except ValueError:
                        pass
            text_lines.append(''.join(chars))
        return '\n'.join(text_lines)

