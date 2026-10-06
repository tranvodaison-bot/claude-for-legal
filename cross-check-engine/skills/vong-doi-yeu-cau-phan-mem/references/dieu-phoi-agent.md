# Điều phối agent trong vòng đời có GATE

Mô hình (đã kiểm chứng với tài liệu Claude Code, 10/2026): **một phiên chính mạnh** lập kế hoạch, quyết
định và review; **subagent effort thấp hơn** làm việc tốn ngữ cảnh; **advisor** mạnh hơn hoặc bằng phiên
chính, chỉ tư vấn ở điểm quyết định, không tự viết code.

## Vai trò

| Vai trò | Cấu hình gợi ý | Làm gì | Không được |
|---|---|---|---|
| Phiên chính | Opus, effort `high` | Phân loại CR, viết PRD/đặc tả, trình GATE, review kết quả subagent, verify trước khi báo xong | Giao quyết định GATE cho subagent |
| Advisor | Fable (hoặc Opus ≥ 5) qua `/advisor` | Đọc toàn bộ phiên, tư vấn | Viết code; được coi là người chốt GATE |
| explorer | effort `medium`, chỉ Read/Grep/Glob | Bước 0 SA hiện trạng; phân tích ảnh hưởng CR | Sửa file |
| researcher | effort `medium`, Web + Read | Bước 2 tri thức, tra văn bản pháp luật, ghi mức nguồn | Tự nâng mức nguồn lên `primary`; kết luận pháp lý |
| worker | effort `medium`, Edit/Bash | Bước 4 code + test; vòng lệch đặc tả ở bước 5 | Sửa đặc tả; sửa test cho khớp code; commit |

Cách đặt: subagent trong `.claude/agents/*.md` (frontmatter `model`, `effort`, `tools`); phiên chính bằng
`/effort` hoặc `modelSettings."<model-id>".effortLevel` (khóa `effortLevel` cấp gốc không tác dụng trên
Opus 5.5); advisor bằng `/advisor <model>` hoặc `advisorModel`.

## Gắn advisor vào điểm quyết định của quy trình

Advisor tự được gọi theo phán đoán của model; để gọi đúng lúc, phiên chính **yêu cầu tường minh**:

| Thời điểm trong ảnh gốc | Điểm tương ứng trong quy trình | Câu lệnh gợi ý |
|---|---|---|
| Trước khi lập kế hoạch | Trước khi trình GATE 1 (PRD) và trước khi chia task ở bước 4 | "Hỏi advisor về PRD/kế hoạch này trước khi trình" |
| Lỗi lặp lại | Vòng lệch đặc tả lần 2 (trước khi chạm giới hạn 3 vòng) | "Lỗi này lặp lại - hỏi advisor trước khi sửa tiếp" |
| Trước khi báo xong | Trước GATE 4 (UAT) và trước khi báo bàn giao | "Hỏi advisor còn sót gì trước khi báo xong" |

Advisor **không thay người chốt GATE**: ý kiến của advisor đưa vào hồ sơ trình như một ý kiến phản biện;
biên bản GATE vẫn chỉ ghi người có thẩm quyền.

## Luồng một vòng CR

```
Phiên chính (high): phân loại CR ──► explorer (medium): ảnh hưởng ──► phiên chính: PRD
   ──► [advisor] ──► GATE 1 ──► researcher (medium): tri thức ──► phiên chính: đặc tả ──► GATE 2, 3
   ──► worker (medium) × n task độc lập, song song ──► phiên chính (high): review + verify
   ──► test E2E (lệch → worker sửa code; lỗi lặp → [advisor]) ──► [advisor] ──► GATE 4 ──► HDSD
```

## Quy tắc phân cấp (rút từ "sharp → code, split → lên trên")
- Việc **xác định được bằng luật** (thứ tự ngày, khớp số, truy vết đủ/thiếu) → chạy bằng **script/engine**,
  không để model "đánh giá". Ví dụ: `check_trace.py`, engine đối soát.
- Việc **mơ hồ** → đẩy lên tầng trên: subagent → phiên chính → advisor → **người chốt GATE**.
- Không dùng dịch vụ quyết định của bên thứ ba cho dữ liệu dự án khi chưa có đánh giá bảo mật và hợp
  đồng dữ liệu.

## Chi phí và giới hạn
- Advisor đọc lại toàn bộ hội thoại mỗi lần gọi, không cache; Fable có thể tính vào usage credits.
- Advisor đang thử nghiệm; chỉ Anthropic API. Không có advisor thì quy trình vẫn chạy - advisor là lớp phản
  biện thêm, không phải điều kiện của GATE.
- Subagent effort `medium` phù hợp đọc/tra/sửa theo đặc tả; việc cần phán đoán (phân loại CR, phản biện
  đặc tả, review) giữ ở phiên chính.
