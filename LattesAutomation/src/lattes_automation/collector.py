"""Coletor paginado da Biblioteca da FURB."""

from __future__ import annotations

from urllib.parse import urljoin

from loguru import logger
from playwright.async_api import BrowserContext, Page

from .config import AppConfig
from .extraction import extract_record
from .models import TccRecord


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
            await page.locator(self._selectors["search_input"]).fill(advisor)
            await page.locator(self._selectors["search_submit"]).click()
            links = await self._collect_result_links(page)
            logger.info("{} páginas de detalhes encontradas.", len(links))
            return await self._extract_all(links)
        finally:
            await page.close()

    async def _collect_result_links(self, page: Page) -> list[str]:
        links: list[str] = []
        visited_pages: set[str] = set()
        max_pages = int(self._config.biblioteca["max_pages"])
        for page_number in range(1, max_pages + 1):
            current_url = page.url
            if current_url in visited_pages:
                logger.warning("Paginação cíclica detectada em {}.", current_url)
                break
            visited_pages.add(current_url)
            await page.wait_for_load_state("domcontentloaded")
            raw_links = await page.locator(self._selectors["result_links"]).evaluate_all(
                "(nodes) => nodes.map((node) => node.href)"
            )
            links.extend(str(link) for link in raw_links)
            logger.debug("Página {}: {} links.", page_number, len(raw_links))
            next_link = page.locator(self._selectors["next_page"])
            if await next_link.count() == 0:
                break
            await next_link.click()
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
