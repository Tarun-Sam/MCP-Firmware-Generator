#!/usr/bin/env python3
"""
Code Quality MCP Server - REFACTORED
Analyzes generated code for structure, safety, and best practices
PHASE 9: Single Source of Truth Architecture
"""

import re
import json
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# Try importing MCP SDK
try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    HAS_MCP = True
except ImportError:
    HAS_MCP = False
    print("⚠️ MCP not installed. Running in standalone mode.")

# ============================================================================
# STRUCTURED ISSUE REPRESENTATION
# ============================================================================

class IssueType(Enum):
    """Issue category types."""
    MEMORY = "memory"
    PERFORMANCE = "performance"
    CORRECTNESS = "correctness"
    SAFETY = "safety"
    STYLE = "style"

class IssueSeverity(Enum):
    """Issue severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class CodeIssue:
    """Structured representation of a code issue."""
    type: str  # IssueType
    severity: str  # IssueSeverity
    message: str
    suggestion: str
    line_number: Optional[int] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "type": self.type,
            "severity": self.severity,
            "message": self.message,
            "suggestion": self.suggestion,
            "line_number": self.line_number
        }

# ============================================================================
# BOARD SPECIFICATIONS
# ============================================================================

BOARD_SPECS = {
    "esp32dev": {
        "name": "ESP32 DevKit V1",
        "total_ram_kb": 520,
        "system_reserved_kb": 100,
        "is_realtime": False,
        "performance_critical": False
    },
    "esp32s3": {
        "name": "ESP32-S3",
        "total_ram_kb": 1507,
        "system_reserved_kb": 150,
        "is_realtime": False,
        "performance_critical": True
    },
    "esp32c3": {
        "name": "ESP32-C3",
        "total_ram_kb": 400,
        "system_reserved_kb": 80,
        "is_realtime": True,
        "performance_critical": True
    }
}

# ============================================================================
# CODE QUALITY ANALYZER (REFACTORED)
# ============================================================================

class CodeQualityAnalyzer:
    """Analyzes C/C++ code for quality issues with structured feedback."""
    
    def __init__(self):
        self.code = ""
        self.board = "esp32dev"
        self.issues: List[CodeIssue] = []
        self.quality_score = 100
    
    def analyze(self, code: str, board: str = "esp32dev") -> Dict:
        """Run full analysis on code with board-aware scoring."""
        self.code = code
        self.board = board
        self.issues = []
        self.quality_score = 100
        
        # Get board specs
        board_info = BOARD_SPECS.get(board, BOARD_SPECS["esp32dev"])
        
        # Run all checks
        self._check_correctness()
        self._check_memory_safety(board_info)
        self._check_performance(board_info)
        self._check_safety()
        self._check_style()
        
        # Memory analysis
        memory_analysis = self._estimate_memory(board_info)
        
        # Calculate board-aware score
        final_score = self._calculate_weighted_score(board_info)
        
        # Generate summary
        summary = self._generate_summary(final_score, board_info)
        
        # Separate by severity
        critical_issues = [i for i in self.issues if i.severity == IssueSeverity.CRITICAL.value]
        high_issues = [i for i in self.issues if i.severity == IssueSeverity.HIGH.value]
        medium_issues = [i for i in self.issues if i.severity == IssueSeverity.MEDIUM.value]
        low_issues = [i for i in self.issues if i.severity == IssueSeverity.LOW.value]
        
        return {
            "quality_score": final_score,
            "code_lines": len(code.split('\n')),
            "code_size_kb": round(len(code) / 1024, 2),
            
            # Structured issues
            "issues": [i.to_dict() for i in self.issues],
            "issues_by_severity": {
                "critical": [i.to_dict() for i in critical_issues],
                "high": [i.to_dict() for i in high_issues],
                "medium": [i.to_dict() for i in medium_issues],
                "low": [i.to_dict() for i in low_issues]
            },
            "issues_by_type": self._group_by_type(),
            
            # Counts (backward compatibility)
            "issues_count": len(self.issues),
            "critical_count": len(critical_issues),
            "high_count": len(high_issues),
            "medium_count": len(medium_issues),
            "low_count": len(low_issues),
            
            # Memory integration
            "estimated_ram_usage_percent": memory_analysis["usage_percent"],
            "estimated_free_ram_kb": memory_analysis["estimated_free_ram_kb"],
            "memory_status": memory_analysis["safety_margin"],
            
            # Human-readable
            "severity": self._get_overall_severity(),
            "summary": summary,
            "board": board_info["name"]
        }
    
    # ========================================================================
    # CORRECTNESS CHECKS (Highest Priority)
    # ========================================================================
    
    def _check_correctness(self):
        """Check for structural correctness issues."""
        
        # Missing setup()
        if "void setup()" not in self.code and "void setup (" not in self.code:
            self.issues.append(CodeIssue(
                type=IssueType.CORRECTNESS.value,
                severity=IssueSeverity.CRITICAL.value,
                message="Missing void setup() function - code won't compile",
                suggestion="Add: void setup() { /* initialization code */ }"
            ))
        
        # Missing loop()
        if "void loop()" not in self.code and "void loop (" not in self.code:
            self.issues.append(CodeIssue(
                type=IssueType.CORRECTNESS.value,
                severity=IssueSeverity.CRITICAL.value,
                message="Missing void loop() function - code won't compile",
                suggestion="Add: void loop() { /* main program logic */ }"
            ))
        
        # Unbounded arrays (dangerous)
        if re.search(r'char\s+\w+\s*\[\s*\]', self.code):
            self.issues.append(CodeIssue(
                type=IssueType.CORRECTNESS.value,
                severity=IssueSeverity.HIGH.value,
                message="Unbounded array declaration without size",
                suggestion="Specify array size: char buffer[256];"
            ))
    
    # ========================================================================
    # MEMORY SAFETY CHECKS
    # ========================================================================
    
    def _check_memory_safety(self, board_info: Dict):
        """Check for memory issues with board-aware severity."""
        
        # Large static allocations
        large_arrays = re.findall(r'char\s+\w+\s*\[\s*(\d+)\s*\]', self.code)
        for size_str in large_arrays:
            size = int(size_str)
            if size > 1000:
                # Critical on low-RAM boards
                severity = IssueSeverity.CRITICAL.value if board_info["total_ram_kb"] < 500 else IssueSeverity.HIGH.value
                self.issues.append(CodeIssue(
                    type=IssueType.MEMORY.value,
                    severity=severity,
                    message=f"Large static array allocation ({size} bytes) detected",
                    suggestion=f"Use dynamic allocation or reduce size. Board has only {board_info['total_ram_kb']}KB RAM"
                ))
        
        # Memory leak detection
        malloc_count = self.code.count('malloc')
        free_count = self.code.count('free')
        
        if malloc_count > 0 and malloc_count > free_count:
            self.issues.append(CodeIssue(
                type=IssueType.MEMORY.value,
                severity=IssueSeverity.HIGH.value,
                message=f"Potential memory leak: {malloc_count} malloc calls but only {free_count} free calls",
                suggestion="Ensure every malloc() has a corresponding free()"
            ))
        
        # String usage without F() macro
        string_literals = len(re.findall(r'Serial\.print(?:ln)?\s*\(\s*"[^"]{10,}"', self.code))
        if string_literals > 3:
            self.issues.append(CodeIssue(
                type=IssueType.MEMORY.value,
                severity=IssueSeverity.MEDIUM.value,
                message=f"Found {string_literals} string literals without F() macro",
                suggestion='Use F("text") to store strings in flash: Serial.println(F("message"));'
            ))
    
    # ========================================================================
    # PERFORMANCE CHECKS
    # ========================================================================
    
    def _check_performance(self, board_info: Dict):
        """Check for performance issues with board-aware severity."""
        
        # Long delays (more critical on realtime boards)
        long_delays = re.findall(r'delay\s*\(\s*(\d+)\s*\)', self.code)
        for delay_str in long_delays:
            delay_ms = int(delay_str)
            if delay_ms >= 10000:  # 10+ seconds
                severity = IssueSeverity.CRITICAL.value if board_info["is_realtime"] else IssueSeverity.HIGH.value
                self.issues.append(CodeIssue(
                    type=IssueType.PERFORMANCE.value,
                    severity=severity,
                    message=f"Very long delay ({delay_ms}ms) detected - blocks entire system",
                    suggestion="Use non-blocking timing: millis() or FreeRTOS tasks"
                ))
            elif delay_ms >= 1000:  # 1+ second
                severity = IssueSeverity.MEDIUM.value if not board_info["is_realtime"] else IssueSeverity.HIGH.value
                self.issues.append(CodeIssue(
                    type=IssueType.PERFORMANCE.value,
                    severity=severity,
                    message=f"Long delay ({delay_ms}ms) may impact responsiveness",
                    suggestion="Consider reducing delay or using non-blocking code"
                ))
        
        # Infinite loops (dangerous pattern)
        if re.search(r'while\s*\(\s*1\s*\)|while\s*\(\s*true\s*\)', self.code):
            self.issues.append(CodeIssue(
                type=IssueType.PERFORMANCE.value,
                severity=IssueSeverity.HIGH.value,
                message="Infinite loop with while(1) or while(true) detected",
                suggestion="Use the loop() function instead for continuous execution"
            ))
        
        # Serial spam without delay
        serial_calls_in_loop = self.code.count('Serial.print')
        if serial_calls_in_loop > 5 and 'delay' not in self.code:
            self.issues.append(CodeIssue(
                type=IssueType.PERFORMANCE.value,
                severity=IssueSeverity.MEDIUM.value,
                message="Multiple Serial.print calls without delays may overwhelm serial buffer",
                suggestion="Add delay(100) or reduce print frequency"
            ))
    
    # ========================================================================
    # SAFETY CHECKS
    # ========================================================================
    
    def _check_safety(self):
        """Check for safety and error handling."""
        
        # Missing Serial.begin (debugging)
        if "Serial.begin" not in self.code:
            self.issues.append(CodeIssue(
                type=IssueType.SAFETY.value,
                severity=IssueSeverity.LOW.value,
                message="Missing Serial.begin() - debugging will be difficult",
                suggestion="Add Serial.begin(115200); in setup()"
            ))
        
        # Limited error checking
        if_count = self.code.count('if (')
        if if_count < 2 and len(self.code) > 500:
            self.issues.append(CodeIssue(
                type=IssueType.SAFETY.value,
                severity=IssueSeverity.MEDIUM.value,
                message="Limited error checking - code may fail silently",
                suggestion="Add validation: if (sensor.begin()) { /* handle error */ }"
            ))
    
    # ========================================================================
    # STYLE CHECKS
    # ========================================================================
    
    def _check_style(self):
        """Check for best practices and style."""
        
        # No const usage
        if 'const' not in self.code and len(self.code) > 200:
            self.issues.append(CodeIssue(
                type=IssueType.STYLE.value,
                severity=IssueSeverity.LOW.value,
                message="No const declarations found",
                suggestion="Use const for constants: const int LED_PIN = 2;"
            ))
        
        # Low comment density
        lines = self.code.split('\n')
        comment_ratio = (self.code.count('//') + self.code.count('/*')) / max(1, len(lines))
        if comment_ratio < 0.05 and len(lines) > 30:
            self.issues.append(CodeIssue(
                type=IssueType.STYLE.value,
                severity=IssueSeverity.LOW.value,
                message="Low comment density (<5%)",
                suggestion="Add comments to explain complex logic"
            ))
        
        # Monolithic code (no functions)
        function_pattern = r'(?:void|int|float|bool|uint\d+_t)\s+\w+\s*\([^)]*\)\s*\{'
        functions = re.findall(function_pattern, self.code)
        if len(functions) <= 2 and len(lines) > 50:  # Just setup/loop
            self.issues.append(CodeIssue(
                type=IssueType.STYLE.value,
                severity=IssueSeverity.MEDIUM.value,
                message="All code in setup/loop - no helper functions",
                suggestion="Break complex logic into reusable functions"
            ))
    
    # ========================================================================
    # MEMORY ESTIMATION (INTEGRATED)
    # ========================================================================
    
    def _estimate_memory(self, board_info: Dict) -> Dict:
        """Estimate memory usage for the board."""
        
        total_ram = board_info["total_ram_kb"]
        system_reserve = board_info["system_reserved_kb"]
        
        # Estimate code size
        code_size_kb = len(self.code) / 1024
        
        # Estimate global variables
        global_vars = len(re.findall(r'^\s*(int|float|double|char|bool|uint\d+_t)\s+\w+', self.code, re.MULTILINE))
        arrays = len(re.findall(r'\[\s*\d+\s*\]', self.code))
        structs = len(re.findall(r'(struct|typedef\s+struct)', self.code))
        
        estimated_global_kb = (global_vars * 4 + arrays * 20 + structs * 10) / 1024
        
        # Calculate available
        used_kb = code_size_kb + estimated_global_kb + system_reserve
        free_kb = max(0, total_ram - used_kb)
        usage_percent = min(100, (used_kb / total_ram) * 100)
        
        # Safety margin
        if usage_percent > 80:
            safety = "critical"
        elif usage_percent > 50:
            safety = "warning"
        else:
            safety = "good"
        
        return {
            "estimated_code_size_kb": round(code_size_kb, 2),
            "estimated_global_vars_kb": round(estimated_global_kb, 2),
            "estimated_free_ram_kb": round(free_kb, 2),
            "usage_percent": round(usage_percent, 1),
            "safety_margin": safety
        }
    
    # ========================================================================
    # BOARD-AWARE SCORING
    # ========================================================================
    
    def _calculate_weighted_score(self, board_info: Dict) -> int:
        """Calculate quality score with board-aware weights."""
        
        score = 100
        
        for issue in self.issues:
            # Base weights by severity
            severity_weights = {
                IssueSeverity.CRITICAL.value: 20,
                IssueSeverity.HIGH.value: 12,
                IssueSeverity.MEDIUM.value: 6,
                IssueSeverity.LOW.value: 3
            }
            
            # Type multipliers
            type_multipliers = {
                IssueType.CORRECTNESS.value: 1.0,  # Always full weight
                IssueType.MEMORY.value: 1.5 if board_info["total_ram_kb"] < 500 else 1.0,
                IssueType.PERFORMANCE.value: 1.3 if board_info["is_realtime"] else 0.8,
                IssueType.SAFETY.value: 1.0,
                IssueType.STYLE.value: 0.5
            }
            
            base_penalty = severity_weights.get(issue.severity, 5)
            multiplier = type_multipliers.get(issue.type, 1.0)
            
            score -= int(base_penalty * multiplier)
        
        return max(0, min(100, score))
    
    # ========================================================================
    # HELPERS
    # ========================================================================
    
    def _group_by_type(self) -> Dict:
        """Group issues by type."""
        grouped = {
            "memory": [],
            "performance": [],
            "correctness": [],
            "safety": [],
            "style": []
        }
        
        for issue in self.issues:
            grouped[issue.type].append(issue.to_dict())
        
        return grouped
    
    def _get_overall_severity(self) -> str:
        """Get overall severity level."""
        critical = sum(1 for i in self.issues if i.severity == IssueSeverity.CRITICAL.value)
        high = sum(1 for i in self.issues if i.severity == IssueSeverity.HIGH.value)
        
        if critical > 0:
            return "critical"
        elif high > 2:
            return "high"
        elif high > 0 or len(self.issues) > 5:
            return "medium"
        elif len(self.issues) > 0:
            return "low"
        else:
            return "excellent"
    
    def _generate_summary(self, score: int, board_info: Dict) -> str:
        """Generate human-readable summary."""
        
        # Score-based assessment
        if score >= 90:
            quality = "excellent"
            action = "ready for production use"
        elif score >= 75:
            quality = "good"
            action = "minor improvements recommended"
        elif score >= 50:
            quality = "acceptable"
            action = "several issues should be addressed"
        else:
            quality = "poor"
            action = "critical issues must be fixed before use"
        
        # Issue highlights
        critical = [i for i in self.issues if i.severity == IssueSeverity.CRITICAL.value]
        memory_issues = [i for i in self.issues if i.type == IssueType.MEMORY.value]
        perf_issues = [i for i in self.issues if i.type == IssueType.PERFORMANCE.value]
        
        highlights = []
        if critical:
            highlights.append(f"{len(critical)} critical issue(s)")
        if memory_issues:
            highlights.append("memory concerns")
        if perf_issues:
            highlights.append("performance bottlenecks")
        
        highlight_str = ", ".join(highlights) if highlights else "no major issues"
        
        return f"Code quality is {quality} ({score}/100) with {highlight_str}. {action.capitalize()}."

# ============================================================================
# MCP SERVER SETUP
# ============================================================================

if HAS_MCP:
    server = Server("code-quality")
    
    @server.list_tools()
    async def list_tools():
        """List available tools."""
        return [
            Tool(
                name="analyze_code_quality",
                description="Analyze code for structure, safety, and best practices with board-aware scoring",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "C/C++ source code"},
                        "board": {"type": "string", "description": "Target board (esp32dev, esp32s3, esp32c3)"}
                    },
                    "required": ["code"]
                }
            )
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        """Execute tool calls."""
        code = arguments.get("code", "")
        board = arguments.get("board", "esp32dev")
        
        if name == "analyze_code_quality":
            analyzer = CodeQualityAnalyzer()
            result = analyzer.analyze(code, board)
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

# ============================================================================
# STANDALONE TEST
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🔍 Code Quality Server (Refactored - Phase 9)")
    print("="*70)
    
    sample_code = """
#include <WiFi.h>
#include <DHT.h>

#define DHT_PIN 23
char bigBuffer[5000];

void setup() {
    Serial.begin(115200);
    WiFi.begin("SSID", "PASSWORD");
}

void loop() {
    float temp = dht.readTemperature();
    Serial.println("Temperature: ");
    Serial.println(temp);
    delay(15000);
}
"""
    
    print("\n📊 Test: ESP32-C3 (Low RAM, Real-time)")
    analyzer = CodeQualityAnalyzer()
    result = analyzer.analyze(sample_code, "esp32c3")
    
    print(f"\n✅ Quality Score: {result['quality_score']}/100")
    print(f"📝 Summary: {result['summary']}")
    print(f"💾 Memory: {result['estimated_ram_usage_percent']}% ({result['memory_status']})")
    print(f"\n🚨 Issues by Severity:")
    print(f"  - Critical: {result['critical_count']}")
    print(f"  - High: {result['high_count']}")
    print(f"  - Medium: {result['medium_count']}")
    print(f"  - Low: {result['low_count']}")
    
    print("\n📋 Structured Issues:")
    for issue in result['issues'][:3]:  # Show first 3
        print(f"\n  [{issue['severity'].upper()}] {issue['type']}")
        print(f"    Problem: {issue['message']}")
        print(f"    Fix: {issue['suggestion']}")
    
    print("\n" + "="*70)
    print("✅ Refactored analyzer ready!")