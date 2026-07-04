"""Carregamento e validação da configuração YAML."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class ConfigurationError(RuntimeError):
    """Indica configuração ausente ou inválida."""


@dataclass(frozen=True, slots=True)
class BrowserSettings:
    """Opções compartilhadas do Playwright."""

    headless: bool
    slow_mo_ms: int
    timeout_ms: int


@dataclass(frozen=True, slots=True)
class AppConfig:
    """Configuração completa da aplicação."""

    root: Path
    browser: BrowserSettings
    biblioteca: dict[str, Any]
    lattes: dict[str, Any]
    paths: dict[str, Path]
    selectors: dict[str, Any]


def _read_yaml(path: Path) -> dict[str, Any]:
    try:
        content = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ConfigurationError(f"Não foi possível ler {path}: {exc}") from exc
    if not isinstance(content, dict):
        raise ConfigurationError(f"{path} deve conter um objeto YAML.")
    return content


def load_config(root: Path | None = None) -> AppConfig:
    """Carrega ``config.yaml`` e ``selectors.yaml`` a partir da raiz."""
    project_root = (root or Path.cwd()).resolve()
    values = _read_yaml(project_root / "config" / "config.yaml")
    selectors = _read_yaml(project_root / "config" / "selectors.yaml")
    try:
        browser = BrowserSettings(
            headless=bool(values["browser"]["headless"]),
            slow_mo_ms=int(values["browser"]["slow_mo_ms"]),
            timeout_ms=int(values["browser"]["timeout_ms"]),
        )
        paths = {
            name: project_root / relative
            for name, relative in values["paths"].items()
        }
        return AppConfig(
            root=project_root,
            browser=browser,
            biblioteca=dict(values["biblioteca"]),
            lattes=dict(values["lattes"]),
            paths=paths,
            selectors=selectors,
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ConfigurationError(f"Configuração incompleta: {exc}") from exc
