import random


class UserUtils:
    @staticmethod
    def get_initials(first_name: str, last_name: str) -> str:
        return f"{first_name[0].upper()}{last_name[0].upper()}"

    @staticmethod
    def generate_color_from_string(value: str) -> tuple:
        random.seed(value)
        return (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        )

    @staticmethod
    def normalize_full_name(full_name: str) -> str:
        return " ".join((full_name or "").strip().split())

    @staticmethod
    def get_initials_from_full_name(full_name: str) -> str:
        normalized = UserUtils.normalize_full_name(full_name)
        if not normalized:
            return "U"

        parts = [p for p in normalized.split(" ") if p]
        if not parts:
            return "U"

        if len(parts) >= 2:
            return f"{parts[0][0].upper()}{parts[-1][0].upper()}"

        token = parts[0]
        if len(token) >= 2:
            return f"{token[0].upper()}{token[1].upper()}"
        return token[0].upper()

    @staticmethod
    def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
        r, g, b = rgb
        r = max(0, min(255, int(r)))
        g = max(0, min(255, int(g)))
        b = max(0, min(255, int(b)))
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def generate_profile_picture_svg(full_name: str, *, size: int = 256) -> str:
        """
        Génère un SVG (avatar) basé sur le nom complet.
        - Fond couleur pseudo-aléatoire (stable) dérivée du nom.
        - Texte: initiales (ex: "Jean Pierre" -> "JP").
        - Accessible: <title> contient le nom complet.
        """
        normalized_name = UserUtils.normalize_full_name(full_name)
        initials = UserUtils.get_initials_from_full_name(normalized_name)
        bg_rgb = UserUtils.generate_color_from_string(normalized_name or initials)
        bg = UserUtils._rgb_to_hex(bg_rgb)

        safe_title = (normalized_name or "Utilisateur").replace("&", "&amp;").replace(
            "<", "&lt;"
        ).replace(">", "&gt;")

        font_size = int(size * 0.42)

        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
            f'viewBox="0 0 {size} {size}" role="img" aria-labelledby="title">'
            f"<title id=\"title\">{safe_title}</title>"
            f'<rect width="{size}" height="{size}" rx="{int(size*0.18)}" fill="{bg}"/>'
            f'<text x="50%" y="52%" dominant-baseline="middle" text-anchor="middle" '
            f'font-family="Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif" '
            f'font-size="{font_size}" font-weight="700" fill="#ffffff">{initials}</text>'
            "</svg>"
        )
