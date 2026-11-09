# Starter Code — Lab #4

> Dành cho học viên VinUni AI Product Labs.

## Cách Sử Dụng

1. **Cài đặt môi trường:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Hoàn thiện bài lab:**
   - Mở `tools.py` → Hoàn thiện 2 hàm tool + JSON Schemas.
   - Mở `template.py` → Hoàn thiện 4 TODO:
     - TODO 1: System Prompt
     - TODO 2: ChatbotBaseline
     - TODO 3: Intent Detection
     - TODO 4: Agent Loop

3. **Chạy thử:**
   ```bash
   python3 template.py
   ```

4. **Kiểm thử autograder:**
   ```bash
   python3 -m pytest ../autograder/test_agent.py -v
   ```

## Lưu Ý
- Code chạy ở chế độ **Mock Simulator** mặc định (không cần API key).
- Nếu muốn thử Live API, đặt biến môi trường: `export GEMINI_API_KEY=your_key`
