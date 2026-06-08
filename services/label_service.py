import string


def generate_book_labels(code: str, total_quantity: int) -> str:
    code = code.strip()

    labels = [
        f"{code}{string.ascii_lowercase[index]}"
        for index in range(total_quantity)
    ]

    return ", ".join(labels)