"""Preenchimento assistido do Lattes, deliberadamente sem salvamento."""

from __future__ import annotations

from loguru import logger
from playwright.async_api import BrowserContext, Page

from .config import AppConfig
from .models import TccRecord


class SafetyViolation(RuntimeError):
    """Indica tentativa de executar uma ação proibida no Lattes."""


class LattesAssistant:
    """Preenche um registro revisado e entrega o controle ao usuário."""

    def __init__(self, context: BrowserContext, config: AppConfig) -> None:
        self._context = context
        self._config = config
        self._selectors = config.selectors["lattes"]

    async def open(self) -> Page:
        """Abre o Lattes para login e navegação manual do usuário."""
        page = await self._context.new_page()
        await page.goto(str(self._config.lattes["url"]))
        logger.info("Lattes aberto. Faça login e navegue até o formulário desejado.")
        return page

    async def fill_record(self, page: Page, record: TccRecord) -> None:
        """Preenche campos, mas nunca localiza nem aciona o botão Salvar."""
        if not record.reviewed:
            raise SafetyViolation(
                "O registro precisa estar marcado como revisado no CSV."
            )
        values = {
            "student_name": record.student_name,
            "title": record.title,
            "year": str(record.year),
            "institution": record.institution,
            "course": record.course,
        }
        for field, value in values.items():
            selector = self._selectors["fields"][field]
            locator = page.locator(selector)
            if await locator.count() != 1:
                raise RuntimeError(
                    f"Seletor do campo {field!r} não encontrou exatamente um elemento."
                )
            await locator.fill(value)
        type_selector = self._selectors["fields"]["work_type"]
        type_field = page.locator(type_selector)
        if await type_field.count() == 1:
            await type_field.select_option(label=record.work_type)
        logger.warning(
            "Campos preenchidos. Confira os dados e clique em Salvar manualmente."
        )
