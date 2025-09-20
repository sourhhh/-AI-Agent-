from typing import List, Dict, Literal
from dataclasses import dataclass, field
from .base_schema import BaseSchema
import json


@dataclass
class Defect(BaseSchema):
    type: Literal["syntax", "security", "logic", "performance", "code_smell"]
    message: str
    line_number: int
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    tool: Literal["pylint", "bandit", "llm", "mypy"]
    confidence: float = 0.8


@dataclass
class FileDefects(BaseSchema):
    file_path: str
    defects: List[Defect] = field(default_factory=list)


@dataclass
class DefectReport(BaseSchema):
    files: List[FileDefects] = field(default_factory=list)
    summary: Dict[str, int] = field(default_factory=dict)

    @classmethod
    def from_json(cls, json_str: str):
        """从JSON字符串创建对象"""
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict) -> 'DefectReport':
        """从字典创建DefectReport对象"""
        files = []
        for file_data in data.get('files', []):
            defects = []
            for defect_data in file_data.get('defects', []):
                defect = Defect(
                    type=defect_data['type'],
                    message=defect_data['message'],
                    line_number=defect_data['line_number'],
                    severity=defect_data['severity'],
                    tool=defect_data['tool'],
                    confidence=defect_data.get('confidence', 0.8)
                )
                defects.append(defect)

            file_defects = FileDefects(
                file_path=file_data['file_path'],
                defects=defects
            )
            files.append(file_defects)

        return cls(
            files=files,
            summary=data.get('summary', {})
        )