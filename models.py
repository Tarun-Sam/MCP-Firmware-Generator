from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class CodeGenerationResponse(BaseModel):
    description: str
    generated_code: str
    file_path: Optional[str] = None
    compilation_status: Optional[str] = None
    compilation_output: Optional[str] = None
    detected_libraries: Optional[List[str]] = None
    error_summary: Optional[str] = None
    troubleshooting_suggestions: Optional[List[str]] = None
    documentation: Optional[str] = None
    installation_guide: Optional[str] = None

    hardware_info: Optional[Dict] = None
    code_quality_score: Optional[int] = None
    memory_usage: Optional[float] = None
    quality_issues: Optional[List[Dict[str, Any]]] = None
    quality_warnings: Optional[List[Dict[str, Any]]] = None


# 🔥 REQUIRED for Pydantic v2
CodeGenerationResponse.model_rebuild()
