"""Modelo relacional de Instagram. Ejecuta este archivo para generar diagram.png."""
from datetime import datetime
from pathlib import Path

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    # Solo almacena el hash; nunca la contraseÃ±a en claro.
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(100))
    bio: Mapped[str | None] = mapped_column(String(150))
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    posts: Mapped[list['Post']] = relationship(back_populates='author', cascade='all, delete-orphan')
    comments: Mapped[list['Comment']] = relationship(back_populates='author', cascade='all, delete-orphan')
    likes: Mapped[list['Like']] = relationship(back_populates='user', cascade='all, delete-orphan')
    # Son dos relaciones distintas hacia la misma tabla de usuarios.
    following: Mapped[list['Follow']] = relationship(foreign_keys='Follow.follower_id', back_populates='follower', cascade='all, delete-orphan')
    followers: Mapped[list['Follow']] = relationship(foreign_keys='Follow.followed_id', back_populates='followed', cascade='all, delete-orphan')

    def serialize(self):
        return {'id': self.id, 'username': self.username, 'full_name': self.full_name,
                'bio': self.bio, 'avatar_url': self.avatar_url}


class Post(db.Model):
    __tablename__ = 'post'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    caption: Mapped[str | None] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(String(150))
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    author: Mapped['User'] = relationship(back_populates='posts')
    media: Mapped[list['Media']] = relationship(back_populates='post', cascade='all, delete-orphan', order_by='Media.position')
    comments: Mapped[list['Comment']] = relationship(back_populates='post', cascade='all, delete-orphan')
    likes: Mapped[list['Like']] = relationship(back_populates='post', cascade='all, delete-orphan')

    def serialize(self):
        return {'id': self.id, 'user_id': self.user_id, 'caption': self.caption, 'location': self.location}


class Media(db.Model):
    __tablename__ = 'media'
    __table_args__ = (
        UniqueConstraint('post_id', 'position', name='uq_media_post_position'),
        CheckConstraint('position >= 0', name='ck_media_position'),
        CheckConstraint("media_type IN ('image', 'video')", name='ck_media_type'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey('post.id', ondelete='CASCADE'), nullable=False, index=True)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    media_type: Mapped[str] = mapped_column(String(10), nullable=False)
    # Permite varias fotos o vÃ­deos en una publicaciÃ³n sin perder su orden.
    position: Mapped[int] = mapped_column(nullable=False, default=0)
    alt_text: Mapped[str | None] = mapped_column(String(300))
    post: Mapped['Post'] = relationship(back_populates='media')

    def serialize(self):
        return {'id': self.id, 'post_id': self.post_id, 'url': self.url,
                'media_type': self.media_type, 'position': self.position, 'alt_text': self.alt_text}


class Comment(db.Model):
    __tablename__ = 'comment'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    post_id: Mapped[int] = mapped_column(ForeignKey('post.id', ondelete='CASCADE'), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    author: Mapped['User'] = relationship(back_populates='comments')
    post: Mapped['Post'] = relationship(back_populates='comments')

    def serialize(self):
        return {'id': self.id, 'user_id': self.user_id, 'post_id': self.post_id, 'content': self.content}


class Like(db.Model):
    __tablename__ = 'post_like'
    __table_args__ = (UniqueConstraint('user_id', 'post_id', name='uq_like_user_post'),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    post_id: Mapped[int] = mapped_column(ForeignKey('post.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    user: Mapped['User'] = relationship(back_populates='likes')
    post: Mapped['Post'] = relationship(back_populates='likes')

    def serialize(self):
        return {'id': self.id, 'user_id': self.user_id, 'post_id': self.post_id}


class Follow(db.Model):
    __tablename__ = 'follow'
    __table_args__ = (
        UniqueConstraint('follower_id', 'followed_id', name='uq_follow_pair'),
        CheckConstraint('follower_id <> followed_id', name='ck_follow_not_self'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    follower_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    followed_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    follower: Mapped['User'] = relationship(foreign_keys=[follower_id], back_populates='following')
    followed: Mapped['User'] = relationship(foreign_keys=[followed_id], back_populates='followers')

    def serialize(self):
        return {'id': self.id, 'follower_id': self.follower_id, 'followed_id': self.followed_id}


if __name__ == '__main__':
    from eralchemy2 import render_er
    destination = Path(__file__).resolve().parents[1] / 'diagram.png'
    # El diagrama usa los modelos actuales, no una base de datos desactualizada.
    render_er(db.metadata, str(destination))
    print(f'Diagrama generado: {destination}')
