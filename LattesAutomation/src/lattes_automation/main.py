"""Interface de linha de comando."""

from __future__ import annotations

import argparse
import asyncio
from datetime import datetime
from pathlib import Path

from loguru import logger

from .browser import browser_context
from .collector import BibliotecaCollector
from .config import AppConfig, load_config
from .csv_service import read_records, write_records
from .lattes import LattesAssistant
from .logging import configure_logging
from .validation import validate_records


def build_parser() -> argparse.ArgumentParser:
    """Monta os comandos públicos da aplicação."""
    parser = argparse.ArgumentParser(prog="lattes-automation")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--verbose", action="store_true")
    commands = parser.add_subparsers(dest="command", required=True)

    collect = commands.add_parser("collect", help="Coleta TCCs e gera CSV.")
    collect.add_argument("--advisor", required=True, help="Nome completo do orientador.")
    collect.add_argument("--output", type=Path)

    validate = commands.add_parser("validate", help="Valida um CSV intermediário.")
    validate.add_argument("csv", type=Path)

    fill = commands.add_parser("fill", help="Preenche um registro revisado no Lattes.")
    fill.add_argument("csv", type=Path)
    fill.add_argument("--row", type=int, required=True, help="Linha de dados, iniciando em 1.")
    return parser


async def _collect(config: AppConfig, advisor: str, output: Path | None) -> int:
    async with browser_context(config.browser) as context:
        records = await BibliotecaCollector(context, config).collect(advisor)
    destination = output or config.paths["exported"] / (
        f"tccs_{datetime.now():%Y%m%d_%H%M%S}.csv"
    )
    count = write_records(records, destination)
    logger.info("{} registros gravados em {}.", count, destination)
    return 0 if count else 1


def _validate(path: Path) -> int:
    records = read_records(path)
    issues = validate_records(records)
    for issue in issues:
        logger.warning("Linha {} [{}]: {}", issue.row, issue.severity, issue.message)
    logger.info("{} registros; {} ocorrências.", len(records), len(issues))
    return 1 if any(issue.severity == "erro" for issue in issues) else 0


async def _fill(config: AppConfig, path: Path, row: int) -> int:
    records = read_records(path)
    if row < 1 or row > len(records):
        raise ValueError(f"Linha deve estar entre 1 e {len(records)}.")
    async with browser_context(config.browser) as context:
        assistant = LattesAssistant(context, config)
        page = await assistant.open()
        input("Após login e abertura do formulário, pressione Enter...")
        await assistant.fill_record(page, records[row - 1])
        input("Revise no navegador. Pressione Enter para encerrar sem salvar...")
    return 0


def main() -> int:
    """Executa o comando solicitado e converte falhas em logs."""
    args = build_parser().parse_args()
    config = load_config(args.root)
    configure_logging(config.paths["logs"], args.verbose)
    try:
        if args.command == "collect":
            return asyncio.run(_collect(config, args.advisor, args.output))
        if args.command == "validate":
            return _validate(args.csv)
        if args.command == "fill":
            return asyncio.run(_fill(config, args.csv, args.row))
    except (KeyboardInterrupt, EOFError):
        logger.warning("Operação cancelada pelo usuário.")
        return 130
    except Exception:
        logger.exception("A operação falhou.")
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
