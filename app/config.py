# sourcery skip: avoid-builtin-shadow
import os
from dataclasses import MISSING, dataclass, fields

import toml

@dataclass
class ConfigWeb:
    host: str
    port: int

    def get_config(self):
        return {
            "host": self.host,
            "port": self.port,
        }


@dataclass
class ConfigToken:
    main: str

    def get_config(self):
        return {
            "main": self.main,
        }

@dataclass
class ConfigDatabase:
    models: list[str]
    protocol: str = "sqlite"
    file_name: str = "production-database.sqlite3"
    user: str = None
    password: str = None
    host: str = None
    port: str = None

    def get_db_url(self):
        if self.protocol == "sqlite":
            return f"{self.protocol}://{self.file_name}"
        return f"{self.protocol}://{self.user}:{self.password}@{self.host}:{self.port}"

    def get_tortoise_config(self):
        return {
            "connections": {"default": self.get_db_url()},
            "apps": {
                "models": {
                    "models": self.models,
                    "default_connection": "default",
                },
            },
        }

@dataclass
class Config:
    web: ConfigWeb
    database: ConfigDatabase
    token: ConfigToken

    @classmethod
    def parse(cls, data: dict) -> "Config":
        sections = {}

        for section in fields(cls):
            pre = {}
            current = data[section.name]

            for field in fields(section.type):
                if field.name in current:
                    pre[field.name] = current[field.name]
                elif field.default is not MISSING:
                    pre[field.name] = field.default
                else:
                    raise ValueError(
                        f"Missing field {field.name} in section {section.name}"
                    )

            sections[section.name] = section.type(**pre)

        return cls(**sections)


def parse_config(config_file: str = "config.toml") -> Config:
    if not os.path.isfile(config_file) and not config_file.endswith(".toml"):
        config_file += ".toml"

    if not os.path.isfile(config_file):
        raise FileNotFoundError(f"Config file not found: {config_file} no such file")

    with open(config_file, "r") as f:
        data = toml.load(f)

    return Config.parse(dict(data))
