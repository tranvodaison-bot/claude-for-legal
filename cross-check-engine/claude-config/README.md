# Cấu hình Claude Code cho dự án (agent tree)

Mô hình điều phối: **Opus 5.5 phiên chính (lập kế hoạch, quyết định, review)** · **Fable 5.1 advisor
(trực, tư vấn ở điểm quyết định)** · **3 subagent effort `medium`** (explorer đọc code, worker sửa code
+ chạy test, researcher tra tài liệu). Quy trình áp dụng: skill `vong-doi-yeu-cau-phan-mem`, mục
"Điều phối agent".

Repo này cố ý gitignore `/.claude/`, nên cấu hình để ở đây và **không tự có hiệu lực**. Cài:

```bash
# Subagent: cho riêng dự án (trong máy của Boss) hoặc cho mọi dự án
mkdir -p .claude/agents && cp cross-check-engine/claude-config/agents/*.md .claude/agents/
# hoặc: mkdir -p ~/.claude/agents && cp cross-check-engine/claude-config/agents/*.md ~/.claude/agents/

# Phiên chính + advisor: gộp các khóa trong settings.example.json vào ~/.claude/settings.json
# hoặc làm trong phiên:
#   /model opus      /effort high      /advisor fable
```

Kiểm tra: `/agents` liệt kê explorer, worker, researcher; khi phiên bắt đầu có thông báo
`Advisor Tool (experimental) is on…`.

## Lưu ý đã kiểm chứng (tài liệu Claude Code, 03/10/2026)
- Opus 5.5 **mặc định effort `medium`**. Khóa `effortLevel` ở cấp gốc settings **không có tác dụng** với
  Opus 5.5 - phải đặt trong `modelSettings."claude-opus-5-5"` (như file mẫu) hoặc dùng `/effort high`.
- Advisor đang **thử nghiệm**; chỉ chạy qua Anthropic API (không chạy trên Bedrock, Vertex, Foundry,
  Claude Platform on AWS); tắt nếu đặt `DISABLE_TELEMETRY` hoặc biến tắt feature flag.
- Fable làm advisor: trên một số gói tính vào **usage credits** và cần đồng ý một lần qua `/model fable`.
  Mỗi lần gọi advisor đọc lại toàn bộ hội thoại (không cache) - tốn thêm token.
- Thời điểm gọi advisor do model tự quyết; không có thiết lập ép gọi. Muốn gọi thì yêu cầu trong prompt
  ("hỏi advisor trước khi trình GATE").
- Subagent kế thừa advisor nếu model của nó đủ điều kiện ghép cặp.

## Không tích hợp: lớp "JEV fork"
JEV là mô hình quyết định của bên thứ ba (TypeSafe), không thuộc Anthropic; muốn dùng phải gửi dữ liệu
phiên (gồm hồ sơ dự án) ra dịch vụ ngoài. Chưa có đánh giá bảo mật/hợp đồng dữ liệu → không dùng cho dữ
liệu pháp lý dự án. Nguyên tắc của nó ("quyết định rõ ràng thì chạy bằng code, mơ hồ thì đẩy lên tầng
trên") đã có sẵn trong hệ thống: engine quy tắc + script kiểm truy vết là phần "chạy bằng code"; GATE là
phần "đẩy lên người quyết định".
