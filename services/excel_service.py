from pathlib import Path

import pandas as pd


DATA_DIR = Path("data")
DATABASE_PATH = DATA_DIR / "library.xlsx"

SHEETS_COLUMNS = {
    "Libros": [
        "ID",
        "Codigo",
        "Titulo",
        "Autor",
        "Editora",
        "Cantidad_Total",
        "Cantidad_Disponible",
        "Observaciones",
    ],
    "Usuarios": [
    "ID",
    "Nombre",
    "Telefono",
    ],
    "Prestamos": [
        "ID",
        "Usuario_ID",
        "Libro_ID",
        "Fecha_Prestamo",
        "Fecha_Prevista_Devolucion",
        "Estado",
    ],
    "Devoluciones": [
        "ID",
        "Prestamo_ID",
        "Libro_ID",
        "Usuario_ID",
        "Fecha_Devolucion",
        "Dias_Atraso",
    ],
}


def initialize_database() -> None:
    DATA_DIR.mkdir(exist_ok=True)

    if not DATABASE_PATH.exists():
        with pd.ExcelWriter(DATABASE_PATH, engine="openpyxl") as writer:
            for sheet_name, columns in SHEETS_COLUMNS.items():
                df = pd.DataFrame(columns=columns)
                df.to_excel(writer, sheet_name=sheet_name, index=False)


def read_sheet(sheet_name: str) -> pd.DataFrame:
    initialize_database()

    if sheet_name not in SHEETS_COLUMNS:
        raise ValueError(f"Sheet '{sheet_name}' is not configured.")

    return pd.read_excel(DATABASE_PATH, sheet_name=sheet_name)


def save_sheet(sheet_name: str, df: pd.DataFrame) -> None:
    initialize_database()

    if sheet_name not in SHEETS_COLUMNS:
        raise ValueError(f"Sheet '{sheet_name}' is not configured.")

    all_sheets = {}

    for current_sheet in SHEETS_COLUMNS.keys():
        if current_sheet == sheet_name:
            all_sheets[current_sheet] = df
        else:
            all_sheets[current_sheet] = pd.read_excel(
                DATABASE_PATH,
                sheet_name=current_sheet
            )

    with pd.ExcelWriter(DATABASE_PATH, engine="openpyxl") as writer:
        for current_sheet, current_df in all_sheets.items():
            current_df.to_excel(
                writer,
                sheet_name=current_sheet,
                index=False
            )


def get_next_id(sheet_name: str) -> int:
    df = read_sheet(sheet_name)

    if df.empty:
        return 1

    return int(df["ID"].max()) + 1