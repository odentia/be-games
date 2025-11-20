from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class GameModel(Base):
    __tablename__ = "games"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    rawg_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    metacritic: Mapped[int | None]
    rating: Mapped[float | None] = mapped_column(Float)
    release_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    developer: Mapped[str | None] = mapped_column(String(255))
    publisher: Mapped[str | None] = mapped_column(String(255))
    background_image: Mapped[str | None] = mapped_column(String(512))
    website: Mapped[str | None] = mapped_column(String(512))
    playtime: Mapped[int | None]
    age_rating: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    platforms: Mapped[list[PlatformModel]] = relationship("PlatformModel", cascade="all, delete-orphan", back_populates="game")
    genres: Mapped[list[GenreModel]] = relationship("GenreModel", cascade="all, delete-orphan", back_populates="game")
    tags: Mapped[list[TagModel]] = relationship("TagModel", cascade="all, delete-orphan", back_populates="game")
    screenshots: Mapped[list[ScreenshotModel]] = relationship("ScreenshotModel", cascade="all, delete-orphan", back_populates="game")


class PlatformModel(Base):
    __tablename__ = "game_platforms"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    game_id: Mapped[str] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(128))

    game: Mapped[GameModel] = relationship(back_populates="platforms")


class GenreModel(Base):
    __tablename__ = "game_genres"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    game_id: Mapped[str] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(128))

    game: Mapped[GameModel] = relationship(back_populates="genres")


class TagModel(Base):
    __tablename__ = "game_tags"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    game_id: Mapped[str] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(128))

    game: Mapped[GameModel] = relationship(back_populates="tags")


class ScreenshotModel(Base):
    __tablename__ = "game_screenshots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    game_id: Mapped[str] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"))
    url: Mapped[str] = mapped_column(String(512))

    game: Mapped[GameModel] = relationship(back_populates="screenshots")
