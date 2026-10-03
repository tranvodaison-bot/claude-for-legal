---
name: vong-doi-yeu-cau-phan-mem
description: >
  Điều phối vòng đời yêu cầu khi build/sửa phần mềm nội bộ có người duyệt: dựng lại kiến trúc hiện
  trạng, phân loại CR lớn/nhỏ theo rủi ro, khơi gợi yêu cầu thành PRD, chuẩn bị tri thức, đặc tả
  (sequence, API, user story, mockup), coding, test E2E, viết HDSD, go-live
  - với các GATE người chốt có biên bản, sổ UC Master, phân tích ảnh hưởng và ma trận truy vết
  UC→US→API→test→HDSD (có script kiểm). Kích hoạt khi: có change request, yêu cầu mới, PRD, BRD,
  user story, use case, đặc tả nghiệp vụ, phân tích ảnh hưởng, duyệt thiết kế, UAT, nghiệm thu phần
  mềm, viết hướng dẫn sử dụng, "làm tính năng mới cho app", "sửa luồng hiện tại", "chốt yêu cầu trước
  khi code". KHÔNG dùng cho: lệnh GSD/phase/wave cụ thể → gsd-master; đặc tả và nghiệm thu chi tiết
  từng màn → dac-ta-ui-nghiep-vu; React/TDD → netninja-master; QLDA xây dựng → hub-master;
  biên bản/văn bản hành chính theo NĐ 30 → nd30-sualoi.
---

# Vòng đời yêu cầu phần mềm có GATE

Nguồn ý tưởng: sơ đồ quy trình BA - dev - test do Boss cung cấp (03/10/2026). Skill giữ khung 0→6 và
các GATE, bổ sung những chỗ sơ đồ để hở (mục "Phản biện đã tích hợp" cuối file).

**Tư tưởng cốt lõi:** mỗi giai đoạn chỉ bắt đầu khi đầu vào đã được người có thẩm quyền chốt bằng
biên bản; mọi thứ xây ra đều truy ngược được về một UC trong sổ Master. AI làm nhanh phần soạn, dựng,
test; con người giữ quyền chốt. Không GATE nào được "coi như đã duyệt" vì người dùng im lặng.

## Bản đồ quy trình

```
0. Dựng lại kiến trúc hiện trạng (SA AS-IS) ◄──────────── cập nhật sau mỗi lần coding xong
        │
   Phân loại CR (theo RỦI RO, không chỉ số chức năng)
        ├── CR LỚN ─► 1. Khơi gợi yêu cầu → PRD ─► [GATE 1: data model + state + danh sách UC]
        │                 ─► 2. Chuẩn bị tri thức ─► 3. Đặc tả
        └── CR NHỎ ─► Luồng CR: làm rõ hẹp + phân tích ảnh hưởng ─► [GATE CR: duyệt + đăng ký UC]
                          ─► cập nhật đặc tả (vào bước 3)
3. Đặc tả: màn hình ASCII → HTML tương tác ─► [GATE 2: chốt màn hình]
           sequence + API + user story      ─► [GATE 3: chốt luồng xử lý + API]
4. Coding ─► 5. Test E2E ──(lệch đặc tả: sửa CODE, test lại; tối đa 3 vòng)──┐
                  ▲──────────────────────────────────────────────────────────┘
5 ─► [GATE 4: UAT + kiểm tra go-live] ─► 6. HDSD ─► Triển khai LIVE ─► cập nhật SA AS-IS (bước 0)
```

## Bước 0 – Dựng lại kiến trúc hiện trạng
Gom mọi repo/thư mục liên quan vào một chỗ; viết `docs/sa-hien-trang.md`: thành phần, luồng dữ liệu,
mô hình dữ liệu, tích hợp ngoài, điểm đã biết là nợ kỹ thuật. Lý do: phân tích ảnh hưởng của CR chỉ
đúng khi bản đồ hiện trạng đúng. Tài liệu này được cập nhật **sau mỗi lần coding xong**, không phải
một lần rồi bỏ.

## Phân loại CR
Đọc `references/phan-loai-cr.md`. Tóm tắt: CR là **LỚN** nếu chạm bất kỳ thứ nào trong: mô hình dữ
liệu, máy trạng thái, phân quyền, quy tắc pháp lý/tài chính, tích hợp ngoài, dữ liệu đã có (migrate) -
**kể cả khi chỉ 1 chức năng**. Chỉ khi không chạm những thứ đó và ≤ 2 chức năng mới là NHỎ. Không chắc
→ xếp LỚN; hạ xuống NHỎ phải có lý do ghi trong biên bản.

## Bước 1 – Khơi gợi yêu cầu → PRD (CR lớn)
Đọc tài liệu chủ sản phẩm (PO) cung cấp; liệt kê **câu hỏi làm rõ** và **khoảng trống (gap)** thành
danh sách đánh số, hỏi gộp một lần; đề xuất quy trình nghiệp vụ. Viết PRD theo mẫu trong
`references/mau-tai-lieu.md`. Không tự điền nghiệp vụ còn trống - ghi "chờ PO".
**GATE 1** chốt: mô hình dữ liệu, sơ đồ trạng thái, danh sách UC (đã có mã trong sổ Master).

## Bước 2 – Chuẩn bị tri thức
`docs/design.md` (nguyên tắc giao diện, token - dùng skill `dac-ta-ui-nghiep-vu`), `docs/sitemap.md`
(cây màn hình, ai vào được đâu), kiến trúc thông tin (đối tượng, thuộc tính, quan hệ). Mục đích: để
mọi màn hình/agent sau dùng chung một từ vựng.

## Bước 3 – Đặc tả
- **Màn hình:** phác ASCII trước (rẻ, sửa nhanh, chốt bố cục và trường dữ liệu), sau đó dựng **HTML
  tương tác** dữ liệu mẫu để người dùng bấm thử. Chi tiết, token, nghiệm thu: skill `dac-ta-ui-nghiep-vu`.
  **GATE 2** chốt màn hình.
- **Luồng xử lý:** sequence diagram (mermaid), đặc tả API (đầu vào, đầu ra, mã lỗi, quyền), user story
  kèm tiêu chí chấp nhận dạng Given/When/Then. **GATE 3** chốt luồng + API.
- Mỗi US/API/màn hình ghi mã UC nó phục vụ (để script truy vết kiểm được).

## Bước 4 – Coding
Lập plan → chia task → sub-agent song song khi task độc lập (dự án dùng GSD thì theo `gsd-master`);
migrate + seeding dữ liệu; unit + integration test. Không đổi đặc tả trong lúc code: thấy đặc tả sai
→ dừng, mở CR (quay về phân loại CR), không lặng lẽ "sửa cho hợp lý".

## Bước 5 – Test E2E
Viết testcase từ tiêu chí chấp nhận của US (mỗi testcase ghi mã US/UC); seeding dữ liệu kiểm thử;
chạy, chụp màn hình làm bằng chứng; báo cáo đạt/lỗi.
**Vòng "lệch đặc tả":** đặc tả là chuẩn - lệch thì sửa **code**, test lại. Không sửa test hay đặc tả
cho khớp code. Tối đa 3 vòng tự sửa; quá 3 vòng → dừng, báo nguyên nhân, chờ quyết định.

## GATE 4 – UAT và kiểm tra go-live (bổ sung so với sơ đồ gốc)
Người dùng nghiệp vụ tự chạy các kịch bản chính trên môi trường thử; kiểm: sao lưu dữ liệu, kịch bản
rollback migrate, phân quyền, cấu hình môi trường, không còn dữ liệu seed giả trên LIVE.

## Bước 6 – Hướng dẫn sử dụng (HDSD)
Theo template của đơn vị (mẫu khung trong `references/mau-tai-lieu.md`); mỗi chức năng: mục đích,
ai dùng, các bước có ảnh chụp từ bản đã test (không dùng ảnh mockup), lỗi thường gặp và cách xử lý.
Mỗi mục HDSD ghi mã UC.

## Điều phối agent (khi chạy trong Claude Code)
Phiên chính mạnh (effort cao) giữ việc cần phán đoán: phân loại CR, PRD, đặc tả, review, verify. Subagent
effort `medium` làm việc tốn ngữ cảnh: **explorer** (bước 0, phân tích ảnh hưởng - chỉ đọc), **researcher**
(bước 2 - tra cứu, ghi mức nguồn), **worker** (bước 4-5 - sửa code, chạy test). **Advisor** (`/advisor`) được
yêu cầu tường minh trước GATE 1, khi lỗi lặp lại, và trước GATE 4; ý kiến advisor là phản biện, không thay
người chốt. Việc xác định được bằng luật thì chạy bằng script, việc mơ hồ thì đẩy lên tầng trên đến người
chốt GATE. Chi tiết, cấu hình, chi phí: `references/dieu-phoi-agent.md`.

## Biên bản GATE và truy vết
- Mỗi GATE có biên bản: phiên bản tài liệu được chốt, người chốt, ngày, điều kiện kèm theo, mục còn
  mở. Mẫu trong `references/mau-tai-lieu.md`. Không có biên bản = chưa qua GATE.
- Sổ `docs/uc-master.yaml` là xương sống: UC ↔ US ↔ API ↔ màn hình ↔ testcase ↔ HDSD ↔ GATE.
- Chạy `python3 scripts/check_trace.py docs/uc-master.yaml` trước mỗi GATE và trước go-live: báo UC
  thiếu đặc tả/test/HDSD, test trỏ tới UC không tồn tại, GATE chưa có người chốt.
- **Chỉ ghi mã của tài liệu đã tồn tại.** Điền "US-001" cho một user story chưa viết là truy vết giả:
  script sẽ báo sạch trong khi thực tế thiếu. Chưa có thì để `[]` và để script báo lỗi.
- Áp vào dự án đã dựng trước khi có quy trình: ghi sổ đúng hiện trạng (GATE chưa ký, thiếu US) rồi trình
  người chốt bù - không hợp thức hóa ngược bằng cách ghi ngày ký giả.

## Phản biện đã tích hợp (so với sơ đồ gốc)
1. **Phân loại CR theo rủi ro, không theo số chức năng** - "1-2 chức năng" nhưng đổi quy tắc tính tiền
   hay phân quyền vẫn là CR lớn.
2. **"Tự fix" chỉ được sửa code** - nếu không, vòng lặp có thể hợp thức hóa lỗi bằng cách sửa test/đặc tả.
   Giới hạn 3 vòng để không lặp vô hạn.
3. **Thêm GATE 4 (UAT + go-live)** - sơ đồ gốc đi thẳng từ test E2E của AI sang LIVE; test do AI viết
   không thay được người dùng nghiệp vụ, và LIVE cần kịch bản rollback.
4. **CR nhỏ vẫn qua GATE 2/3 nếu đổi màn hình hoặc API** - sơ đồ gốc đưa CR thẳng vào bước 3; skill
   này giữ GATE ở bước 3 cho mọi thay đổi chạm màn hình/API.
5. **Biên bản cho mọi GATE + sổ truy vết** - để kiểm toán/nghiệm thu chứng minh được ai chốt gì, khi nào.
