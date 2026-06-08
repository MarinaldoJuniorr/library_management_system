import pandas as pd

from services.excel_service import read_sheet, save_sheet, get_next_id


SHEET_NAME = "Usuarios"


def get_all_users() -> pd.DataFrame:
    """
    Returns all users registered in the system.
    """
    return read_sheet(SHEET_NAME)


def get_user_by_id(user_id: int) -> pd.DataFrame:
    """
    Returns a user by its ID.
    """
    users_df = get_all_users()
    return users_df[users_df["ID"] == user_id]


def create_user(
    name: str,
    phone: str,
) -> None:
    """
    Creates a new user record.
    """
    name = name.strip()
    phone = phone.strip()


    if not name or not phone:
        raise ValueError("Todos los campos son obligatorios.")

    users_df = get_all_users()

    existing_user = users_df[
        (users_df["Nombre"].astype(str).str.lower() == name.lower())
    ]

    if not existing_user.empty:
        raise ValueError("Este usuario ya está registrado.")

    new_user = {
        "ID": get_next_id(SHEET_NAME),
        "Nombre": name,
        "Telefono": phone,
    }

    users_df = pd.concat(
        [users_df, pd.DataFrame([new_user])],
        ignore_index=True
    )

    save_sheet(SHEET_NAME, users_df)


def update_user(
    user_id: int,
    name: str,
    phone: str,
) -> None:
    """
    Updates an existing user record.
    """
    name = name.strip()
    phone = phone.strip()

    if not name or not phone:
        raise ValueError("Todos los campos son obligatorios.")

    users_df = get_all_users()

    if user_id not in users_df["ID"].values:
        raise ValueError("Usuario no encontrado.")

    users_df.loc[
        users_df["ID"] == user_id,
        ["Nombre", "Telefono"]
    ] = [name, phone]

    save_sheet(SHEET_NAME, users_df)


def delete_user(user_id: int) -> None:
    """
    Deletes a user by ID.
    """
    users_df = get_all_users()

    if user_id not in users_df["ID"].values:
        raise ValueError("Usuario no encontrado.")

    users_df = users_df[users_df["ID"] != user_id]

    save_sheet(SHEET_NAME, users_df)