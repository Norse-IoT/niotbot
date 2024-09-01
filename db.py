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

Base = declarative_base()
engine = create_engine("sqlite:///:memory:", echo=True)
Session: orm.Session = sessionmaker(bind=engine)


class Submission(Base):
    """Represents a submission from a discord message, and the associated thread

    A submission has many attachments"""

    __tablename__ = "submission"

    id: Mapped[int] = mapped_column(primary_key=True)
    date = Column(DateTime, nullable=False, default=datetime.now())

    discord_message_content: Mapped[Optional[str]]
    discord_message_id: Mapped[int] = Column(BigInteger, nullable=False)
    discord_thread_id: Mapped[int] = Column(BigInteger, nullable=False)
    discord_author_id: Mapped[int] = Column(BigInteger, nullable=False)
    discord_author_display_name: Mapped[str]
    discord_approval_message_id: Mapped[int] = Column(BigInteger, nullable=False)

    attachments: Mapped[list["Attachment"]] = relationship()


class Attachment(Base):
    """An attachment in discord"""

    __tablename__ = "attachment"

    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey("submission.id"))
    discord_attachment_id: Mapped[int] = Column(BigInteger, nullable=False)
    content_type: Mapped[str]
