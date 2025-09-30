from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from rdflib import Graph, Namespace, URIRef


DEFAULT_ONTO_NS_STR = "http://www.semanticweb.org/georg/ontologies/2025/8/untitled-ontology-3#"


@dataclass
class OntologyService:
	graph: Graph
	base_ns: Namespace

	@classmethod
	def from_file(cls, path: str) -> "OntologyService":
		graph = Graph()
		fmt: Optional[str] = None
		lower_path = path.lower()
		if lower_path.endswith(".rdf") or lower_path.endswith(".owl") or lower_path.endswith(".xml"):
			fmt = None
		else:
			with open(path, "rb") as f:
				start = f.read(256).lstrip()
			if start.startswith(b"<?xml") or start.startswith(b"<"):
				fmt = "application/rdf+xml"
		try:
			graph.parse(path, format=fmt)
		except Exception:
			try:
				graph.parse(path, format="application/rdf+xml")
			except Exception:
				graph.parse(path, format="turtle")

		base_ns_str = cls._detect_base_ns(graph) or DEFAULT_ONTO_NS_STR
		return cls(graph=graph, base_ns=Namespace(base_ns_str))

	@staticmethod
	def _detect_base_ns(graph: Graph) -> Optional[str]:
		q_person = """
		SELECT ?c WHERE {
			?c a <http://www.w3.org/2002/07/owl#Class> .
			FILTER(STRAFTER(STR(?c), "#") = "Person")
		}
		LIMIT 1
		"""
		for row in graph.query(q_person):
			iri = str(row[0])
			return iri.rsplit("#", 1)[0] + "#"
		q_prop = """
		SELECT ?p WHERE {
			?p a <http://www.w3.org/2002/07/owl#ObjectProperty> .
			FILTER(STRAFTER(STR(?p), "#") = "parentOf")
		}
		LIMIT 1
		"""
		for row in graph.query(q_prop):
			iri = str(row[0])
			return iri.rsplit("#", 1)[0] + "#"
		return None

	def _local(self, name: str) -> URIRef:
		return self.base_ns[name]

	def list_individuals(self) -> List[str]:
		q = f"""
		PREFIX onto: <{self.base_ns}>
		SELECT DISTINCT ?s WHERE {{
			?s a onto:Person .
		}}
		"""
		res = {str(row[0]).split("#")[-1] for row in self.graph.query(q)}
		q2 = f"""
		PREFIX onto: <{self.base_ns}>
		SELECT DISTINCT ?s WHERE {{
			{{ ?s a onto:Male }} UNION {{ ?s a onto:Female }}
		}}
		"""
		res.update(str(row[0]).split("#")[-1] for row in self.graph.query(q2))
		return sorted(res)

	def is_female(self, person_local: str) -> bool:
		q = f"""
		PREFIX onto: <{self.base_ns}>
		ASK {{ <{self._local(person_local)}> a onto:Female }}
		"""
		return bool(self.graph.query(q).askAnswer)

	def is_male(self, person_local: str) -> bool:
		q = f"""
		PREFIX onto: <{self.base_ns}>
		ASK {{ <{self._local(person_local)}> a onto:Male }}
		"""
		return bool(self.graph.query(q).askAnswer)

	# ---------- Base explicit relations ----------
	def _explicit_parents_of(self, person_local: str) -> List[str]:
		q = f"""
		PREFIX onto: <{self.base_ns}>
		SELECT DISTINCT ?p WHERE {{ ?p onto:parentOf <{self._local(person_local)}> }}
		"""
		return [str(row[0]).split("#")[-1] for row in self.graph.query(q)]

	def _explicit_grandparents_of(self, person_local: str) -> List[str]:
		q = f"""
		PREFIX onto: <{self.base_ns}>
		SELECT DISTINCT ?g WHERE {{ ?g onto:grandparentOf <{self._local(person_local)}> }}
		"""
		return [str(row[0]).split("#")[-1] for row in self.graph.query(q)]

	def _explicit_grandchildren_of(self, person_local: str) -> List[str]:
		q1 = f"""
		PREFIX onto: <{self.base_ns}>
		SELECT DISTINCT ?c WHERE {{ <{self._local(person_local)}> onto:grandparentOf ?c }}
		"""
		res = [str(row[0]).split("#")[-1] for row in self.graph.query(q1)]
		q2 = f"""
		PREFIX onto: <{self.base_ns}>
		SELECT DISTINCT ?c WHERE {{ ?c onto:grandsonOf <{self._local(person_local)}> }}
		"""
		res += [str(row[0]).split("#")[-1] for row in self.graph.query(q2)]
		return sorted(set(res))

	def _explicit_mother_of(self, person_local: str) -> List[str]:
		q = f"""
		PREFIX onto: <{self.base_ns}>
		SELECT DISTINCT ?m WHERE {{ ?m onto:motherOf <{self._local(person_local)}> }}
		"""
		return [str(row[0]).split("#")[-1] for row in self.graph.query(q)]

	def _explicit_father_of(self, person_local: str) -> List[str]:
		q = f"""
		PREFIX onto: <{self.base_ns}>
		SELECT DISTINCT ?f WHERE {{ ?f onto:fatherOf <{self._local(person_local)}> }}
		"""
		return [str(row[0]).split("#")[-1] for row in self.graph.query(q)]

	def _explicit_siblings_of(self, person_local: str) -> List[str]:
		q = f"""
		PREFIX onto: <{self.base_ns}>
		SELECT DISTINCT ?s WHERE {{
			{{ <{self._local(person_local)}> onto:sibling ?s }}
			UNION
			{{ ?s onto:sibling <{self._local(person_local)}> }}
		}}
		"""
		return [str(row[0]).split("#")[-1] for row in self.graph.query(q)]

	def _explicit_brothers_of(self, person_local: str) -> List[str]:
		# Only X brotherOf person_local (don't include person_local brotherOf X)
		q = f"""
		PREFIX onto: <{self.base_ns}>
		SELECT DISTINCT ?b WHERE {{ ?b onto:brotherOf <{self._local(person_local)}> }}
		"""
		return [str(row[0]).split("#")[-1] for row in self.graph.query(q)]

	def _explicit_sisters_of(self, person_local: str) -> List[str]:
		# Only X sisterOf person_local
		q = f"""
		PREFIX onto: <{self.base_ns}>
		SELECT DISTINCT ?s WHERE {{ ?s onto:sisterOf <{self._local(person_local)}> }}
		"""
		return [str(row[0]).split("#")[-1] for row in self.graph.query(q)]

	def _explicit_aunts_for(self, person_local: str) -> List[str]:
		q = f"""
		PREFIX onto: <{self.base_ns}>
		SELECT DISTINCT ?x WHERE {{ ?x onto:auntFor <{self._local(person_local)}> }}
		"""
		return [str(row[0]).split("#")[-1] for row in self.graph.query(q)]

	def _explicit_uncles_for(self, person_local: str) -> List[str]:
		q = f"""
		PREFIX onto: <{self.base_ns}>
		SELECT DISTINCT ?x WHERE {{ ?x onto:uncleFor <{self._local(person_local)}> }}
		"""
		return [str(row[0]).split("#")[-1] for row in self.graph.query(q)]

	def _explicit_cousins_for(self, person_local: str) -> List[str]:
		q = f"""
		PREFIX onto: <{self.base_ns}>
		SELECT DISTINCT ?c WHERE {{ ?c onto:cousinFor <{self._local(person_local)}> }}
		"""
		return [str(row[0]).split("#")[-1] for row in self.graph.query(q)]

	# ---------- Inferred (manual) rules from base triples ----------
	def children_of(self, person_local: str) -> List[str]:
		q = f"""
		PREFIX onto: <{self.base_ns}>
		SELECT DISTINCT ?c WHERE {{ <{self._local(person_local)}> onto:parentOf ?c }}
		"""
		return [str(row[0]).split("#")[-1] for row in self.graph.query(q)]

	def parents_of(self, person_local: str) -> List[str]:
		return self._explicit_parents_of(person_local)

	def grandparents_of(self, person_local: str) -> List[str]:
		exp = set(self._explicit_grandparents_of(person_local))
		inf: Set[str] = set()
		for p in self._explicit_parents_of(person_local):
			for gp in self._explicit_parents_of(p):
				inf.add(gp)
		return sorted(exp.union(inf))

	def grandchildren_of(self, person_local: str) -> List[str]:
		exp = set(self._explicit_grandchildren_of(person_local))
		inf: Set[str] = set()
		for ch in self.children_of(person_local):
			for gc in self.children_of(ch):
				inf.add(gc)
		return sorted(exp.union(inf))

	def mother_of(self, person_local: str) -> List[str]:
		exp = self._explicit_mother_of(person_local)
		if exp:
			return sorted(set(exp))
		return [p for p in self._explicit_parents_of(person_local) if self.is_female(p)]

	def father_of(self, person_local: str) -> List[str]:
		exp = self._explicit_father_of(person_local)
		if exp:
			return sorted(set(exp))
		return [p for p in self._explicit_parents_of(person_local) if self.is_male(p)]

	def siblings_of(self, person_local: str) -> List[str]:
		exp = set(self._explicit_siblings_of(person_local))
		q = f"""
		PREFIX onto: <{self.base_ns}>
		SELECT DISTINCT ?s WHERE {{
			?s onto:childOf ?p .
			<{self._local(person_local)}> onto:childOf ?p .
			FILTER (?s != <{self._local(person_local)}>)
		}}
		"""
		inf = {str(row[0]).split("#")[-1] for row in self.graph.query(q)}
		return sorted(exp.union(inf))

	def brothers_of(self, person_local: str) -> List[str]:
		exp = set(self._explicit_brothers_of(person_local))
		male_sibs = {s for s in self.siblings_of(person_local) if self.is_male(s)}
		return sorted(exp.union(male_sibs))

	def sisters_of(self, person_local: str) -> List[str]:
		exp = set(self._explicit_sisters_of(person_local))
		female_sibs = {s for s in self.siblings_of(person_local) if self.is_female(s)}
		return sorted(exp.union(female_sibs))

	def aunts_for(self, person_local: str) -> List[str]:
		exp = set(self._explicit_aunts_for(person_local))
		res: Set[str] = set(exp)
		for parent in self._explicit_parents_of(person_local):
			for sib in self.siblings_of(parent):
				if self.is_female(sib):
					res.add(sib)
		return sorted(res)

	def uncles_for(self, person_local: str) -> List[str]:
		exp = set(self._explicit_uncles_for(person_local))
		res: Set[str] = set(exp)
		for parent in self._explicit_parents_of(person_local):
			for sib in self.siblings_of(parent):
				if self.is_male(sib):
					res.add(sib)
		return sorted(res)

	def cousins_for(self, person_local: str) -> List[str]:
		exp = set(self._explicit_cousins_for(person_local))
		res: Set[str] = set(exp)
		for parent in self._explicit_parents_of(person_local):
			for sib in self.siblings_of(parent):
				for child in self.children_of(sib):
					res.add(child)
		return sorted(res)

	def male_cousins_for(self, person_local: str) -> List[str]:
		return [c for c in self.cousins_for(person_local) if self.is_male(c)]


def map_russian_relation_to_method() -> Dict[str, str]:
	return {
		"мать": "mother_of",
		"отец": "father_of",
		"родители": "parents_of",
		"братья_сёстры": "siblings_of",
		"братья": "brothers_of",
		"сестры": "sisters_of",
		"тети": "aunts_for",
		"дяди": "uncles_for",
		"кузены": "cousins_for",
		"двоюродные_братья": "male_cousins_for",
		"бабушки_дедушки": "grandparents_of",
		"внуки": "grandchildren_of",
	}
