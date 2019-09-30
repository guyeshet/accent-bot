class AccentType:
    USA = "usa"
    UK = "uk"

    display = {USA: "American",
               UK: "British"}

    @staticmethod
    def language(accent_type):
        return AccentType.display.get(accent_type, "")

