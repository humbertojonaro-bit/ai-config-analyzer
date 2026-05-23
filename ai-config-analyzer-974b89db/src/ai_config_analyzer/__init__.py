"""AI Config Analyzer - inspect and validate configuration files across formats."""

from ai_config_analyzer.analyzer import AnalysisResult, Analyzer
from ai_config_analyzer.findings import Finding, Severity
from ai_config_analyzer.parser import ParseError, detect_format, parse_file, parse_string

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "Analyzer",
    "AnalysisResult",
    "Finding",
    "Severity",
    "ParseError",
    "parse_file",
    "parse_string",
    "detect_format",
]
