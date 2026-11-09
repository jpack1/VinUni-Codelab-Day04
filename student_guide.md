# Hướng Dẫn Chi Tiết Bài Thực Hành (Student Guide) — Lab #4

> **Dành cho:** Học viên chương trình VinUni AI Training Program  
> **Tài liệu:** Hướng dẫn thực hành từng bước (Step-by-Step Lab Walkthrough)

---

## 🧭 Hướng Dẫn Thực Hiện 4 Milestones

### 1. Milestone 1: Thiết Kế Production System Prompt

Mở file `starter-code/template.py` và tìm biến `SYSTEM_PROMPT` (TODO 1).

Một System Prompt cấp sản xuất cần có 5 phần:

```text
1. PERSONA — Ai là Agent? (Tên, vai trò, phong cách giao tiếp)
2. AVAILABLE TOOLS — Agent có những tool gì? (Tên + mô tả ngắn)
3. CORE RULES — Quy tắc bắt buộc (KHÔNG bịa dữ liệu, PHẢI gọi tool)
4. OPERATIONAL BOUNDARIES — Phạm vi hoạt động (chỉ Vingroup)
5. OUTPUT CONTRACT — Định dạng trả lời (Thought/Action/Observation/Final Answer)
```

**Ví dụ cấu trúc System Prompt:**
```text
Bạn là VinAssistant — trợ lý AI chính thức của hệ sinh thái Vingroup.

## PERSONA
- Tên: VinAssistant
- Vai trò: Chuyên viên tư vấn sản phẩm & dịch vụ VinFast, Vinpearl
- Giọng nói: Chuyên nghiệp, thân thiện, chính xác

## CORE RULES
1. KHÔNG BAO GIỜ bịa dữ liệu sản phẩm. PHẢI gọi tool để lấy dữ liệu thực.
...
```

**💡 Mẹo:** System Prompt tốt = Agent "biết luật chơi" → ít hallucination hơn.

---

### 2. Milestone 2: Hoàn Thiện Tool Functions & JSON Schemas

Mở file `starter-code/tools.py` và hoàn thiện 3 phần:

#### 2.1. Hàm `search_product_catalog`
```python
def search_product_catalog(category: str, max_price: int = 999999999999) -> List[Dict[str, Any]]:
    catalog_file = os.path.join(RAW_DATA_DIR, "product_catalog.json")
    if not os.path.exists(catalog_file):
        return [{"error": "Product catalog file not found."}]
    
    with open(catalog_file, "r", encoding="utf-8") as f:
        products = json.load(f)
    
    # Lọc sản phẩm theo category + max_price
    results = [
        p for p in products
        if p["category"].lower() == category.lower()
        and p["price_vnd"] <= max_price
    ]
    return results
```

#### 2.2. Hàm `submit_support_ticket`
```python
def submit_support_ticket(customer_name, issue_description, priority="medium"):
    tickets_file = os.path.join(RAW_DATA_DIR, "support_tickets.json")
    
    # Load existing tickets
    existing_tickets = []
    if os.path.exists(tickets_file):
        with open(tickets_file, "r", encoding="utf-8") as f:
            existing_tickets = json.load(f)
    
    # Generate ticket ID
    today = datetime.now().strftime("%Y%m%d")
    seq = len(existing_tickets) + 1
    ticket_id = f"TK-{today}-{seq:03d}"
    
    # Create & save new ticket
    new_ticket = {
        "ticket_id": ticket_id,
        "customer_name": customer_name,
        "issue_description": issue_description,
        "priority": priority.lower(),
        "status": "open",
        "created_at": datetime.now().isoformat() + "+07:00",
        "category": "general"
    }
    existing_tickets.append(new_ticket)
    
    with open(tickets_file, "w", encoding="utf-8") as f:
        json.dump(existing_tickets, f, indent=2, ensure_ascii=False)
    
    return {
        "ticket_id": ticket_id,
        "customer_name": customer_name,
        "priority": priority.lower(),
        "status": "open",
        "message": f"Ticket {ticket_id} đã được tạo thành công."
    }
```

#### 2.3. Định nghĩa JSON Schema (`TOOL_DEFINITIONS`)
```python
TOOL_DEFINITIONS = [
    {
        "name": "search_product_catalog",
        "description": "Tra cứu sản phẩm/dịch vụ Vingroup theo danh mục và giá tối đa.",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Loại sản phẩm: 'xe_dien' hoặc 'du_lich'.",
                    "enum": ["xe_dien", "du_lich"]
                },
                "max_price": {
                    "type": "integer",
                    "description": "Giá tối đa tính bằng VNĐ."
                }
            },
            "required": ["category"]
        }
    },
    # Tương tự cho submit_support_ticket...
]
```

---

### 3. Milestone 3: Xây Dựng Agent Loop

Trong class `ToolCallingAgent`, thuật toán Agent Loop được cài đặt theo sơ đồ:

```
[User Input] ──> Intent Detection
                     │
         ┌───────────┼───────────────┐
         │           │               │
    [needs_catalog] [needs_ticket]  [is_faq]
         │           │               │
         ▼           ▼               ▼
    Iteration 1   Iteration 2    Final Answer
    (catalog)     (ticket)       (trả lời trực tiếp)
         │           │
         └─────┬─────┘
               ▼
         Iteration 3
    (Tổng hợp Final Answer)
```

**Các bước chính:**
1. **Intent Detection:** Dùng keyword matching để xác định user cần tool nào.
2. **Iteration 1:** Nếu cần catalog → gọi `search_product_catalog`, lưu vào trace.
3. **Iteration 2:** Nếu cần ticket → gọi `submit_support_ticket`, lưu vào trace.
4. **Iteration 3+:** Tổng hợp tất cả observation từ trace → xuất Final Answer.

**💡 Mẹo:** Luôn kiểm tra `intents["needs_catalog"]` và `intents["needs_ticket"]` để quyết định số iteration cần thiết.

---

### 4. Milestone 4: Safeguards & Edge Cases

#### 4.1. Max Iterations Guard
```python
while iteration <= self.max_iterations:
    result, is_final = self._execute_step(...)
    if is_final:
        return {"answer": result, "trace": self.trace, "status": "completed"}
    iteration += 1

# Nếu vượt max_iterations
return {"answer": "Lỗi: Vượt quá số bước tối đa.", "status": "max_iterations_reached"}
```

#### 4.2. Empty Results Handling
```python
if not results or len(results) == 0:
    return "Rất tiếc, không tìm thấy sản phẩm phù hợp."
```

---

## 🪤 3 Bẫy Thường Gặp & Cách Khắc Phục (Traps & Gotchas)

1. **Trap 1: FileNotFoundError khi đọc JSON**
   * *Nguyên nhân:* Đường dẫn `RAW_DATA_DIR` không đúng khi chạy từ thư mục khác.
   * *Cách khắc phục:* Luôn dùng `os.path.join(os.path.dirname(__file__), "..", "raw-data")` để tính đường dẫn tương đối.

2. **Trap 2: Ticket bị ghi đè thay vì append**
   * *Nguyên nhân:* Mở file ở mode `"w"` mà không load existing tickets trước.
   * *Cách khắc phục:* Luôn `json.load()` trước, append new ticket, rồi mới `json.dump()` lại.

3. **Trap 3: Intent Detection sai khi câu hỏi chứa cả catalog + ticket**
   * *Nguyên nhân:* Dùng `if-elif` thay vì `if-if` riêng biệt → chỉ detect 1 intent.
   * *Cách khắc phục:* Kiểm tra `needs_catalog` và `needs_ticket` độc lập, cả 2 có thể `True` đồng thời.

---

## 🧪 Cách Kiểm Thử Kết Quả Bài Làm

Sau khi hoàn thành `template.py` và `tools.py`, chạy lệnh pytest:
```bash
python3 -m pytest autograder/test_agent.py -v
```

Nếu 8/8 test cases báo `PASSED`, chúc mừng bạn đã hoàn thành xuất sắc Lab #4! 🎉

---

## 📚 Tài Liệu Tham Khảo

| Tài liệu | Liên kết |
| :--- | :--- |
| OpenAI Function Calling Guide | https://platform.openai.com/docs/guides/function-calling |
| Google Gemini Tool Use | https://ai.google.dev/gemini-api/docs/function-calling |
| JSON Schema Specification | https://json-schema.org/understanding-json-schema |
| System Prompt Engineering Best Practices | Slide 18-27 trong bài giảng Day04 |
