import os

class StylesheetLoader:
    _stylesheet_cache = {}

    @staticmethod
    def load_stylesheet(name: str) -> str:
        if name not in StylesheetLoader._stylesheet_cache:
            stylesheet_path = os.path.join(os.path.dirname(__file__), f'{name}.qss')
            try:
                with open(stylesheet_path, 'r') as file:
                    StylesheetLoader._stylesheet_cache[name] = file.read()
            except FileNotFoundError as e:
                print(f"Stylesheet not found: {e}")
                StylesheetLoader._stylesheet_cache[name] = ""

        return StylesheetLoader._stylesheet_cache[name]