import os
import sqlite3
from typing import List

from jmcomic.jm_toolkit import JmcomicText

from .models import AlbumRecord


SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS albums (
  jm_id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  link TEXT NOT NULL DEFAULT '',
  pdf_path TEXT NOT NULL DEFAULT '',
  cover_path TEXT NOT NULL DEFAULT '',
  album_dir TEXT NOT NULL DEFAULT '',
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS authors (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS tags (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS album_authors (
  jm_id TEXT NOT NULL,
  author_id INTEGER NOT NULL,
  PRIMARY KEY (jm_id, author_id),
  FOREIGN KEY (jm_id) REFERENCES albums(jm_id) ON DELETE CASCADE,
  FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS album_tags (
  jm_id TEXT NOT NULL,
  tag_id INTEGER NOT NULL,
  PRIMARY KEY (jm_id, tag_id),
  FOREIGN KEY (jm_id) REFERENCES albums(jm_id) ON DELETE CASCADE,
  FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS chapters (
  jm_id TEXT NOT NULL,
  chapter_id TEXT NOT NULL,
  chapter_index TEXT NOT NULL,
  title TEXT NOT NULL,
  PRIMARY KEY (jm_id, chapter_id, chapter_index),
  FOREIGN KEY (jm_id) REFERENCES albums(jm_id) ON DELETE CASCADE
);
"""


class ShelfDatabase:

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.conn = None

    def open(self) -> None:
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        self.conn = sqlite3.connect(self.filepath)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self._migrate()
        self.conn.commit()

    def _migrate(self) -> None:
        columns = {
            row['name'] for row in self.conn.execute('PRAGMA table_info(albums)').fetchall()
        }
        if 'album_dir' not in columns:
            self.conn.execute("ALTER TABLE albums ADD COLUMN album_dir TEXT NOT NULL DEFAULT ''")

    def close(self) -> None:
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def _require_conn(self):
        if self.conn is None:
            self.open()
        return self.conn

    def _id_for(self, table: str, name: str) -> int:
        conn = self._require_conn()
        conn.execute(f'INSERT OR IGNORE INTO {table} (name) VALUES (?)', (name,))
        row = conn.execute(f'SELECT id FROM {table} WHERE name = ?', (name,)).fetchone()
        return int(row['id'])

    def _normalize_tag(self, tag: str) -> str:
        return str(JmcomicText.to_zh_cn(tag)).strip()

    def upsert_album(self, record: AlbumRecord) -> None:
        conn = self._require_conn()
        with conn:
            conn.execute(
                """
                INSERT INTO albums (jm_id, title, link, pdf_path, cover_path, album_dir, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(jm_id) DO UPDATE SET
                  title=excluded.title,
                  link=excluded.link,
                  pdf_path=excluded.pdf_path,
                  cover_path=excluded.cover_path,
                  album_dir=excluded.album_dir,
                  updated_at=CURRENT_TIMESTAMP
                """,
                (record.jm_id, record.title, record.link, record.pdf_path, record.cover_path, record.album_dir),
            )
            conn.execute('DELETE FROM album_authors WHERE jm_id = ?', (record.jm_id,))
            conn.execute('DELETE FROM album_tags WHERE jm_id = ?', (record.jm_id,))
            conn.execute('DELETE FROM chapters WHERE jm_id = ?', (record.jm_id,))

            for author in record.authors:
                author_id = self._id_for('authors', author)
                conn.execute('INSERT OR IGNORE INTO album_authors VALUES (?, ?)', (record.jm_id, author_id))

            for tag in record.tags:
                tag = self._normalize_tag(tag)
                if not tag:
                    continue
                tag_id = self._id_for('tags', tag)
                conn.execute('INSERT OR IGNORE INTO album_tags VALUES (?, ?)', (record.jm_id, tag_id))

            for chapter in record.chapters:
                conn.execute(
                    'INSERT OR REPLACE INTO chapters VALUES (?, ?, ?, ?)',
                    (
                        record.jm_id,
                        str(chapter.get('id', '')),
                        str(chapter.get('index', '')),
                        str(chapter.get('title', '')),
                    ),
                )

    def delete_albums(self, jm_ids: list[str]) -> int:
        normalized = [str(jm_id).removeprefix('JM').removeprefix('jm') for jm_id in jm_ids]
        normalized = [jm_id for jm_id in normalized if jm_id]
        if not normalized:
            return 0
        conn = self._require_conn()
        with conn:
            deleted = 0
            for jm_id in normalized:
                cursor = conn.execute('DELETE FROM albums WHERE jm_id = ?', (jm_id,))
                deleted += cursor.rowcount
            return deleted

    def query_albums(self, query: str = '') -> List[AlbumRecord]:
        conn = self._require_conn()
        q = query.strip()
        if q.upper().startswith('JM') and q[2:].isdigit():
            q = q[2:]

        where = ''
        params = []
        if q:
            like = f'%{q}%'
            where = """
            WHERE a.jm_id LIKE ?
               OR a.title LIKE ?
               OR EXISTS (
                    SELECT 1 FROM album_authors aa
                    JOIN authors au ON au.id = aa.author_id
                    WHERE aa.jm_id = a.jm_id AND au.name LIKE ?
               )
               OR EXISTS (
                    SELECT 1 FROM album_tags at
                    JOIN tags t ON t.id = at.tag_id
                    WHERE at.jm_id = a.jm_id AND t.name LIKE ?
               )
            """
            params = [like, like, like, like]

        rows = conn.execute(
            f'SELECT * FROM albums a {where} ORDER BY updated_at DESC, jm_id DESC',
            params,
        ).fetchall()
        return [self._row_to_album(row) for row in rows]

    def list_tags(self) -> list[str]:
        conn = self._require_conn()
        rows = conn.execute(
            """
            SELECT DISTINCT t.name
            FROM tags t
            JOIN album_tags at ON at.tag_id = t.id
            ORDER BY t.name
            """
        ).fetchall()
        return [row['name'] for row in rows]

    def query_albums_by_tag(self, tag: str) -> List[AlbumRecord]:
        conn = self._require_conn()
        tag = self._normalize_tag(tag)
        rows = conn.execute(
            """
            SELECT a.*
            FROM albums a
            JOIN album_tags at ON at.jm_id = a.jm_id
            JOIN tags t ON t.id = at.tag_id
            WHERE t.name = ?
            ORDER BY a.updated_at DESC, a.jm_id DESC
            """,
            (tag,),
        ).fetchall()
        return [self._row_to_album(row) for row in rows]

    def _row_to_album(self, row) -> AlbumRecord:
        conn = self._require_conn()
        jm_id = row['jm_id']
        authors = [
            item['name'] for item in conn.execute(
                """
                SELECT au.name FROM authors au
                JOIN album_authors aa ON aa.author_id = au.id
                WHERE aa.jm_id = ?
                ORDER BY au.name
                """,
                (jm_id,),
            )
        ]
        tags = [
            item['name'] for item in conn.execute(
                """
                SELECT t.name FROM tags t
                JOIN album_tags at ON at.tag_id = t.id
                WHERE at.jm_id = ?
                ORDER BY t.name
                """,
                (jm_id,),
            )
        ]
        chapters = [
            {
                'id': item['chapter_id'],
                'index': item['chapter_index'],
                'title': item['title'],
            }
            for item in conn.execute(
                """
                SELECT chapter_id, chapter_index, title
                FROM chapters
                WHERE jm_id = ?
                ORDER BY chapter_index
                """,
                (jm_id,),
            )
        ]
        return AlbumRecord(
            jm_id=jm_id,
            title=row['title'],
            link=row['link'],
            pdf_path=row['pdf_path'],
            cover_path=row['cover_path'],
            album_dir=row['album_dir'],
            authors=authors,
            tags=tags,
            chapters=chapters,
        )
