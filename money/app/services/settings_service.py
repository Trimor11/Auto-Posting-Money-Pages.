from typing import Any, Dict

from sqlalchemy.orm import Session

from app.models import Setting


class SettingsService:
    def __init__(self, db: Session):
        self.db = db

    def get(self, key: str, default: Any = None) -> Any:
        setting = self.db.query(Setting).filter(Setting.key == key).first()
        if setting:
            return setting.value
        return default

    def set(self, key: str, value: Any) -> None:
        setting = self.db.query(Setting).filter(Setting.key == key).first()
        if not setting:
            setting = Setting(key=key, value=value)
            self.db.add(setting)
        else:
            setting.value = value
        self.db.commit()

    def bulk_set(self, values: Dict[str, Any]) -> None:
        for key, value in values.items():
            self.set(key, value)
