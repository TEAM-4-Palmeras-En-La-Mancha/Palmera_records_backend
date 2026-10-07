"""Datos de demostración de Palmeras en la Mancha Records.

Se siembran automáticamente en el arranque (ver ``main.py``) solo si la
base de datos está vacía, de modo que sobreviven al disco efímero de
Render Free. Los datos son idénticos al fichero de referencia
``palmeras_records.sqlite3``.
"""

from decimal import Decimal

from core.database import SessionLocal
from model.album_format_model import AlbumFormat
from model.album_model import Album
from model.artist_model import Artist
from model.branch_model import Branch
from model.format_model import Format
from model.genre_model import Genre
from model.record_labels_model import RecordLabel

CLOUDINARY = "https://res.cloudinary.com/u34rknur/image/upload"

RECORD_LABELS = [
    (1, "Partisan Records", "Estados Unidos", "https://partisanrecords.com"),
    (2, "Go! Beat Records", "Reino Unido", "https://www.islandrecords.com"),
    (3, "Flightless Records", "Australia", "https://flightlessrecords.com"),
    (4, "Transgressive Records", "Reino Unido", "https://transgressiverecords.com"),
    (5, "Mushroom Pillow", "España", "https://mushroompillow.com"),
]

GENRES = [
    (2, "Rock"),
    (3, "Pop"),
    (4, "Electrónica"),
    (5, "Post-Punk"),
    (6, "Trip Hop"),
    (7, "Rock Psicodélico"),
    (8, "Indie Pop"),
    (9, "Noise Rock"),
]

FORMATS = [
    (1, 'Vinilo LP 12"', None),
    (2, "CD Digipak", None),
    (3, "Cassette Edición Limitada", None),
]

ARTISTS = [
    (1, "Fontaines D.C.",
     "Banda irlandesa de post-punk y rock alternativo formada en Dublín, "
     "reconocida por su sonido crudo y líricas poéticas sobre el desarraigo moderno."),
    (2, "Portishead",
     "Banda británica pionera del sonido trip hop de Bristol, caracterizada por "
     "sus atmósferas oscuras, texturas de vinilo lo-fi y la voz de Beth Gibbons."),
    (3, "King Gizzard & The Lizard Wizard",
     "Prolífica formación australiana de rock psicodélico, microtonal y garage rock, "
     "célebre por su experimentación constante de géneros y autogestión editorial."),
    (4, "Arlo Parks",
     "Cantautora y poeta británica referente del indie pop y neo-soul contemporáneo, "
     "galardonada con el Mercury Prize por su sensibilidad introspectiva."),
    (5, "Triángulo de Amor Bizarro",
     "Banda gallega pilar del noise rock, shoegaze y post-punk independiente nacional, "
     "con guitarras abrasivas y melodías de pop distorsionado."),
]

BRANCHES = [
    (1, "Madrid — Malasaña", "Calle de la Palma 42, 28004 Madrid", "+34 91 521 88 40"),
    (2, "Toledo — Sede Histórica", "Calle Santo Tomé 14, 45002 Toledo", "+34 925 25 61 19"),
    (3, "Barcelona — Gràcia", "Carrer del Torrent de l'Olla 68, 08012 Barcelona", "+34 932 18 45 12"),
]

# id, título, año, cover_image_url, cover_image_public_id, label_id, artist_ids, genre_ids
ALBUMS = [
    (1, "Skinty Fia", 2022,
     f"{CLOUDINARY}/v1791363546/palmeras_records/albums/pz2xswjcxsqgoekuofmw.jpg",
     "palmeras_records/albums/pz2xswjcxsqgoekuofmw", 1, [1], [5]),
    (2, "Dummy", 1994,
     f"{CLOUDINARY}/v1791363626/palmeras_records/albums/khocaa7r7d5akhcdkgyn.jpg",
     "palmeras_records/albums/khocaa7r7d5akhcdkgyn", 2, [2], [6]),
    (3, "Nonagon Infinity", 2016,
     f"{CLOUDINARY}/v1791363721/palmeras_records/albums/jar7wifimek7uk78qacn.jpg",
     "palmeras_records/albums/jar7wifimek7uk78qacn", 3, [3], [7]),
    (4, "Collapsed in Sunbeams", 2021,
     f"{CLOUDINARY}/v1791363806/palmeras_records/albums/iyuxfi4imgqe6lu9k0b4.jpg",
     "palmeras_records/albums/iyuxfi4imgqe6lu9k0b4", 4, [4], [8]),
    (5, "Año Santo", 2010,
     f"{CLOUDINARY}/v1791363874/palmeras_records/albums/nmenmaoncn9tgdsn7o0n.jpg",
     "palmeras_records/albums/nmenmaoncn9tgdsn7o0n", 5, [5], [9]),
]

# album_id, format_id, price, stock
ALBUM_FORMATS = [
    (1, 1, Decimal("26.50"), 12),
    (1, 2, Decimal("15.00"), 8),
    (2, 1, Decimal("23.50"), 15),
    (2, 3, Decimal("13.50"), 5),
    (3, 1, Decimal("29.00"), 10),
    (4, 2, Decimal("14.00"), 11),
    (5, 1, Decimal("21.50"), 7),
]


def seed_if_empty() -> bool:
    """Carga los datos de demo solo si la base de datos está vacía.

    Devuelve ``True`` si siembra y ``False`` si ya había datos.
    """
    db = SessionLocal()
    try:
        if db.query(Genre).first() is not None:
            return False

        labels = [RecordLabel(id=i, name=n, country=c, website=w)
                  for i, n, c, w in RECORD_LABELS]
        genres = [Genre(id=i, name=n) for i, n in GENRES]
        formats = [Format(id=i, name=n, description=d) for i, n, d in FORMATS]
        artists = [Artist(id=i, name=n, bio=b) for i, n, b in ARTISTS]
        branches = [Branch(id=i, name=n, address=a, phone=p)
                    for i, n, a, p in BRANCHES]

        db.add_all(labels + genres + formats + artists + branches)
        db.flush()

        artists_by_id = {a.id: a for a in artists}
        genres_by_id = {g.id: g for g in genres}

        for album_id, title, year, cover_url, cover_pid, label_id, artist_ids, genre_ids in ALBUMS:
            album = Album(
                id=album_id,
                title=title,
                release_year=year,
                cover_image_url=cover_url,
                cover_image_public_id=cover_pid,
                label_id=label_id,
            )
            album.artists.extend(artists_by_id[i] for i in artist_ids)
            album.genres.extend(genres_by_id[i] for i in genre_ids)
            db.add(album)

        db.flush()

        db.add_all(
            AlbumFormat(album_id=a, format_id=f, price=p, stock=s)
            for a, f, p, s in ALBUM_FORMATS
        )

        db.commit()
        return True
    except BaseException:
        db.rollback()
        raise
    finally:
        db.close()
