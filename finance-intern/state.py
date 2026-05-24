import json
from dataclasses import dataclass, field
from typing import List


@dataclass
class Evidence:
    source: str
    content: str
    timestamp: str


@dataclass
class WorkingHypothesis:
    claim: str
    evidence: List[Evidence] = field(default_factory=list)
    status: str = "unverified"


@dataclass
class ResearchState:
    question: str
    hypotheses: List[WorkingHypothesis] = field(default_factory=list)
    established_results: List[str] = field(default_factory=list)
    critiques: List[str] = field(default_factory=list)
    iteration: int = 0

    def save(self, filename="state.json"):
        with open(filename, "w") as f:
            json.dump(self.__dict__, f, indent=2, default=str)
        print(f"State saved at iteration {self.iteration}")

    def load(self, filename="state.json"):
        with open(filename, "r") as f:
            data = json.load(f)
        print(f"State loaded - iteration {data['iteration']}")
        return data
