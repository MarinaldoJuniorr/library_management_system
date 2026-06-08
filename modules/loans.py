import pandas as pd

from services.excel_service import read_sheet, save_sheet, get_next_id


SHEET_LOANS = "Prestamos"
SHEET_BOOKS = "Libros"
SHEET_USERS = "Usuarios"


def get_all_loans() -> pd.DataFrame:
    """
    Returns all loans registered in the system.
    """
    return read_sheet(SHEET_LOANS)


def get_active_loans() -> pd.DataFrame:
    """
    Returns only active loans.
    """
    loans_df = get_all_loans()

    if loans_df.empty:
        return loans_df

    return loans_df[loans_df["Estado"] == "Activo"]


def create_loan(
    user_id: int,
    book_id: int,
    loan_date: str,
    expected_return_date: str,
) -> None:
    """
    Creates a new loan and updates book availability.
    """
    books_df = read_sheet(SHEET_BOOKS)
    users_df = read_sheet(SHEET_USERS)
    loans_df = read_sheet(SHEET_LOANS)

    if user_id not in users_df["ID"].values:
        raise ValueError("Usuario no encontrado.")

    if book_id not in books_df["ID"].values:
        raise ValueError("Libro no encontrado.")

    book_row = books_df[books_df["ID"] == book_id]

    available_quantity = int(book_row.iloc[0]["Cantidad_Disponible"])

    if available_quantity <= 0:
        raise ValueError("No hay unidades disponibles para este libro.")

    new_loan = {
        "ID": get_next_id(SHEET_LOANS),
        "Usuario_ID": user_id,
        "Libro_ID": book_id,
        "Fecha_Prestamo": loan_date,
        "Fecha_Prevista_Devolucion": expected_return_date,
        "Estado": "Activo",
    }

    loans_df = pd.concat(
        [loans_df, pd.DataFrame([new_loan])],
        ignore_index=True
    )

    books_df.loc[
        books_df["ID"] == book_id,
        "Cantidad_Disponible"
    ] = available_quantity - 1

    save_sheet(SHEET_LOANS, loans_df)
    save_sheet(SHEET_BOOKS, books_df)