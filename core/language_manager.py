import json

class LanguageManager:
    def __init__(self, lang_file="data/lang.json", config_file="config.json"):
        self.lang_file = lang_file
        self.config_file = config_file
        self.translations = self._load_translations()
        self.language = self._load_language()

    def _load_translations(self):
        with open(self.lang_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_language(self):
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
            return config.get("language", "en")
        except FileNotFoundError:
            return "en"

    def set_language(self, lang_code: str):
        """Muda o idioma e salva no config sem apagar os outros dados."""
        self.language = lang_code

        try:
            # 🔹 Lê o conteúdo atual do config.json
            with open(self.config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Se o arquivo não existir ou estiver corrompido, recria um novo
            config = {}

        # 🔹 Atualiza apenas o idioma
        config["language"] = lang_code

        # 🔹 Salva de volta o arquivo completo
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)

    def t(self, key: str) -> str:
        """Traduz uma chave interna (ex: 'strength' → 'Força')."""
        entry = self.translations.get(key)
        if entry is None:
            print(f"[DEBUG] Chave não encontrada: {key}")
            return key
        text = entry.get(self.language)
        if text is None:
            print(f"[DEBUG] Tradução não encontrada para idioma '{self.language}' na chave '{key}'")
            return key
        return text

    def rt(self, text: str) -> str:
        """Tradução reversa — obtém a chave interna a partir do texto traduzido."""
        for key, langs in self.translations.items():
            if langs.get(self.language) == text:
                return key
        return text  # se não encontrar, retorna o original

if __name__ == "__main__":
    lm = LanguageManager()

    print("--- Tradução normal ---")
    print(lm.t("strength"))
    print(lm.t("wisdom"))

    print("--- Tradução reversa ---")
    print(lm.rt("Força"))
    print(lm.rt("Sabedoria"))

    lm.set_language("en")
    print("--- Inglês ---")
    print(lm.t("strength"))
