"""Gerenciamento do ciclo de vida do Playwright."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from playwright.async_api import BrowserContext, Playwright, async_playwright

from .config import BrowserSettings


@asynccontextmanager
async def browser_context(
    settings: BrowserSettings,
) -> AsyncIterator[BrowserContext]:
    """Abre um Chromium e garante o encerramento de todos os recursos."""
    playwright: Playwright | None = None
    browser = None
    try:
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(
            headless=settings.headless,
            slow_mo=settings.slow_mo_ms,
        )
        context = await browser.new_context(locale="pt-BR")
        context.set_default_timeout(settings.timeout_ms)
        yield context
    finally:
        if browser is not None:
            await browser.close()
        if playwright is not None:
            await playwright.stop()
