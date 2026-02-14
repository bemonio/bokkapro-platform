from urllib.parse import urlencode

SUPPORTED_LOCALES = {"en", "es"}
DEFAULT_LOCALE = "en"

TRANSLATIONS = {
    "en": {
        "common": {
            "app_name": "Bokkapro Platform",
            "back": "Back",
            "save": "Save",
            "actions": "Actions",
            "coming_soon": "Coming soon.",
            "language": "Language",
            "spanish": "Español",
            "english": "English",
        },
        "menu": {
            "dashboard": "Dashboard",
            "offices": "Offices",
            "vehicles": "Vehicles",
            "crews": "Crews",
            "tasks": "Tasks",
            "routes": "Routes",
        },
        "dashboard": {
            "title": "Dashboard",
            "manage_offices": "Manage office records.",
            "manage_vehicles": "Manage vehicle records.",
        },
        "vehicles": {
            "title": "Vehicles",
            "new_vehicle": "New Vehicle",
            "search_placeholder": "Search vehicles...",
            "name": "Name",
            "plate": "Plate",
            "office": "Office",
            "max_capacity": "Max Capacity",
            "view": "View",
            "edit": "Edit",
            "delete": "Delete",
            "delete_title": "Delete Vehicle",
            "delete_question": "Are you sure you want to delete {name}?",
            "delete_warning": "This action cannot be undone.",
            "cancel": "Cancel",
            "no_results": "No vehicles found.",
            "total": "Total",
            "prev": "Prev",
            "next": "Next",
            "page_of": "Page {page} / {total_pages}",
            "page_size": "{size} / page",
            "form_view_title": "Vehicle #{vehicle_id}",
            "form_edit_title": "Edit Vehicle #{vehicle_id}",
            "form_new_title": "New Vehicle",
            "select_office": "Select an office",
        },
        "offices": {
            "title": "Offices",
            "new_office": "New Office",
            "search_placeholder": "Search offices...",
            "name": "Name",
            "address": "Address",
            "coordinates": "Coordinates",
            "storage": "Storage",
            "view": "View",
            "edit": "Edit",
            "delete": "Delete",
            "delete_title": "Delete Office",
            "delete_question": "Are you sure you want to delete {name}?",
            "delete_warning": "This action cannot be undone.",
            "cancel": "Cancel",
            "no_results": "No offices found.",
            "total": "Total",
            "prev": "Prev",
            "next": "Next",
            "page_of": "Page {page} / {total_pages}",
            "page_size": "{size} / page",
            "form_view_title": "Office #{office_id}",
            "form_edit_title": "Edit Office #{office_id}",
            "form_new_title": "New Office",
            "latitude": "Latitude",
            "longitude": "Longitude",
            "map_location": "Map location",
            "showing_coordinates": "Showing coordinates",
            "storage_capacity": "Storage Capacity",
            "name_required": "Name is required",
            "storage_required": "Storage capacity is required",
        },
    },
    "es": {
        "common": {
            "app_name": "Plataforma Bokkapro",
            "back": "Volver",
            "save": "Guardar",
            "actions": "Acciones",
            "coming_soon": "Próximamente.",
            "language": "Idioma",
            "spanish": "Español",
            "english": "Inglés",
        },
        "menu": {
            "dashboard": "Panel",
            "offices": "Oficinas",
            "vehicles": "Vehículos",
            "crews": "Cuadrillas",
            "tasks": "Tareas",
            "routes": "Rutas",
        },
        "dashboard": {
            "title": "Panel",
            "manage_offices": "Gestiona los registros de oficinas.",
            "manage_vehicles": "Gestiona los registros de vehículos.",
        },
        "vehicles": {
            "title": "Vehículos",
            "new_vehicle": "Nuevo vehículo",
            "search_placeholder": "Buscar vehículos...",
            "name": "Nombre",
            "plate": "Placa",
            "office": "Oficina",
            "max_capacity": "Capacidad máxima",
            "view": "Ver",
            "edit": "Editar",
            "delete": "Eliminar",
            "delete_title": "Eliminar vehículo",
            "delete_question": "¿Seguro que quieres eliminar {name}?",
            "delete_warning": "Esta acción no se puede deshacer.",
            "cancel": "Cancelar",
            "no_results": "No se encontraron vehículos.",
            "total": "Total",
            "prev": "Anterior",
            "next": "Siguiente",
            "page_of": "Página {page} / {total_pages}",
            "page_size": "{size} / página",
            "form_view_title": "Vehículo #{vehicle_id}",
            "form_edit_title": "Editar vehículo #{vehicle_id}",
            "form_new_title": "Nuevo vehículo",
            "select_office": "Selecciona una oficina",
        },
        "offices": {
            "title": "Oficinas",
            "new_office": "Nueva oficina",
            "search_placeholder": "Buscar oficinas...",
            "name": "Nombre",
            "address": "Dirección",
            "coordinates": "Coordenadas",
            "storage": "Almacenamiento",
            "view": "Ver",
            "edit": "Editar",
            "delete": "Eliminar",
            "delete_title": "Eliminar oficina",
            "delete_question": "¿Seguro que quieres eliminar {name}?",
            "delete_warning": "Esta acción no se puede deshacer.",
            "cancel": "Cancelar",
            "no_results": "No se encontraron oficinas.",
            "total": "Total",
            "prev": "Anterior",
            "next": "Siguiente",
            "page_of": "Página {page} / {total_pages}",
            "page_size": "{size} / página",
            "form_view_title": "Oficina #{office_id}",
            "form_edit_title": "Editar oficina #{office_id}",
            "form_new_title": "Nueva oficina",
            "latitude": "Latitud",
            "longitude": "Longitud",
            "map_location": "Ubicación en mapa",
            "showing_coordinates": "Mostrando coordenadas",
            "storage_capacity": "Capacidad de almacenamiento",
            "name_required": "El nombre es obligatorio",
            "storage_required": "La capacidad de almacenamiento es obligatoria",
        },
    },
}


def normalize_locale(lang: str | None) -> str:
    if not lang:
        return DEFAULT_LOCALE
    candidate = lang.strip().lower()
    return candidate if candidate in SUPPORTED_LOCALES else DEFAULT_LOCALE


def translate(locale: str, key: str, **kwargs: object) -> str:
    section, message_key = key.split(".", maxsplit=1)
    messages = TRANSLATIONS.get(locale, TRANSLATIONS[DEFAULT_LOCALE])
    fallback_messages = TRANSLATIONS[DEFAULT_LOCALE]
    message = messages.get(section, {}).get(message_key) or fallback_messages.get(section, {}).get(message_key) or key
    return message.format(**kwargs)


def build_url(path: str, lang: str, **query_params: object) -> str:
    clean = {k: v for k, v in query_params.items() if v is not None and v != ""}
    clean["lang"] = lang
    query = urlencode(clean)
    return f"{path}?{query}" if query else path
