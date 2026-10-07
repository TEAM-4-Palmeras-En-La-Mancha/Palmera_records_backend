from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from controller.album_controller import (
    get_all,
    get_by_id,
    create_albums,
    update_album,
    delete_Album,
    get_by_record_label,
)
from model.album_model import Album
from model.artist_model import Artist
from model.genre_model import Genre
from model.record_labels_model import RecordLabel
from schema.album_schema import AlbumCreate, AlbumUpdate


# ============================================================================
# AYUDANTE: db.query() cuando se consultan VARIAS tablas
# ============================================================================

def _db_query(album=None, label=None, genres=None, artists=None):
    """
    Devuelve una función para usarla como db.query.side_effect.

    ¿Por qué hace falta?
    create_albums() hace varias consultas: db.query(RecordLabel),
    db.query(Genre) y db.query(Artist).

    Si usamos db_mock.query.return_value (como en el workshop), las tres
    llamadas devolverían EXACTAMENTE lo mismo y el test mentiría.

    Con side_effect, cada llamada pasa por esta función y devuelve un mock
    distinto según la tabla (la entidad) que se pida.
    """
    def _query(entity):
        q = MagicMock()

        if entity is Album:
            q.filter.return_value.first.return_value = album
        elif entity is RecordLabel:
            q.filter.return_value.first.return_value = label
        elif entity is Genre:
            q.filter.return_value.all.return_value = [] if genres is None else genres
        elif entity is Artist:
            q.filter.return_value.all.return_value = [] if artists is None else artists

        return q

    return _query


# ============================================================================
# TESTS: get_all
# ============================================================================

def test_get_all_success_happy_path():
    """
    Test obtención de la lista completa de álbumes (Happy Path).
    Metodología AAA: Arrange, Act, Assert.
    """
    # -----------------------------
    # 1. ARRANGE (Preparación)
    # -----------------------------
    db_mock = MagicMock()
    esperados = [
        Album(id=1, title="Dummy", release_year=2001, label_id=1),
        Album(id=2, title="Nonagon Infinity", release_year=2016, label_id=1),
    ]

    # Simulamos la cadena real: db.query().offset().limit().all()
    db_mock.query.return_value.offset.return_value.limit.return_value.all.return_value = esperados

    # -----------------------------
    # 2. ACT (Acción)
    # -----------------------------
    result = get_all(db=db_mock, skip=0, limit=100)

    # -----------------------------
    # 3. ASSERT (Verificación)
    # -----------------------------
    assert result == esperados
    assert len(result) == 2
    db_mock.query.assert_called_once_with(Album)


def test_get_all_db_error_unhappy_path():
    """
    Test fallo al listar álbumes por error de base de datos (Unhappy Path).
    Metodología AAA: Arrange, Act, Assert.
    """
    # -----------------------------
    # 1. ARRANGE (Preparación)
    # -----------------------------
    db_mock = MagicMock()
    # db.query() lanza un error de SQLAlchemy en cuanto se le llama
    db_mock.query.side_effect = SQLAlchemyError("Disco corrupto")

    # -----------------------------
    # 2. ACT & 3. ASSERT (Acción y Verificación)
    # -----------------------------
    with pytest.raises(HTTPException) as exc_info:
        get_all(db=db_mock)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Database error in getting albums" in exc_info.value.detail


# ============================================================================
# TESTS: get_by_id
# ============================================================================

def test_get_by_id_found_happy_path():
    """
    Test obtención exitosa de un álbum existente por ID (Happy Path).
    Metodología AAA: Arrange, Act, Assert.
    """
    # -----------------------------
    # 1. ARRANGE (Preparación)
    # -----------------------------
    db_mock = MagicMock()
    esperado = Album(id=1, title="Dummy", release_year=2001, label_id=1)

    # Simulamos la cadena real: db.query().filter().first()
    db_mock.query.return_value.filter.return_value.first.return_value = esperado

    # -----------------------------
    # 2. ACT (Acción)
    # -----------------------------
    result = get_by_id(db=db_mock, album_id=1)

    # -----------------------------
    # 3. ASSERT (Verificación)
    # -----------------------------
    assert result is esperado
    assert result.id == 1
    assert result.title == "Dummy"
    db_mock.query.assert_called_once_with(Album)


def test_get_by_id_not_found_unhappy_path():
    """
    Test búsqueda de un álbum que NO existe (Unhappy Path).
    OJO: aquí NUESTRO controlador lanza un 404, no devuelve None
    como hacía el workshop. Por eso usamos pytest.raises.
    Metodología AAA: Arrange, Act, Assert.
    """
    # -----------------------------
    # 1. ARRANGE (Preparación)
    # -----------------------------
    db_mock = MagicMock()
    # first() devuelve None cuando no encuentra el registro
    db_mock.query.return_value.filter.return_value.first.return_value = None

    # -----------------------------
    # 2. ACT & 3. ASSERT (Acción y Verificación)
    # -----------------------------
    with pytest.raises(HTTPException) as exc_info:
        get_by_id(db=db_mock, album_id=999)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Album not found"


def test_get_by_id_db_error_unhappy_path():
    """
    Test fallo en la consulta por error de base de datos (Unhappy Path).
    Metodología AAA: Arrange, Act, Assert.
    """
    # -----------------------------
    # 1. ARRANGE (Preparación)
    # -----------------------------
    db_mock = MagicMock()
    db_mock.query.side_effect = SQLAlchemyError("Error de lectura")

    # -----------------------------
    # 2. ACT & 3. ASSERT (Acción y Verificación)
    # -----------------------------
    with pytest.raises(HTTPException) as exc_info:
        get_by_id(db=db_mock, album_id=1)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Database error in getting album" in exc_info.value.detail


# ============================================================================
# TESTS: create_albums
# ============================================================================

def test_create_album_success_happy_path():
    """
    Test creación exitosa de un álbum SIN portada (Happy Path).
    Metodología AAA: Arrange, Act, Assert.
    """
    # -----------------------------
    # 1. ARRANGE (Preparación)
    # -----------------------------
    db_mock = MagicMock()

    # Objetos que "viven" en la base de datos (simulados)
    sello = RecordLabel(id=1, name="Domino Recording", country="United Kingdom")
    genero = Genre(id=1, name="Rock")
    artista = Artist(id=1, name="Black midi", bio="Banda británica")

    # El controlador consulta 3 tablas distintas -> usamos el ayudante
    db_mock.query.side_effect = _db_query(
        label=sello,
        genres=[genero],
        artists=[artista],
    )

    album_data = AlbumCreate(
        title="Nonagon Infinity",
        release_year=2016,
        label_id=1,
        genre_ids=[1],
        artist_ids=[1],
    )

    # -----------------------------
    # 2. ACT (Acción)
    # -----------------------------
    result = create_albums(db=db_mock, album_data=album_data)

    # -----------------------------
    # 3. ASSERT (Verificación)
    # -----------------------------
    # Comprobamos que se guardó en la base de datos
    db_mock.add.assert_called_once_with(result)
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once_with(result)

    # Comprobamos los datos del álbum creado
    assert isinstance(result, Album)
    assert result.title == "Nonagon Infinity"
    assert result.release_year == 2016
    assert result.label_id == 1

    # Sin portada -> no se sube nada a Cloudinary
    assert result.cover_image_url is None
    assert result.cover_image_public_id is None

    # Comprobamos las relaciones M:N
    assert list(result.genres) == [genero]
    assert list(result.artists) == [artista]


@patch("controller.album_controller.cloudinary_service.upload_image")
def test_create_album_con_portada_happy_path(mock_upload):
    """
    Test creación de un álbum CON portada (Happy Path).
    Se parchea Cloudinary para que NO se suba nada a internet.
    Metodología AAA: Arrange, Act, Assert.
    """
    # -----------------------------
    # 1. ARRANGE (Preparación)
    # -----------------------------
    # Cloudinary devolvería esto si funcionara de verdad
    mock_upload.return_value = {
        "secure_url": "https://res.cloudinary.com/demo/cover.jpg",
        "public_id": "palmeras_records/albums/cover",
    }

    db_mock = MagicMock()
    sello = RecordLabel(id=1, name="Domino Recording", country="United Kingdom")
    genero = Genre(id=1, name="Indie Rock")
    artista = Artist(id=1, name="Arctic Monkeys")

    db_mock.query.side_effect = _db_query(
        label=sello,
        genres=[genero],
        artists=[artista],
    )

    album_data = AlbumCreate(
        title="Tranquility Base",
        release_year=2018,
        label_id=1,
        genre_ids=[1],
        artist_ids=[1],
    )

    # Falso UploadFile: solo necesitamos que tenga un atributo .file
    cover = MagicMock()

    # -----------------------------
    # 2. ACT (Acción)
    # -----------------------------
    result = create_albums(db=db_mock, album_data=album_data, cover_image=cover)

    # -----------------------------
    # 3. ASSERT (Verificación)
    # -----------------------------
    # Se llamó a Cloudinary UNA vez con el fichero y la carpeta correcta
    mock_upload.assert_called_once_with(
        cover.file,
        folder="palmeras_records/albums",
    )
    assert result.cover_image_url == "https://res.cloudinary.com/demo/cover.jpg"
    assert result.cover_image_public_id == "palmeras_records/albums/cover"
    db_mock.commit.assert_called_once()


def test_create_album_label_not_found_unhappy_path():
    """
    Test creación con un sello discográfico inexistente (Unhappy Path).
    Metodología AAA: Arrange, Act, Assert.
    """
    # -----------------------------
    # 1. ARRANGE (Preparación)
    # -----------------------------
    db_mock = MagicMock()
    genero = Genre(id=1, name="Rock")
    artista = Artist(id=1, name="Black midi")

    # label=None simula que el sello NO existe en la base de datos
    db_mock.query.side_effect = _db_query(
        label=None,
        genres=[genero],
        artists=[artista],
    )

    album_data = AlbumCreate(
        title="Álbum sin sello",
        release_year=2020,
        label_id=999,
        genre_ids=[1],
        artist_ids=[1],
    )

    # -----------------------------
    # 2. ACT & 3. ASSERT (Acción y Verificación)
    # -----------------------------
    with pytest.raises(HTTPException) as exc_info:
        create_albums(db=db_mock, album_data=album_data)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Label not found"

    # Como falla antes de guardar, NO se debe tocar la base de datos
    db_mock.add.assert_not_called()
    db_mock.commit.assert_not_called()


def test_create_album_genre_not_found_unhappy_path():
    """
    Test creación con un género inexistente (Unhappy Path).
    El controlador compara: nº de géneros pedidos vs nº devueltos.
    Metodología AAA: Arrange, Act, Assert.
    """
    # -----------------------------
    # 1. ARRANGE (Preparación)
    # -----------------------------
    db_mock = MagicMock()
    sello = RecordLabel(id=1, name="Domino Recording", country="United Kingdom")
    artista = Artist(id=1, name="Black midi")

    # Pedimos genre_ids=[1] pero la base de datos devuelve 0 géneros
    # 0 != 1  ->  el controlador lanza el 404
    db_mock.query.side_effect = _db_query(
        label=sello,
        genres=[],
        artists=[artista],
    )

    album_data = AlbumCreate(
        title="Álbum sin género",
        release_year=2020,
        label_id=1,
        genre_ids=[1],
        artist_ids=[1],
    )

    # -----------------------------
    # 2. ACT & 3. ASSERT (Acción y Verificación)
    # -----------------------------
    with pytest.raises(HTTPException) as exc_info:
        create_albums(db=db_mock, album_data=album_data)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Genre not found"
    db_mock.commit.assert_not_called()


def test_create_album_artist_not_found_unhappy_path():
    """
    Test creación con un artista inexistente (Unhappy Path).
    Misma lógica que el género: nº pedido vs nº devuelto.
    Metodología AAA: Arrange, Act, Assert.
    """
    # -----------------------------
    # 1. ARRANGE (Preparación)
    # -----------------------------
    db_mock = MagicMock()
    sello = RecordLabel(id=1, name="Domino Recording", country="United Kingdom")
    genero = Genre(id=1, name="Rock")

    # Pedimos artist_ids=[1] pero la base de datos devuelve 0 artistas
    db_mock.query.side_effect = _db_query(
        label=sello,
        genres=[genero],
        artists=[],
    )

    album_data = AlbumCreate(
        title="Álbum sin artista",
        release_year=2020,
        label_id=1,
        genre_ids=[1],
        artist_ids=[1],
    )

    # -----------------------------
    # 2. ACT & 3. ASSERT (Acción y Verificación)
    # -----------------------------
    with pytest.raises(HTTPException) as exc_info:
        create_albums(db=db_mock, album_data=album_data)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Artist not found"
    db_mock.commit.assert_not_called()


def test_create_album_db_error_unhappy_path():
    """
    Test fallo al guardar el álbum en la base de datos (Unhappy Path).
    Verificamos que se hace ROLLBACK: lo más importante de este test.
    Metodología AAA: Arrange, Act, Assert.
    """
    # -----------------------------
    # 1. ARRANGE (Preparación)
    # -----------------------------
    db_mock = MagicMock()
    sello = RecordLabel(id=1, name="Domino Recording", country="United Kingdom")
    genero = Genre(id=1, name="Rock")
    artista = Artist(id=1, name="Black midi")

    db_mock.query.side_effect = _db_query(
        label=sello,
        genres=[genero],
        artists=[artista],
    )

    # Simulamos que el commit revienta
    db_mock.commit.side_effect = SQLAlchemyError("Disco lleno")

    album_data = AlbumCreate(
        title="Álbum con fallo",
        release_year=2020,
        label_id=1,
        genre_ids=[1],
        artist_ids=[1],
    )

    # -----------------------------
    # 2. ACT & 3. ASSERT (Acción y Verificación)
    # -----------------------------
    with pytest.raises(HTTPException) as exc_info:
        create_albums(db=db_mock, album_data=album_data)

    # Lo más importante: si el commit falla, SE DEBE DESHACER
    db_mock.rollback.assert_called_once()

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Database error in creating album" in exc_info.value.detail


# ============================================================================
# TESTS: update_album
# ============================================================================

def test_update_album_success_happy_path():
    """
    Test actualización de título y año de un álbum (Happy Path).
    No se tocan relaciones: solo Album, así usamos la cadena simple.
    Metodología AAA: Arrange, Act, Assert.
    """
    # -----------------------------
    # 1. ARRANGE (Preparación)
    # -----------------------------
    db_mock = MagicMock()
    existente = Album(id=1, title="Dummy", release_year=2001, label_id=1)
    db_mock.query.return_value.filter.return_value.first.return_value = existente

    update_data = AlbumUpdate(title="Dummy (Edición Expandida)", release_year=2004)

    # -----------------------------
    # 2. ACT (Acción)
    # -----------------------------
    result = update_album(db=db_mock, album_id=1, album_data=update_data)

    # -----------------------------
    # 3. ASSERT (Verificación)
    # -----------------------------
    assert result is existente
    assert result.title == "Dummy (Edición Expandida)"
    assert result.release_year == 2004
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once_with(existente)
    db_mock.rollback.assert_not_called()


def test_update_album_label_happy_path():
    """
    Test cambio de sello discográfico de un álbum (Happy Path).
    Aquí SÍ se consultan 2 tablas (Album y RecordLabel),
    así que usamos el ayudante _db_query.
    Metodología AAA: Arrange, Act, Assert.
    """
    # -----------------------------
    # 1. ARRANGE (Preparación)
    # -----------------------------
    db_mock = MagicMock()
    existente = Album(id=1, title="Dummy", release_year=2001, label_id=1)
    sello_nuevo = RecordLabel(id=2, name="4AD", country="United Kingdom")

    db_mock.query.side_effect = _db_query(album=existente, label=sello_nuevo)

    update_data = AlbumUpdate(label_id=2, title="Dummy (Reedición 4AD)")

    # -----------------------------
    # 2. ACT (Acción)
    # -----------------------------
    result = update_album(db=db_mock, album_id=1, album_data=update_data)

    # -----------------------------
    # 3. ASSERT (Verificación)
    # -----------------------------
    assert result.label_id == 2
    assert result.title == "Dummy (Reedición 4AD)"
    db_mock.commit.assert_called_once()
    db_mock.refresh.assert_called_once_with(existente)


def test_update_album_not_found_unhappy_path():
    """
    Test actualización de un álbum inexistente (Unhappy Path).
    NUESTRO controlador lanza 404, no devuelve None.
    Metodología AAA: Arrange, Act, Assert.
    """
    # -----------------------------
    # 1. ARRANGE (Preparación)
    # -----------------------------
    db_mock = MagicMock()
    db_mock.query.return_value.filter.return_value.first.return_value = None

    update_data = AlbumUpdate(title="Título Nuevo")

    # -----------------------------
    # 2. ACT & 3. ASSERT (Acción y Verificación)
    # -----------------------------
    with pytest.raises(HTTPException) as exc_info:
        update_album(db=db_mock, album_id=999, album_data=update_data)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Album not found"
    db_mock.commit.assert_not_called()


def test_update_album_label_not_found_unhappy_path():
    """
    Test cambio a un sello discográfico inexistente (Unhappy Path).
    Metodología AAA: Arrange, Act, Assert.
    """
    # -----------------------------
    # 1. ARRANGE (Preparación)
    # -----------------------------
    db_mock = MagicMock()
    existente = Album(id=1, title="Dummy", release_year=2001, label_id=1)

    # El álbum existe, pero el sello que pedimos NO
    db_mock.query.side_effect = _db_query(album=existente, label=None)

    update_data = AlbumUpdate(label_id=999)

    # -----------------------------
    # 2. ACT & 3. ASSERT (Acción y Verificación)
    # -----------------------------
    with pytest.raises(HTTPException) as exc_info:
        update_album(db=db_mock, album_id=1, album_data=update_data)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Record label not found"
    db_mock.commit.assert_not_called()


def test_update_album_db_error_unhappy_path():
    """
    Test fallo al guardar la actualización (Unhappy Path).
    Comprobamos que se hace ROLLBACK.
    Metodología AAA: Arrange, Act, Assert.
    """
    # -----------------------------
    # 1. ARRANGE (Preparación)
    # -----------------------------
    db_mock = MagicMock()
    existente = Album(id=1, title="Dummy", release_year=2001, label_id=1)
    db_mock.query.return_value.filter.return_value.first.return_value = existente

    db_mock.commit.side_effect = SQLAlchemyError("Conexión perdida")

    update_data = AlbumUpdate(title="Título Nuevo")

    # -----------------------------
    # 2. ACT & 3. ASSERT (Acción y Verificación)
    # -----------------------------
    with pytest.raises(HTTPException) as exc_info:
        update_album(db=db_mock, album_id=1, album_data=update_data)

    db_mock.rollback.assert_called_once()

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Database error in updating album" in exc_info.value.detail


# ============================================================================
# TESTS: delete_Album
# ============================================================================

def test_delete_album_success_happy_path():
    """
    Test eliminación de un álbum SIN portada (Happy Path).
    OJO: se llama delete_Album con A mayúscula, como en el controlador.
    Metodología AAA: Arrange, Act, Assert.
    """
    # -----------------------------
    # 1. ARRANGE (Preparación)
    # -----------------------------
    db_mock = MagicMock()
    existente = Album(
        id=1,
        title="Álbum a borrar",
        release_year=2020,
        label_id=1,
        cover_image_public_id=None,   # sin portada -> no toca Cloudinary
    )
    db_mock.query.return_value.filter.return_value.first.return_value = existente

    # -----------------------------
    # 2. ACT (Acción)
    # -----------------------------
    result = delete_Album(db=db_mock, album_id=1)

    # -----------------------------
    # 3. ASSERT (Verificación)
    # -----------------------------
    # El controlador no devuelve nada -> es None
    assert result is None
    db_mock.delete.assert_called_once_with(existente)
    db_mock.commit.assert_called_once()
    db_mock.rollback.assert_not_called()


@patch("controller.album_controller.cloudinary_service.delete_image")
def test_delete_album_con_portada_happy_path(mock_delete):
    """
    Test eliminación de un álbum CON portada (Happy Path).
    Comprobamos que se borra también la imagen de Cloudinary.
    Metodología AAA: Arrange, Act, Assert.
    """
    # -----------------------------
    # 1. ARRANGE (Preparación)
    # -----------------------------
    db_mock = MagicMock()
    existente = Album(
        id=1,
        title="Álbum con portada",
        release_year=2020,
        label_id=1,
        cover_image_public_id="palmeras_records/albums/cover",  # sí tiene portada
    )
    db_mock.query.return_value.filter.return_value.first.return_value = existente

    # -----------------------------
    # 2. ACT (Acción)
    # -----------------------------
    result = delete_Album(db=db_mock, album_id=1)

    # -----------------------------
    # 3. ASSERT (Verificación)
    # -----------------------------
    # Se borró la imagen en Cloudinary con ese public_id exacto
    mock_delete.assert_called_once_with("palmeras_records/albums/cover")
    assert result is None
    db_mock.delete.assert_called_once_with(existente)
    db_mock.commit.assert_called_once()


def test_delete_album_not_found_unhappy_path():
    """
    Test eliminación de un álbum inexistente (Unhappy Path).
    Metodología AAA: Arrange, Act, Assert.
    """
    # -----------------------------
    # 1. ARRANGE (Preparación)
    # -----------------------------
    db_mock = MagicMock()
    db_mock.query.return_value.filter.return_value.first.return_value = None

    # -----------------------------
    # 2. ACT & 3. ASSERT (Acción y Verificación)
    # -----------------------------
    with pytest.raises(HTTPException) as exc_info:
        delete_Album(db=db_mock, album_id=999)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Album not found"
    db_mock.delete.assert_not_called()
    db_mock.commit.assert_not_called()


def test_delete_album_db_error_unhappy_path():
    """
    Test fallo al eliminar el álbum (Unhappy Path).
    Comprobamos que se hace ROLLBACK.
    Metodología AAA: Arrange, Act, Assert.
    """
    # -----------------------------
    # 1. ARRANGE (Preparación)
    # -----------------------------
    db_mock = MagicMock()
    existente = Album(
        id=1,
        title="Álbum con fallo",
        release_year=2020,
        label_id=1,
        cover_image_public_id=None,
    )
    db_mock.query.return_value.filter.return_value.first.return_value = existente
    db_mock.commit.side_effect = SQLAlchemyError("Disco lleno")

    # -----------------------------
    # 2. ACT & 3. ASSERT (Acción y Verificación)
    # -----------------------------
    with pytest.raises(HTTPException) as exc_info:
        delete_Album(db=db_mock, album_id=1)

    db_mock.rollback.assert_called_once()

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Database error in deleting album" in exc_info.value.detail


# ============================================================================
# TESTS: get_by_record_label
# ============================================================================

def test_get_by_record_label_success_happy_path():
    """
    Test obtención de los álbumes de un sello concreto (Happy Path).
    Metodología AAA: Arrange, Act, Assert.
    """
    # -----------------------------
    # 1. ARRANGE (Preparación)
    # -----------------------------
    db_mock = MagicMock()
    esperados = [
        Album(id=1, title="Dummy", release_year=2001, label_id=1),
        Album(id=2, title="Nonagon Infinity", release_year=2016, label_id=1),
    ]
    # db.query().filter().all()
    db_mock.query.return_value.filter.return_value.all.return_value = esperados

    # -----------------------------
    # 2. ACT (Acción)
    # -----------------------------
    result = get_by_record_label(db=db_mock, label_id=1)

    # -----------------------------
    # 3. ASSERT (Verificación)
    # -----------------------------
    assert result == esperados
    assert len(result) == 2
    db_mock.query.assert_called_once_with(Album)


def test_get_by_record_label_db_error_unhappy_path():
    """
    Test fallo al consultar los álbumes de un sello (Unhappy Path).
    Metodología AAA: Arrange, Act, Assert.
    """
    # -----------------------------
    # 1. ARRANGE (Preparación)
    # -----------------------------
    db_mock = MagicMock()
    db_mock.query.side_effect = SQLAlchemyError("Error de red")

    # -----------------------------
    # 2. ACT & 3. ASSERT (Acción y Verificación)
    # -----------------------------
    with pytest.raises(HTTPException) as exc_info:
        get_by_record_label(db=db_mock, label_id=1)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Database error in fetching albums" in exc_info.value.detail