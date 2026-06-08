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

    existing_phone = users_df[
        users_df["Telefono"].astype(str) == phone
    ]

    if not existing_phone.empty:
        raise ValueError("Este teléfono ya está registrado.")

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

    if user_id not in users_df["ID"].astype(int).values:
        raise ValueError("Usuario no encontrado.")

    existing_phone = users_df[
        (users_df["Telefono"].astype(str) == phone)
        &
        (users_df["ID"].astype(int) != int(user_id))
    ]

    if not existing_phone.empty:
        raise ValueError("Este teléfono ya está registrado.")

    users_df.loc[
        users_df["ID"].astype(int) == int(user_id),
        ["Nombre", "Telefono"]
    ] = [name, phone]

    save_sheet(SHEET_NAME, users_df)

def delete_user(user_id: int) -> None:
    """
    Deletes a user by ID only if the user has no active loans.
    """
    users_df = get_all_users()

    user_id = int(user_id)

    if user_id not in users_df["ID"].astype(int).values:
        raise ValueError("Usuario no encontrado.")

    loans_df = read_sheet("Prestamos")

    if not loans_df.empty:
        loans_df["Usuario_ID"] = loans_df["Usuario_ID"].astype(int)
        loans_df["Estado"] = loans_df["Estado"].astype(str)

        active_loans = loans_df[
            (loans_df["Usuario_ID"] == user_id)
            &
            (loans_df["Estado"].str.lower() == "activo")
        ]

        if not active_loans.empty:
            raise ValueError(
                "No se puede eliminar un usuario con préstamos activos."
            )

    users_df = users_df[
        users_df["ID"].astype(int) != user_id
    ]

    save_sheet(SHEET_NAME, users_df)