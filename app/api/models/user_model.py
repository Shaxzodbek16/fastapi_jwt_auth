from datetime import datetime, timezone, UTC, timedelta

from sqlalchemy import String, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship

from app.core.models import TimestampMixin, BaseModel


class User(BaseModel, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    password: Mapped[str] = mapped_column(Text, nullable=False)

    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # TODO: Add more fields as necessary


class VerificationCode(BaseModel):
    __tablename__ = "verification_codes"
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    code: Mapped[int] = mapped_column(Integer, index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    request_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    blocked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    @property
    def is_expired(self) -> bool:
        return datetime.now(UTC) > self.expires_at

    @property
    def is_blocked(self) -> bool:
        return self.blocked_until is not None and datetime.now(UTC) < self.blocked_until

    @staticmethod
    def generate_code() -> int:
        """returns a random 6 digit number"""
        import secrets

        return secrets.randbelow(900000) + 100000

    @staticmethod
    def generate_expiration() -> datetime:
        return datetime.now(UTC) + timedelta(minutes=10)

    @staticmethod
    def current_time() -> datetime:
        return datetime.now(UTC)

    def get_valid_time(self) -> timedelta:
        return self.expires_at - self.current_time()


class Token(TimestampMixin):
    __tablename__ = "tokens"
    # Foreignkey
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    # Fields
    token: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    is_revoked: Mapped[bool] = mapped_column(default=False)

    # relationships
    user = relationship("User", backref="refresh_tokens")

    @property
    def is_valid(self) -> bool:
        now = datetime.now(timezone.utc)
        return now < self.expires_at and not self.is_revoked

    def revoke(self):
        self.is_revoked = True
