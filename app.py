import streamlit as st
from datetime import date

from modules.books import create_book, get_all_books, update_book, delete_book
from modules.users import create_user, get_all_users, update_user, delete_user
from modules.loans import create_loan, get_all_loans, get_active_loans
from modules.returns import create_return, get_all_returns
from services.dashboard_service import (
    get_dashboard_metrics,
    get_loans_report,
    get_overdue_loans,
    get_returns_report,
)
from services.excel_service import initialize_database


st.set_page_config(
    page_title="Sistema de Gestión de Biblioteca",
    layout="wide"
)

initialize_database()

st.title("Sistema de Gestión de Biblioteca")

def show_dataframe(df):
    st.dataframe(
        df,
        width="stretch",
        hide_index=True
    )

menu = st.sidebar.selectbox(
    "Menú",
    [
        "Libros",
        "Usuarios",
        "Préstamos",
        "Devoluciones",
        "Informes",
    ]
)

if menu == "Libros":
    st.header("Gestión de Libros")

    with st.form("book_form", clear_on_submit=True):
        st.subheader("Registrar nuevo libro")

        code = st.text_input("Código")
        title = st.text_input("Título")
        author = st.text_input("Autor")
        publisher = st.text_input("Editora")

        total_quantity = st.number_input(
            "Cantidad total",
            min_value=1,
            step=1
        )

        submitted = st.form_submit_button("Registrar libro")

        if submitted:
            if (
                not code.strip()
                or not title.strip()
                or not author.strip()
                or not publisher.strip()
            ):
                st.error("Todos los campos son obligatorios.")
            else:
                try:
                    create_book(
                        code=code,
                        title=title,
                        author=author,
                        publisher=publisher,
                        total_quantity=int(total_quantity),
                    )
                    st.rerun()

                except ValueError as error:
                    st.error(str(error))

    st.divider()
    st.subheader("Buscar libro")

    search_term = st.text_input(
        "Buscar por código, título, autor o editora"
    )

    st.subheader("Libros registrados")

    books_df = get_all_books()

    if search_term:
        search_term = search_term.lower()

        books_df = books_df[
            books_df["Codigo"].astype(str).str.lower().str.contains(search_term)
            |
            books_df["Titulo"].astype(str).str.lower().str.contains(search_term)
            |
            books_df["Autor"].astype(str).str.lower().str.contains(search_term)
            |
            books_df["Editora"].astype(str).str.lower().str.contains(search_term)
        ]

    if books_df.empty:
        st.info("No hay libros registrados.")
    else:
        books_display = books_df.rename(
            columns={
                "Codigo": "Código",
                "Titulo": "Título",
                "Cantidad_Total": "Total",
                "Cantidad_Disponible": "Disponibles",
                "Observaciones": "Etiquetas",
            }
        )

        books_display = books_display[
            [
                "Código",
                "Título",
                "Autor",
                "Editora",
                "Total",
                "Disponibles",
                "Etiquetas",
            ]
        ]

        selected_event = st.dataframe(
            books_display,
            width="stretch",
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )

        selected_rows = selected_event.selection.rows

        if selected_rows:
            selected_index = selected_rows[0]
            selected_book_id = int(books_df.iloc[selected_index]["ID"])

            selected_book = books_df[
                books_df["ID"] == selected_book_id
            ].iloc[0]

            st.info(
                f'Libro seleccionado: {selected_book["Codigo"]} - {selected_book["Titulo"]}'
            )

            col_edit, col_delete = st.columns(2)

            with col_edit:
                if st.button("Editar libro"):
                    st.session_state["selected_book_id"] = selected_book_id
                    st.session_state["book_action"] = "edit"

            with col_delete:
                if st.button("Eliminar libro"):
                    st.session_state["selected_book_id"] = selected_book_id
                    st.session_state["book_action"] = "delete"
        else:
            st.session_state["selected_book_id"] = None
            st.session_state["book_action"] = None       

    if st.session_state.get("book_action") == "edit":
        selected_book_id = st.session_state.get("selected_book_id")

        selected_book = books_df[
            books_df["ID"] == selected_book_id
        ].iloc[0]

        st.divider()
        st.subheader("Modificar libro")

        with st.form("update_book_form"):
            updated_code = st.text_input(
                "Código",
                value=str(selected_book["Codigo"])
            )

            updated_title = st.text_input(
                "Título",
                value=str(selected_book["Titulo"])
            )

            updated_author = st.text_input(
                "Autor",
                value=str(selected_book["Autor"])
            )

            updated_publisher = st.text_input(
                "Editora",
                value=str(selected_book["Editora"])
            )

            updated_total_quantity = st.number_input(
                "Cantidad total",
                min_value=1,
                step=1,
                value=int(selected_book["Cantidad_Total"])
            )

            submitted_update = st.form_submit_button("Actualizar libro")

            if submitted_update:
                try:
                    update_book(
                        book_id=selected_book_id,
                        code=updated_code,
                        title=updated_title,
                        author=updated_author,
                        publisher=updated_publisher,
                        total_quantity=int(updated_total_quantity),
                    )

                    st.session_state["book_action"] = None
                    st.session_state["selected_book_id"] = None
                    st.rerun()

                except ValueError as error:
                    st.error(str(error))

    if st.session_state.get("book_action") == "delete":
        selected_book_id = st.session_state.get("selected_book_id")

        selected_book = books_df[
            books_df["ID"] == selected_book_id
        ].iloc[0]

        st.divider()
        st.subheader("Eliminar libro")

        st.warning(
            f'Libro seleccionado: {selected_book["Codigo"]} - {selected_book["Titulo"]}'
        )

        confirm_delete = st.checkbox(
            "Confirmo que deseo eliminar este libro."
        )

        if st.button("Confirmar eliminación"):
            if not confirm_delete:
                st.error("Debe confirmar antes de eliminar el libro.")
            else:
                try:
                    delete_book(selected_book_id)

                    st.session_state["book_action"] = None
                    st.session_state["selected_book_id"] = None
                    st.rerun()

                except ValueError as error:
                    st.error(str(error))

elif menu == "Usuarios":
    st.header("Gestión de Usuarios")

    with st.form("user_form", clear_on_submit=True):
        st.subheader("Registrar nuevo usuario")

        name = st.text_input("Nombre")
        phone = st.text_input("Teléfono")

        submitted = st.form_submit_button("Registrar usuario")

        if submitted:
            if not name.strip() or not phone.strip():
                st.error("Todos los campos son obligatorios.")
            else:
                try:
                    create_user(
                        name=name,
                        phone=phone
                    )
                    st.rerun()

                except ValueError as error:
                    st.error(str(error))

    st.divider()
    st.subheader("Buscar usuario")

    search_user = st.text_input(
        "Buscar por nombre o teléfono"
    )

    st.subheader("Usuarios registrados")

    users_df = get_all_users()

    if search_user:
        search_user = search_user.lower()

        users_df = users_df[
            users_df["Nombre"].astype(str).str.lower().str.contains(search_user)
            |
            users_df["Telefono"].astype(str).str.lower().str.contains(search_user)
        ]

    if users_df.empty:
        st.info("No hay usuarios registrados.")
    else:
        users_display = users_df.rename(
            columns={
                "Nombre": "Nombre",
                "Telefono": "Teléfono",
            }
        )

        users_display = users_display[
            [
                "Nombre",
                "Teléfono",
            ]
        ]

        selected_event = st.dataframe(
            users_display,
            width="stretch",
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )

        selected_rows = selected_event.selection.rows

        if selected_rows:
            selected_index = selected_rows[0]
            selected_user_id = int(users_df.iloc[selected_index]["ID"])

            selected_user = users_df[
                users_df["ID"] == selected_user_id
            ].iloc[0]

            st.info(
                f'Usuario seleccionado: {selected_user["Nombre"]} - {selected_user["Telefono"]}'
            )

            col_edit, col_delete = st.columns(2)

            with col_edit:
                if st.button("Editar usuario"):
                    st.session_state["selected_user_id"] = selected_user_id
                    st.session_state["user_action"] = "edit"

            with col_delete:
                if st.button("Eliminar usuario"):
                    st.session_state["selected_user_id"] = selected_user_id
                    st.session_state["user_action"] = "delete"

        else:
            st.session_state["selected_user_id"] = None
            st.session_state["user_action"] = None

    if st.session_state.get("user_action") == "edit":
        selected_user_id = st.session_state.get("selected_user_id")

        selected_user = users_df[
            users_df["ID"] == selected_user_id
        ].iloc[0]

        st.divider()
        st.subheader("Modificar usuario")

        with st.form("update_user_form"):
            updated_name = st.text_input(
                "Nombre",
                value=str(selected_user["Nombre"])
            )

            updated_phone = st.text_input(
                "Teléfono",
                value=str(selected_user["Telefono"])
            )

            submitted_update = st.form_submit_button("Actualizar usuario")

            if submitted_update:
                try:
                    update_user(
                        user_id=selected_user_id,
                        name=updated_name,
                        phone=updated_phone,
                    )

                    st.session_state["user_action"] = None
                    st.session_state["selected_user_id"] = None
                    st.rerun()

                except ValueError as error:
                    st.error(str(error))

    if st.session_state.get("user_action") == "delete":
        selected_user_id = st.session_state.get("selected_user_id")

        selected_user = users_df[
            users_df["ID"] == selected_user_id
        ].iloc[0]

        st.divider()
        st.subheader("Eliminar usuario")

        st.warning(
            f'Usuario seleccionado: {selected_user["Nombre"]} - {selected_user["Telefono"]}'
        )

        confirm_delete = st.checkbox(
            "Confirmo que deseo eliminar este usuario."
        )

        if st.button("Confirmar eliminación"):
            if not confirm_delete:
                st.error("Debe confirmar antes de eliminar el usuario.")
            else:
                try:
                    delete_user(selected_user_id)

                    st.session_state["user_action"] = None
                    st.session_state["selected_user_id"] = None
                    st.rerun()

                except ValueError as error:
                    st.error(str(error))

elif menu == "Préstamos":
    st.header("Gestión de Préstamos")

    users_df = get_all_users()
    books_df = get_all_books()

    if users_df.empty:
        st.warning("Debe registrar al menos un usuario antes de crear un préstamo.")

    elif books_df.empty:
        st.warning("Debe registrar al menos un libro antes de crear un préstamo.")

    else:
        with st.form("loan_form", clear_on_submit=True):
            st.subheader("Registrar nuevo préstamo")

            user_options = {
                row["Nombre"]: int(row["ID"])
                for _, row in users_df.iterrows()
            }

            selected_user = st.selectbox(
                "Usuario",
                options=[None] + list(user_options.keys()),
                format_func=lambda x: "Seleccione un usuario..." if x is None else x
            )

            available_books_df = books_df[
                books_df["Cantidad_Disponible"] > 0
            ]

            if available_books_df.empty:
                st.warning("No hay libros disponibles para préstamo.")
                submitted = False
            else:
                book_options = {
                    f'{row["Codigo"]} - {row["Titulo"]}': int(row["ID"])
                    for _, row in available_books_df.iterrows()
                }

                selected_book = st.selectbox(
                    "Libro",
                    options=[None] + list(book_options.keys()),
                    format_func=lambda x: "Seleccione un libro..." if x is None else x
                )

                loan_date = st.date_input(
                    "Fecha de préstamo",
                    value=date.today()
                )

                expected_return_date = st.date_input(
                    "Fecha prevista de devolución"
                )

                submitted = st.form_submit_button("Registrar préstamo")

                if submitted:
                    if selected_user is None:
                        st.error("Debe seleccionar un usuario.")

                    elif selected_book is None:
                        st.error("Debe seleccionar un libro.")

                    else:
                        try:
                            create_loan(
                                user_id=user_options[selected_user],
                                book_id=book_options[selected_book],
                                loan_date=str(loan_date),
                                expected_return_date=str(expected_return_date),
                            )

                            st.rerun()

                        except ValueError as error:
                            st.error(str(error))

    st.divider()
    st.subheader("Buscar préstamo")

    search_loan = st.text_input(
        "Buscar por usuario, código, título o estado"
    )

    st.subheader("Préstamos registrados")

    loans_report_df = get_loans_report()

    if search_loan:
        search_loan = search_loan.lower()

        loans_report_df = loans_report_df[
            loans_report_df["Nombre"].astype(str).str.lower().str.contains(search_loan)
            |
            loans_report_df["Codigo"].astype(str).str.lower().str.contains(search_loan)
            |
            loans_report_df["Titulo"].astype(str).str.lower().str.contains(search_loan)
            |
            loans_report_df["Estado"].astype(str).str.lower().str.contains(search_loan)
        ]

    if loans_report_df.empty:
        st.info("No hay préstamos registrados.")
    else:
        loans_display = loans_report_df.rename(
            columns={
                "Nombre": "Usuario",
                "Codigo": "Código",
                "Titulo": "Libro",
                "Fecha_Prestamo": "Fecha préstamo",
                "Fecha_Prevista_Devolucion": "Fecha prevista",
                "Estado": "Estado",
            }
        )

        loans_display = loans_display[
            [
                "Usuario",
                "Código",
                "Libro",
                "Fecha préstamo",
                "Fecha prevista",
                "Estado",
            ]
        ]

        selected_event = st.dataframe(
            loans_display,
            width="stretch",
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )

        selected_rows = selected_event.selection.rows

        if selected_rows:
            selected_index = selected_rows[0]
            selected_loan = loans_report_df.iloc[selected_index]

            st.info(
                f'Préstamo seleccionado: {selected_loan["Nombre"]} - '
                f'{selected_loan["Codigo"]} - {selected_loan["Titulo"]}'
            )

            st.write(f'**Usuario:** {selected_loan["Nombre"]}')
            st.write(f'**Código:** {selected_loan["Codigo"]}')
            st.write(f'**Libro:** {selected_loan["Titulo"]}')
            st.write(f'**Fecha préstamo:** {selected_loan["Fecha_Prestamo"]}')
            st.write(f'**Fecha prevista:** {selected_loan["Fecha_Prevista_Devolucion"]}')
            st.write(f'**Estado:** {selected_loan["Estado"]}')

elif menu == "Devoluciones":
    st.header("Gestión de Devoluciones")

    active_loans_df = get_active_loans()
    loans_report_df = get_loans_report()

    if active_loans_df.empty:
        st.info("No hay préstamos activos para devolver.")
    else:
        active_report_df = loans_report_df[
            loans_report_df["Estado"] == "Activo"
        ]

        with st.form("return_form", clear_on_submit=True):
            st.subheader("Registrar devolución")

            loan_options = {
                (
                    f'{row["Nombre"]} - {row["Codigo"]} - {row["Titulo"]} '
                    f'({row["Fecha_Prevista_Devolucion"]})'
                ): int(row["ID"])
                for _, row in active_report_df.iterrows()
            }

            selected_loan = st.selectbox(
                "Préstamo activo",
                options=[None] + list(loan_options.keys()),
                format_func=lambda x: "Seleccione un préstamo..." if x is None else x
            )

            return_date = st.date_input(
                "Fecha de devolución",
                value=date.today()
            )

            submitted = st.form_submit_button("Registrar devolución")

            if submitted:
                if selected_loan is None:
                    st.error("Debe seleccionar un préstamo activo.")
                else:
                    try:
                        create_return(
                            loan_id=loan_options[selected_loan],
                            return_date=str(return_date),
                        )
                        st.rerun()

                    except ValueError as error:
                        st.error(str(error))

    st.divider()
    st.subheader("Buscar devolución")

    search_return = st.text_input(
        "Buscar por usuario, código o título"
    )

    st.subheader("Devoluciones registradas")

    returns_report_df = get_returns_report()

    if search_return:
        search_return = search_return.lower()

        returns_report_df = returns_report_df[
            returns_report_df["Nombre"].astype(str).str.lower().str.contains(search_return)
            |
            returns_report_df["Codigo"].astype(str).str.lower().str.contains(search_return)
            |
            returns_report_df["Titulo"].astype(str).str.lower().str.contains(search_return)
        ]

    if returns_report_df.empty:
        st.info("No hay devoluciones registradas.")
    else:
        returns_display = returns_report_df.rename(
            columns={
                "Nombre": "Usuario",
                "Codigo": "Código",
                "Titulo": "Libro",
                "Fecha_Devolucion": "Fecha devolución",
                "Dias_Atraso": "Días atraso",
            }
        )

        returns_display = returns_display[
            [
                "Usuario",
                "Código",
                "Libro",
                "Fecha devolución",
                "Días atraso",
            ]
        ]

        selected_event = st.dataframe(
            returns_display,
            width="stretch",
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )

        selected_rows = selected_event.selection.rows

        if selected_rows:
            selected_index = selected_rows[0]
            selected_return = returns_report_df.iloc[selected_index]

            st.info(
                f'Devolución seleccionada: {selected_return["Nombre"]} - '
                f'{selected_return["Codigo"]} - {selected_return["Titulo"]}'
            )

            st.write(f'**Usuario:** {selected_return["Nombre"]}')
            st.write(f'**Código:** {selected_return["Codigo"]}')
            st.write(f'**Libro:** {selected_return["Titulo"]}')
            st.write(f'**Fecha devolución:** {selected_return["Fecha_Devolucion"]}')
            st.write(f'**Días atraso:** {selected_return["Dias_Atraso"]}')

elif menu == "Informes":
    st.header("Informes")

    metrics = get_dashboard_metrics()

    col1, col2, col3 = st.columns(3)
    col1.metric("Títulos registrados", metrics["total_titles"])
    col2.metric("Ejemplares totales", metrics["total_books"])
    col3.metric("Ejemplares disponibles", metrics["available_books"])

    col4, col5, col6 = st.columns(3)
    col4.metric("Usuarios", metrics["users"])
    col5.metric("Préstamos activos", metrics["active_loans"])
    col6.metric("Devoluciones con atraso", metrics["overdue_returns"])

    st.divider()

    st.subheader("Préstamos vencidos")

    overdue_df = get_overdue_loans()

    if overdue_df.empty:
        st.info("No hay préstamos vencidos.")
    else:
        show_dataframe(overdue_df)

    st.divider()

    st.subheader("Relatórios")

    report_tabs = st.tabs(
        ["Libros", "Préstamos", "Devoluciones"]
    )

    with report_tabs[0]:
        books_df = get_all_books()

        if books_df.empty:
            st.info("No hay libros registrados.")
        else:
            show_dataframe(books_df)

    with report_tabs[1]:
        loans_report_df = get_loans_report()

        if loans_report_df.empty:
            st.info("No hay préstamos registrados.")
        else:
            show_dataframe(loans_report_df)

    with report_tabs[2]:
        returns_report_df = get_returns_report()

        if returns_report_df.empty:
            st.info("No hay devoluciones registradas.")
        else:
            show_dataframe(returns_report_df)