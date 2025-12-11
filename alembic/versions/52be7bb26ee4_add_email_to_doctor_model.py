"""add email to doctor model

Revision ID: 52be7bb26ee4
Revises: f140ccc9d660
Create Date: 2025-12-05 22:18:19.593414

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "52be7bb26ee4"
down_revision: Union[str, None] = "f140ccc9d660"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем колонку emails только если её ещё нет
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'doctors'
                  AND column_name = 'emails'
            ) THEN
                ALTER TABLE doctors ADD COLUMN emails VARCHAR(120);
            END IF;
        END
        $$;
        """
    )


def downgrade() -> None:
    # Удаляем колонку, только если она есть
    op.execute(
        """
        ALTER TABLE doctors
        DROP COLUMN IF EXISTS emails;
        """
    )
