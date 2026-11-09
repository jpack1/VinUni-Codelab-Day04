"""
Lab #4 Autograder — Pytest Suite (8 Unit Tests)
Kiểm thử solution-code: tools.py, agent.py

Chạy: python3 -m pytest Day04-Prompt-Engineering-Tool-Calling/02-lab/autograder/test_agent.py -v
"""

import sys
import os
import json
import pytest

SOLUTION_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "solution-code"))
STARTER_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "starter-code"))

for code_dir in [SOLUTION_DIR, STARTER_DIR]:
    if os.path.exists(code_dir) and code_dir not in sys.path:
        sys.path.insert(0, code_dir)

try:
    from template import ChatbotBaseline, ToolCallingAgent
except ModuleNotFoundError:
    from agent import ChatbotBaseline, ToolCallingAgent

from tools import search_product_catalog, submit_support_ticket, TOOL_MAP, TOOL_DEFINITIONS


# ═══════════════════════════════════════════════════════════════════════════
# Test 1: search_product_catalog — xe điện giá dưới 600 triệu
# ═══════════════════════════════════════════════════════════════════════════

def test_catalog_search_xe_dien_under_600m():
    results = search_product_catalog(category="xe_dien", max_price=600000000)
    assert isinstance(results, list)
    assert len(results) == 2  # VF 3 (315M) + VF 5 Plus (548M)
    names = [p["name"] for p in results]
    assert "VinFast VF 3" in names
    assert "VinFast VF 5 Plus" in names


# ═══════════════════════════════════════════════════════════════════════════
# Test 2: search_product_catalog — du lịch giá dưới 6 triệu
# ═══════════════════════════════════════════════════════════════════════════

def test_catalog_search_du_lich_under_6m():
    results = search_product_catalog(category="du_lich", max_price=6000000)
    assert isinstance(results, list)
    assert len(results) == 2  # Nha Trang (3.5M) + Phú Quốc (5.2M)
    names = [p["name"] for p in results]
    assert "Vinpearl Resort & Spa Nha Trang" in names
    assert "Vinpearl Discovery Phú Quốc" in names


# ═══════════════════════════════════════════════════════════════════════════
# Test 3: submit_support_ticket — tạo ticket thành công
# ═══════════════════════════════════════════════════════════════════════════

def test_submit_ticket_creates_ticket():
    result = submit_support_ticket(
        customer_name="Test User",
        issue_description="Test issue for autograder",
        priority="high"
    )
    assert isinstance(result, dict)
    assert "ticket_id" in result
    assert result["ticket_id"].startswith("TK-")
    assert result["customer_name"] == "Test User"
    assert result["priority"] == "high"
    assert result["status"] == "open"


# ═══════════════════════════════════════════════════════════════════════════
# Test 4: ChatbotBaseline — không gọi tool
# ═══════════════════════════════════════════════════════════════════════════

def test_chatbot_baseline_no_tools():
    chatbot = ChatbotBaseline()
    res = chatbot.query("Tôi muốn xem xe VinFast")
    assert res["status"] == "success"
    assert len(res["tool_calls"]) == 0


# ═══════════════════════════════════════════════════════════════════════════
# Test 5: ToolCallingAgent — single tool (catalog search)
# ═══════════════════════════════════════════════════════════════════════════

def test_agent_single_tool_catalog():
    agent = ToolCallingAgent(max_iterations=5)
    res = agent.run("Tôi muốn xem xe điện VinFast giá dưới 600 triệu.")
    assert res["status"] == "completed"
    assert res["iterations"] == 1
    assert "VF 3" in res["answer"] or "VF 5" in res["answer"]


# ═══════════════════════════════════════════════════════════════════════════
# Test 6: ToolCallingAgent — single tool (ticket submit)
# ═══════════════════════════════════════════════════════════════════════════

def test_agent_single_tool_ticket():
    agent = ToolCallingAgent(max_iterations=5)
    res = agent.run("Tôi tên Lê Minh Khoa, xe VF 8 của tôi bị lỗi hệ thống ADAS. Đây là vấn đề nghiêm trọng, cần xử lý gấp.")
    assert res["status"] == "completed"
    assert res["iterations"] == 1
    assert "TK-" in res["answer"]
    assert "Lê Minh Khoa" in res["answer"]


# ═══════════════════════════════════════════════════════════════════════════
# Test 7: ToolCallingAgent — FAQ (no tool call)
# ═══════════════════════════════════════════════════════════════════════════

def test_agent_faq_no_tool():
    agent = ToolCallingAgent(max_iterations=5)
    res = agent.run("Chính sách bảo hành pin xe điện VinFast kéo dài bao lâu?")
    assert res["status"] == "completed"
    assert res["iterations"] == 1
    assert "bảo hành" in res["answer"].lower() or "10 năm" in res["answer"]


# ═══════════════════════════════════════════════════════════════════════════
# Test 8: ToolCallingAgent — no results fallback
# ═══════════════════════════════════════════════════════════════════════════

def test_agent_no_results_fallback():
    agent = ToolCallingAgent(max_iterations=5)
    res = agent.run("Có xe điện nào giá dưới 200 triệu không?")
    assert res["status"] == "completed"
    assert "không tìm thấy" in res["answer"].lower() or "rất tiếc" in res["answer"].lower()


if __name__ == "__main__":
    sys.exit(pytest.main([__file__] + sys.argv[1:]))
