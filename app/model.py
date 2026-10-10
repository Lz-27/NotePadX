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

    def text_to_binary(self, text):
        """Converts normal text to binary string, preserving newlines."""
        if not text:
            return ""
        lines = text.split('\n')
        binary_lines = []
        for line in lines:
            # Convert each character to 8-bit binary and join with space
            binary_line = ' '.join(format(ord(c), '08b') for c in line)
            binary_lines.append(binary_line)
        return '\n'.join(binary_lines)

    def binary_to_text(self, binary_text):
        """Converts binary string back to normal text."""
        if not binary_text:
            return ""
        lines = binary_text.split('\n')
        text_lines = []
        for line in lines:
            blocks = line.split(' ')
            chars = []
            for block in blocks:
                if len(block) == 8 and all(c in '01' for c in block):
                    try:
                        chars.append(chr(int(block, 2)))
                    except ValueError:
                        pass
            text_lines.append(''.join(chars))
        return '\n'.join(text_lines)
