import pandas as pd

from services.excel_service import read_sheet, save_sheet, get_next_id
from services.label_service import generate_book_labels


SHEET_NAME = "Libros"


def get_all_books() -> pd.DataFrame:
    return read_sheet(SHEET_NAME)


def get_book_by_id(book_id: int) -> pd.DataFrame:
    books_df = get_all_books()
    return books_df[books_df["ID"] == book_id]


def create_book(
    code: str,
    title: str,
    author: str,
    publisher: str,
    total_quantity: int,
) -> None:
    code = code.strip()
    title = title.strip()
    author = author.strip()
    publisher = publisher.strip()

    if not code or not title or not author or not publisher:
        raise ValueError("Todos los campos son obligatorios.")

    books_df = get_all_books()

    existing_code = books_df[
        books_df["Codigo"].astype(str).str.lower() == code.lower()
    ]

    if not existing_code.empty:
        raise ValueError("Este código ya está registrado.")

    new_book = {
        "ID": get_next_id(SHEET_NAME),
        "Codigo": code,
        "Titulo": title,
        "Autor": author,
        "Editora": publisher,
        "Cantidad_Total": total_quantity,
        "Cantidad_Disponible": total_quantity,
        "Observaciones": generate_book_labels(code, total_quantity),
    }

    books_df = pd.concat(
        [books_df, pd.DataFrame([new_book])],
        ignore_index=True
    )

    save_sheet(SHEET_NAME, books_df)


def update_book(
    book_id: int,
    code: str,
    title: str,
    author: str,
    publisher: str,
    total_quantity: int,
) -> None:
    code = code.strip()
    title = title.strip()
    author = author.strip()
    publisher = publisher.strip()

    if not code or not title or not author or not publisher:
        raise ValueError("Todos los campos son obligatorios.")

    books_df = get_all_books()

    if book_id not in books_df["ID"].values:
        raise ValueError("Libro no encontrado.")

    current_book = books_df[books_df["ID"] == book_id].iloc[0]

    old_total = int(current_book["Cantidad_Total"])
    old_available = int(current_book["Cantidad_Disponible"])

    borrowed_quantity = old_total - old_available
    new_available = total_quantity - borrowed_quantity

    if new_available < 0:
        raise ValueError(
            "La cantidad total no puede ser menor que los ejemplares prestados."
        )

    duplicated_code = books_df[
        (books_df["Codigo"].astype(str).str.lower() == code.lower())
        &
        (books_df["ID"] != book_id)
    ]

    if not duplicated_code.empty:
        raise ValueError("Este código ya está registrado.")

    books_df.loc[
        books_df["ID"] == book_id,
        [
            "Codigo",
            "Titulo",
            "Autor",
            "Editora",
            "Cantidad_Total",
            "Cantidad_Disponible",
            "Observaciones",
        ],
    ] = [
        code,
        title,
        author,
        publisher,
        total_quantity,
        new_available,
        generate_book_labels(code, total_quantity),
    ]

    save_sheet(SHEET_NAME, books_df)


def delete_book(book_id: int) -> None:
    """
    Deletes a book by ID.
    """
    books_df = get_all_books()

    if book_id not in books_df["ID"].values:
        raise ValueError("Libro no encontrado.")

    loans_df = read_sheet("Prestamos")

    active_loans = loans_df[
        (loans_df["Libro_ID"] == book_id)
        &
        (loans_df["Estado"] == "Activo")
    ]

    if not active_loans.empty:
        raise ValueError(
            "No se puede eliminar un libro con préstamos activos."
        )

    books_df = books_df[books_df["ID"] != book_id]

    save_sheet(SHEET_NAME, books_df)