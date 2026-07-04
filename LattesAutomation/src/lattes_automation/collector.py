"""Coletor paginado da Biblioteca da FURB."""

from __future__ import annotations

import re
import unicodedata
from urllib.parse import urljoin

from loguru import logger
from playwright.async_api import BrowserContext, Page

from .config import AppConfig
from .extraction import extract_record
from .models import TccRecord


def person_name_key(value: str) -> tuple[str, ...]:
    """Normaliza nomes, desconsiderando ordem, pontuação, acentos e datas."""
    value = re.sub(r"\b\d{4}\s*-\s*(?:\d{4})?\b", " ", value)
    value = unicodedata.normalize("NFKD", value)
    ascii_value = value.encode("ascii", "ignore").decode().casefold()
    return tuple(sorted(re.findall(r"[a-z]+", ascii_value)))


class BibliotecaCollector:
    """Pesquisa um orientador, percorre resultados e extrai detalhes."""

    def __init__(self, context: BrowserContext, config: AppConfig) -> None:
        self._context = context
        self._config = config
        self._selectors = config.selectors["biblioteca"]

    async def collect(self, advisor: str) -> list[TccRecord]:
        """Executa a coleta completa, sem qualquer acesso ao Lattes."""
        page = await self._context.new_page()
        try:
            await page.goto(str(self._config.biblioteca["search_url"]))
            authority_url = await self._find_authority(page, advisor)
            await page.goto(authority_url)
            links = await self._collect_authority_links(page)
            logger.info("{} páginas de detalhes encontradas.", len(links))
            return await self._extract_all(links)
        finally:
            await page.close()

    async def _find_authority(self, page: Page, advisor: str) -> str:
        """Pesquisa o nome e retorna o cabeçalho de autoridade correspondente."""
        await page.locator(self._selectors["search_type_author"]).check()
        await page.locator(self._selectors["search_input"]).fill(advisor)
        await page.locator(self._selectors["search_submit"]).click()
        await page.wait_for_load_state("domcontentloaded")
        candidates = page.locator(self._selectors["authority_links"])
        count = await candidates.count()
        if count == 0:
            raise RuntimeError(f"Nenhum autor encontrado para {advisor!r}.")
        entries: list[dict[str, str]] = await candidates.evaluate_all(
            """
            (nodes) => nodes.map((node) => ({
                text: (node.textContent || "").trim(),
                href: node.href
            }))
            """
        )
        expected_key = person_name_key(advisor)
        matches = [
            entry for entry in entries if person_name_key(entry["text"]) == expected_key
        ]
        if len(matches) != 1:
            raise RuntimeError(
                f"A busca encontrou {count} autores e {len(matches)} correspondências "
                f"exatas para {advisor!r}."
            )
        href = matches[0]["href"]
        if not href:
            raise RuntimeError("O resultado do autor não possui URL.")
        return urljoin(str(self._config.biblioteca["base_url"]), href)

    async def _collect_authority_links(self, page: Page) -> list[str]:
        """Percorre todas as páginas de obras do cabeçalho selecionado."""
        links: list[str] = []
        max_pages = int(self._config.biblioteca["max_pages"])
        page_urls = await page.locator(self._selectors["page_links"]).evaluate_all(
            "(nodes) => nodes.map((node) => node.href)"
        )
        pages = [page.url, *(str(url) for url in page_urls)]
        for page_number, page_url in enumerate(dict.fromkeys(pages), start=1):
            if page_number > max_pages:
                logger.warning("Limite de {} páginas atingido.", max_pages)
                break
            if page.url != page_url:
                await page.goto(page_url)
            await page.wait_for_load_state("domcontentloaded")
            raw_links = await page.locator(self._selectors["result_links"]).evaluate_all(
                "(nodes) => nodes.map((node) => node.href)"
            )
            links.extend(str(link) for link in raw_links)
            logger.debug("Página {}: {} links.", page_number, len(raw_links))
        return list(dict.fromkeys(links))

    async def _extract_all(self, links: list[str]) -> list[TccRecord]:
        detail_page = await self._context.new_page()
        records: list[TccRecord] = []
        raw_directory = self._config.paths["raw"]
        raw_directory.mkdir(parents=True, exist_ok=True)
        try:
            for index, link in enumerate(links, start=1):
                url = urljoin(str(self._config.biblioteca["base_url"]), link)
                try:
                    await detail_page.goto(url)
                    html = await detail_page.content()
                    (raw_directory / f"tcc_{index:04d}.html").write_text(
                        html, encoding="utf-8"
                    )
                    records.append(extract_record(html, url))
                    logger.info("Extraído {}/{}: {}", index, len(links), url)
                except Exception:
                    logger.exception("Falha ao extrair {}.", url)
        finally:
            await detail_page.close()
        return records
