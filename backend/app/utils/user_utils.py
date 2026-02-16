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
