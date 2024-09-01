from datetime import datetime

from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import BigInteger
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import orm
from sqlalchemy.orm import sessionmaker
from typing import Optional
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()
engine = create_engine("sqlite:///niotbot.db", echo=True)
Session: orm.Session = sessionmaker(bind=engine)


class Submission(Base):
    """Represents a submission from a discord message, and the associated thread

    A submission has many attachments"""

    __tablename__ = "submission"

    id: Mapped[int] = mapped_column(primary_key=True)
    date = Column(DateTime, nullable=False, default=datetime.now())
    posted: Mapped[bool] = mapped_column(default=False)

    discord_message_content: Mapped[Optional[str]]
    discord_message_id: Mapped[int] = Column(BigInteger, nullable=False)
    discord_thread_id: Mapped[int] = Column(BigInteger, nullable=False)
    discord_author_id: Mapped[int] = Column(BigInteger, nullable=False)
    discord_author_display_name: Mapped[str]
    discord_approval_message_id: Mapped[int] = Column(BigInteger, nullable=False)

    attachments: Mapped[list["Attachment"]] = relationship()
    reviews: Mapped[list["Review"]] = relationship()

    @hybrid_property
    def description(self) -> str:
        credit = f"Submitted by {self.discord_author_display_name}."
        if self.discord_message_content is not None:
            return f"{self.discord_message_content}\n\n{credit}"
        else:
            return credit


class Attachment(Base):
    """An attachment in discord"""

    __tablename__ = "attachment"

    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey("submission.id"))
    discord_attachment_id: Mapped[int] = Column(BigInteger, nullable=False)
    content_type: Mapped[str]


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey("submission.id"))
    date = Column(DateTime, nullable=False, default=datetime.now())

    approval: Mapped[bool]
    discord_user_id: Mapped[int] = Column(BigInteger, nullable=False)
    discord_user_display_name: Mapped[str]
