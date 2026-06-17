import os
import sqlite3
from typing import List

from .models import AlbumRecord


SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS albums (
  jm_id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  link TEXT NOT NULL DEFAULT '',
  pdf_path TEXT NOT NULL DEFAULT '',
  cover_path TEXT NOT NULL DEFAULT '',
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
        self.conn.commit()

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

    def upsert_album(self, record: AlbumRecord) -> None:
        conn = self._require_conn()
        with conn:
            conn.execute(
                """
                INSERT INTO albums (jm_id, title, link, pdf_path, cover_path, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(jm_id) DO UPDATE SET
                  title=excluded.title,
                  link=excluded.link,
                  pdf_path=excluded.pdf_path,
                  cover_path=excluded.cover_path,
                  updated_at=CURRENT_TIMESTAMP
                """,
                (record.jm_id, record.title, record.link, record.pdf_path, record.cover_path),
            )
            conn.execute('DELETE FROM album_authors WHERE jm_id = ?', (record.jm_id,))
            conn.execute('DELETE FROM album_tags WHERE jm_id = ?', (record.jm_id,))
            conn.execute('DELETE FROM chapters WHERE jm_id = ?', (record.jm_id,))

            for author in record.authors:
                author_id = self._id_for('authors', author)
                conn.execute('INSERT OR IGNORE INTO album_authors VALUES (?, ?)', (record.jm_id, author_id))

            for tag in record.tags:
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
            authors=authors,
            tags=tags,
            chapters=chapters,
        )
