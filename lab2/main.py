from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List

from ontology_queries import OntologyService, map_russian_relation_to_method


PROMPT = (
	"Введите строку: 'Я: <индивидуал>, ищу: <отношение1>;<отношение2>;...'\n"
	"Команды: help, list, exit.\n> "
)

# Accepts both punctuated and unpunctuated forms, Russian letters, underscores, hyphens
INPUT_RE = re.compile(
	r"^\s*я[:\s]+(?P<me>[\w\-а-яА-ЯёЁ]+)(?:[\s,]*(?:интересуют|ищу)[:\s]+(?P<rels>[\wа-яА-ЯёЁ_\-;\s,]+))?\s*$",
	re.UNICODE,
)

REL_SPLIT_RE = re.compile(r"[;\s,]+")


def normalize_text(s: str) -> str:
	# normalize ё -> е, lowercase
	return s.replace("Ё", "Е").replace("ё", "е").lower()


def parse_input_line(line: str) -> (str, List[str]):
	line = normalize_text(line)
	m = INPUT_RE.match(line)
	if not m:
		raise ValueError(
			"Некорректный ввод. Пример: 'Я mike ищу тети кузены' или 'Я: dmitriy_a, ищу: тети;кузены'"
		)
	me = m.group("me").strip()
	rels_str = m.group("rels")
	rels: List[str] = []
	if rels_str:
		rels = [r.strip() for r in REL_SPLIT_RE.split(rels_str) if r.strip()]
	return me, rels


def print_help() -> None:
	rel_map = map_russian_relation_to_method()
	print("Доступные команды:")
	print(" - help: показать помощь")
	print(" - list: показать всех индивидуалов из онтологии")
	print(" - exit: выйти")
	print("")
	print("Доступные отношения:")
	for r in rel_map.keys():
		print(f" - {r}")
	print("")
	print("Пример:")
	print(" Я mike ищу тети кузены")


def main() -> int:
	root = Path(__file__).resolve().parent.parent
	onto_path = root / "lab1_part2" / "lab1_full.rdf"
	if not onto_path.exists():
		print(f"Не найден файл онтологии: {onto_path}")
		return 1

	service = OntologyService.from_file(str(onto_path))

	orig_rel_map = map_russian_relation_to_method()
	rel_map_norm = {normalize_text(k): v for k, v in orig_rel_map.items()}

	print_help()
	while True:
		try:
			line = input(PROMPT)
		except EOFError:
			print("")
			break

		cmd = normalize_text(line.strip())
		if cmd in ("exit", "quit"):
			break
		if cmd == "help":
			print_help()
			continue
		if cmd == "list":
			inds = service.list_individuals()
			print("Индивидуалы:")
			for name in inds:
				print(f" - {name}")
			continue

		try:
			me, rels = parse_input_line(line)
		except ValueError as e:
			print(str(e))
			continue

		if not rels:
			print(f"Вы ввели индивидуал: {me}. Уточните, что ищете: 'ищу ...'")
			continue

		for rel in rels:
			nrel = normalize_text(rel)
			method_name = rel_map_norm.get(nrel)
			if not method_name:
				print(f"Неизвестное отношение: {rel}. Допустимые: {', '.join(orig_rel_map.keys())}")
				continue
			method = getattr(service, method_name)
			results = method(me)
			if results:
				print(f"{rel}: {', '.join(results)}")
			else:
				print(f"{rel}: нет данных")

	return 0


if __name__ == "__main__":
	sys.exit(main())
