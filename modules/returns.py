import pandas as pd

from services.excel_service import read_sheet, save_sheet, get_next_id


SHEET_RETURNS = "Devoluciones"
SHEET_LOANS = "Prestamos"
SHEET_BOOKS = "Libros"


def get_all_returns() -> pd.DataFrame:
    """
    Returns all book returns registered in the system.
    """
    return read_sheet(SHEET_RETURNS)


def create_return(loan_id: int, return_date: str) -> None:
    """
    Registers a return, closes the loan, and restores book availability.
    """
    loans_df = read_sheet(SHEET_LOANS)
    books_df = read_sheet(SHEET_BOOKS)
    returns_df = read_sheet(SHEET_RETURNS)

    if loan_id not in loans_df["ID"].values:
        raise ValueError("Préstamo no encontrado.")

    loan_row = loans_df[loans_df["ID"] == loan_id].iloc[0]

    if loan_row["Estado"] != "Activo":
        raise ValueError("Este préstamo ya fue devuelto.")

    book_id = int(loan_row["Libro_ID"])
    user_id = int(loan_row["Usuario_ID"])

    expected_return_date = pd.to_datetime(
        loan_row["Fecha_Prevista_Devolucion"]
    ).date()

    actual_return_date = pd.to_datetime(return_date).date()

    days_late = max(
        (actual_return_date - expected_return_date).days,
        0
    )

    new_return = {
        "ID": get_next_id(SHEET_RETURNS),
        "Prestamo_ID": loan_id,
        "Libro_ID": book_id,
        "Usuario_ID": user_id,
        "Fecha_Devolucion": return_date,
        "Dias_Atraso": days_late,
    }

    returns_df = pd.concat(
        [returns_df, pd.DataFrame([new_return])],
        ignore_index=True
    )

    loans_df.loc[
        loans_df["ID"] == loan_id,
        "Estado"
    ] = "Devuelto"

    book_row = books_df[books_df["ID"] == book_id]

    if book_row.empty:
        raise ValueError("Libro no encontrado.")

    available_quantity = int(book_row.iloc[0]["Cantidad_Disponible"])
    total_quantity = int(book_row.iloc[0]["Cantidad_Total"])

    books_df.loc[
        books_df["ID"] == book_id,
        "Cantidad_Disponible"
    ] = min(available_quantity + 1, total_quantity)

    save_sheet(SHEET_RETURNS, returns_df)
    save_sheet(SHEET_LOANS, loans_df)
    save_sheet(SHEET_BOOKS, books_df)