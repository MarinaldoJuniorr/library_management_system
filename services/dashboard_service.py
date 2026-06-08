import pandas as pd

from services.excel_service import read_sheet


SHEET_BOOKS = "Libros"
SHEET_USERS = "Usuarios"
SHEET_LOANS = "Prestamos"
SHEET_RETURNS = "Devoluciones"


def get_dashboard_metrics() -> dict:
    books_df = read_sheet(SHEET_BOOKS)
    users_df = read_sheet(SHEET_USERS)
    loans_df = read_sheet(SHEET_LOANS)
    returns_df = read_sheet(SHEET_RETURNS)

    total_titles = len(books_df)
    total_books = (
        int(books_df["Cantidad_Total"].sum())
        if not books_df.empty
        else 0
    )
    available_books = (
        int(books_df["Cantidad_Disponible"].sum())
        if not books_df.empty
        else 0
    )
    users = len(users_df)

    active_loans = 0
    if not loans_df.empty:
        active_loans = len(loans_df[loans_df["Estado"] == "Activo"])

    overdue_returns = 0
    if not returns_df.empty:
        overdue_returns = len(returns_df[returns_df["Dias_Atraso"] > 0])

    return {
        "total_titles": total_titles,
        "total_books": total_books,
        "available_books": available_books,
        "users": users,
        "active_loans": active_loans,
        "overdue_returns": overdue_returns,
    }


def get_loans_report() -> pd.DataFrame:
    loans_df = read_sheet(SHEET_LOANS)
    users_df = read_sheet(SHEET_USERS)
    books_df = read_sheet(SHEET_BOOKS)

    if loans_df.empty:
        return loans_df

    report_df = loans_df.merge(
        users_df[["ID", "Nombre"]],
        left_on="Usuario_ID",
        right_on="ID",
        how="left",
        suffixes=("", "_Usuario")
    )

    report_df = report_df.merge(
        books_df[["ID", "Codigo", "Titulo"]],
        left_on="Libro_ID",
        right_on="ID",
        how="left",
        suffixes=("", "_Libro")
    )

    return report_df[
        [
            "ID",
            "Nombre",
            "Codigo",
            "Titulo",
            "Fecha_Prestamo",
            "Fecha_Prevista_Devolucion",
            "Estado",
        ]
    ]


def get_returns_report() -> pd.DataFrame:
    returns_df = read_sheet(SHEET_RETURNS)
    users_df = read_sheet(SHEET_USERS)
    books_df = read_sheet(SHEET_BOOKS)

    if returns_df.empty:
        return returns_df

    report_df = returns_df.merge(
        users_df[["ID", "Nombre"]],
        left_on="Usuario_ID",
        right_on="ID",
        how="left",
        suffixes=("", "_Usuario")
    )

    report_df = report_df.merge(
        books_df[["ID", "Codigo", "Titulo"]],
        left_on="Libro_ID",
        right_on="ID",
        how="left",
        suffixes=("", "_Libro")
    )

    return report_df[
        [
            "ID",
            "Nombre",
            "Codigo",
            "Titulo",
            "Fecha_Devolucion",
            "Dias_Atraso",
        ]
    ]


def get_overdue_loans() -> pd.DataFrame:
    loans_report_df = get_loans_report()

    if loans_report_df.empty:
        return loans_report_df

    today = pd.Timestamp.today().date()

    loans_report_df["Fecha_Prevista_Devolucion"] = pd.to_datetime(
        loans_report_df["Fecha_Prevista_Devolucion"]
    ).dt.date

    overdue_df = loans_report_df[
        (loans_report_df["Estado"] == "Activo")
        &
        (loans_report_df["Fecha_Prevista_Devolucion"] < today)
    ]

    return overdue_df