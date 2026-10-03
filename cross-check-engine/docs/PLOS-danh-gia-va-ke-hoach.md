# PL-OS: đối chiếu đặc tả và kế hoạch build

Ngày lập: 03/10/2026. Tài liệu nháp để Ban QLDA thẩm định; không phải ý kiến pháp lý.

## 1. Kiểm chứng các khẳng định pháp lý trong đặc tả

Nguồn tra cứu là kết quả tìm kiếm trên các trang thứ cấp (thuvienphapluat, luatvietnam, cổng
sở/ban quản lý). Môi trường build chặn truy cập trực tiếp một số cổng chính phủ, nên **chưa đọc
văn bản gốc**. Mọi dòng dưới đây cần đối chiếu Công báo trước khi nạp vào hệ thống.

| # | Khẳng định trong đặc tả | Kết quả tra cứu | Hệ quả thiết kế |
|---|---|---|---|
| 1 | Luật XD 135/2025/QH15 ban hành 10/12/2025, hiệu lực chung 01/07/2026; một số điều/khoản hiệu lực 01/01/2026 | **Khớp.** Hiệu lực sớm: Đ43 k2, k3; Đ71; Đ95 k3, k4, k5 | Mô hình hiệu lực phải đến cấp điều/khoản, không chỉ cấp văn bản |
| 2 | Có VBHN 91/2026/VBHN-NĐ-BXD ngày 25/09/2026 về quản lý hoạt động xây dựng | **Khớp** số hiệu và ngày. **Chưa rõ** văn bản nào được hợp nhất | Xem mục 1.1 |
| 3 | Luật 135/2025 bãi bỏ điều kiện/chứng chỉ năng lực của doanh nghiệp | **Sai một phần.** Chứng chỉ năng lực tổ chức đã bị bãi bỏ **từ 01/07/2025**, theo Đ56 k1 Luật Đường sắt 95/2025/QH15 (bãi bỏ k4 Đ148 Luật XD 2014). Từ 01/07/2026, tổ chức **tự công khai thông tin năng lực** trên cổng của Bộ Xây dựng | Quy tắc năng lực có **ít nhất 3 cửa sổ thời gian** (trước 01/07/2025; 01/07/2025–30/06/2026; từ 01/07/2026), không phải 2 |
| 4 | (Ngầm định trong đặc tả gốc) Trình tự theo NĐ 175/2024/NĐ-CP | NĐ 175/2024 **hết hiệu lực từ 01/07/2026**, được thay bởi **NĐ 217/2026/NĐ-CP** | **Engine G1 đang gắn căn cứ NĐ 175/2024 cho mọi sự kiện, sai với sự kiện từ 01/07/2026** (xem mục 4) |
| 5 | (Từ tra cứu) Luật 135/2025 bỏ thủ tục thẩm định thiết kế triển khai sau TKCS tại cơ quan chuyên môn, chuyển trách nhiệm kiểm soát thiết kế cho CĐT | Chưa kiểm tra văn bản gốc | Quy tắc "phê duyệt thiết kế ← thẩm tra/thẩm định" phải phân nhánh theo thời điểm |

### 1.1. Điểm nghi vấn về VBHN 91/2026

Đặc tả gốc viết "NĐ 175/2024 được hợp nhất tại VBHN 91/2026". Tôi nghi ngờ điều này:
- Tên VBHN 91 là "quy định chi tiết một số điều của Luật Xây dựng về quản lý hoạt động xây dựng".
  Tên NĐ 175/2024 có thêm cụm "**và biện pháp thi hành**".
- NĐ 175/2024 đã hết hiệu lực từ 01/07/2026. Hợp nhất một văn bản đã hết hiệu lực vào 25/09/2026 là bất thường.

Giả thuyết: VBHN 91 hợp nhất **NĐ 217/2026** cùng văn bản sửa đổi của nó. **Phải mở phần "căn cứ hợp
nhất" của VBHN 91 để xác nhận.**

Nguyên tắc thiết kế rút ra: VBHN là **lớp hiển thị**, không phải nguồn gốc. Mọi trích dẫn trong
Finding phải trỏ về văn bản gốc hoặc văn bản sửa đổi đã tạo ra nội dung của điều/khoản đó.

## 2. Đánh giá kiến trúc PL-OS

### 2.1. Đồng ý và giữ nguyên

- Lấy **Legal Event** làm trục: Dự án → Sự kiện → Nghĩa vụ → Căn cứ → Hồ sơ → Đối soát → Rủi ro.
- **Finding là đối tượng có vòng đời** (người chịu trách nhiệm, hạn xử lý, chứng cứ khắc phục, người duyệt).
- **4 trạng thái hồ sơ**: có / có nhưng chưa đủ chứng minh / có nhưng mâu thuẫn / không có.
- **Quy tắc là dữ liệu, không phải code.**
- **AI không được tạo căn cứ pháp lý**; không tìm được căn cứ thì kết quả là UNKNOWN.
- Có **ma trận áp dụng pháp luật** và **ma trận tuân thủ**.

### 2.2. Phản biện, đề nghị sửa

| Điểm trong đặc tả | Vấn đề | Đề nghị |
|---|---|---|
| V1 = kho văn bản đầy đủ đến cấp điểm | Khối lượng nhập liệu rất lớn, mà chưa có quy tắc nào dùng thì chưa có giá trị. Dễ thành "thư viện pháp luật thứ N" | **Kho theo nhu cầu**: chỉ nạp điều/khoản mà quy tắc trích dẫn. Build theo **lát cắt dọc** (một chuỗi sự kiện, xuyên đủ các lớp) |
| Risk score = Impact × Occurrence × Evidence gap × Chain impact | Nhân các thang thứ bậc tạo ra con số chính xác giả. Một hệ số bằng 0 thì toàn bộ rủi ro về 0. Khó giải trình với kiểm toán | Mức độ gốc do **quy tắc gán**. Có điều chỉnh minh bạch (ví dụ +1 bậc nếu chặn ≥ N sự kiện phía sau, tính từ đồ thị). Điểm số chỉ dùng để sắp xếp |
| 15 loại node, khoảng 25 bảng, đồ thị tri thức ngay từ đầu | Thiết kế quá sớm. Với quy mô vài trăm dự án, CSDL đồ thị chuyên dụng không cần thiết | CSDL quan hệ (SQLite, lên Postgres khi nhiều người dùng) + bảng cạnh `relations` + truy vấn đệ quy. Thêm loại node khi có quy tắc cần dùng |
| 5 agent AI | Librarian chủ yếu là việc của người (biên tập, xác minh). Conflict Agent ở mức "Rule ↔ Rule" là nghiên cứu pháp lý, không phải tính năng | Chỉ làm **agent trích xuất** (Agent 03) ở M4. Copilot hỏi đáp làm sau cùng, **chỉ trả lời trên kho đã xác minh** |
| Copilot báo "126 nghĩa vụ, 98 PASS" | Ngầm hiểu hệ thống biết **đủ** nghĩa vụ. Không có Finding bị đọc thành "tuân thủ" | Mọi báo cáo phải ghi **độ phủ**: "thư viện quy tắc phủ X/Y loại sự kiện; ngoài phạm vi = chưa kiểm tra" |

### 2.3. Bổ sung, cả hai đặc tả đều thiếu

1. **Ngày nào quyết định văn bản áp dụng.** Điều khoản chuyển tiếp thường căn vào ngày **nộp hồ sơ**,
   ngày **phê duyệt dự án** hoặc ngày **ký hợp đồng**, không phải ngày diễn ra sự kiện đang xét. Mỗi
   Legal Event cần nhiều loại ngày (nộp, tiếp nhận, ký, có hiệu lực). Mỗi quy tắc chuyển tiếp khai báo
   rõ nó dùng ngày nào.
2. **Thay thế hồ sơ dự án.** Quyết định điều chỉnh thay thế quyết định gốc, từng phần hoặc toàn bộ.
   Cần quan hệ `SUPERSEDES` giữa các Evidence, nếu không engine sẽ đối soát với bản đã hết giá trị.
3. **Thẩm quyền và ủy quyền.** Kiểm tra "người ký có thẩm quyền" cần dữ liệu: chức danh, văn bản ủy
   quyền, thời hạn ủy quyền.
4. **Hai người kiểm soát khi sửa quy tắc** (người lập / người duyệt). Quy tắc chưa duyệt không được tạo
   Finding mức CRITICAL/HIGH. **Căn cứ chưa xác minh → mức tối đa là REVIEW.**
5. **Test hồi quy cho quy tắc.** Mỗi quy tắc có dự án mẫu kèm kết quả kỳ vọng. Khi luật đổi, chạy lại
   toàn bộ để thấy dự án nào đổi kết luận.
6. **Chất lượng chứng cứ.** Bản scan, bản sao y, bản gốc, bản điện tử có chữ ký số.
7. **Phân quyền và bảo mật hồ sơ** (hồ sơ dự án, hợp đồng là dữ liệu nhạy cảm), kèm nhật ký truy cập.
8. **Nguồn cập nhật kho văn bản.** Ai theo dõi văn bản mới, lấy từ đâu (Công báo, CSDL quốc gia
   VBQPPL), mất bao lâu từ khi ban hành đến khi quy tắc được cập nhật.

## 3. Đối chiếu engine G1 hiện có với PL-OS

| Thành phần PL-OS | G1 hiện có | Khoảng cách |
|---|---|---|
| Legal Event | `steps` (một bản ghi cho mỗi bước) | Chưa có nhiều lần cùng loại (điều chỉnh dự án nhiều lần), chưa có nhiều loại ngày |
| Rule không hard-code | YAML, `applies_if` chỉ so sánh bằng | Cần ngôn ngữ điều kiện an toàn (JSON Logic, không dùng `eval`) và cửa sổ hiệu lực của quy tắc |
| 4 trạng thái hồ sơ | DATA_GAP ≈ "không có / chưa đủ" | Chưa tách "có nhưng chưa đủ chứng minh" và "có nhưng mâu thuẫn" |
| Finding | Dataclass, xuất báo cáo | Chưa lưu trữ, chưa có vòng đời |
| Căn cứ đã/chưa xác minh | Cờ `verified` | Chưa dùng cờ này để giới hạn mức độ |
| Temporal | So sánh thứ tự ngày giữa các bước | Chưa có hiệu lực văn bản, hiệu lực từng phần, chuyển tiếp |

Kết luận: G1 tái sử dụng được phần lõi đánh giá tiên quyết và thứ tự thời gian. Mô hình dữ liệu phải
chuyển từ "bước" sang "sự kiện + chứng cứ" ở M1.

## 4. Sai sót của G1 cần sửa

- `data/procedure_rules.yaml` gắn căn cứ "NĐ 175/2024/NĐ-CP" cho mọi quy tắc. Với sự kiện từ 01/07/2026,
  căn cứ đúng là văn bản thay thế (NĐ 217/2026, chưa xác minh). Sửa triệt để ở M2 (quy tắc có cửa sổ
  hiệu lực). Trước mắt đã ghi cảnh báo vào đầu file quy tắc và README.
- Quy tắc "phê duyệt thiết kế ← thẩm tra thiết kế" có thể không còn đúng dạng này sau Luật 135/2025.

## 5. Kế hoạch build: lát cắt dọc, mỗi mốc có kết quả xem được

| Mốc | Nội dung | Kết quả Ban QLDA xem được | Cần từ Ban QLDA |
|---|---|---|---|
| **M1. Chuỗi Khởi công** | Mô hình dữ liệu lõi trên SQLite: `legal_documents`, `provisions`, `validity` (từng phần), `rules` (có cửa sổ hiệu lực), `projects`, `events` (nhiều loại ngày), `evidences` (4 trạng thái, `SUPERSEDES`), `findings`. Chuyển engine G1 sang mô hình này. Kho chỉ gồm các điều/khoản của chuỗi chủ trương → phê duyệt dự án → thiết kế → GPXD → hợp đồng → khởi công, theo **hai chế độ**: Luật 2014 + NĐ 175/2024 và Luật 135/2025 + NĐ 217/2026 | Báo cáo Legal Trace của 1 dự án mẫu: Finding → quy tắc → điều/khoản → văn bản → sự kiện → hồ sơ | Văn bản gốc (bản Công báo) của các điều/khoản liên quan; người xác nhận quy tắc |
| **M2. Temporal + chuyển tiếp** | Chọn chế độ pháp lý theo ngày quyết định của từng quy tắc chuyển tiếp. Ma trận áp dụng v0 (thuộc tính dự án → văn bản/điều khoản). Giới hạn mức độ khi căn cứ chưa xác minh | Cùng một dự án mẫu cho hai kết luận khác nhau khi đổi ngày phê duyệt trước/sau 01/07/2026, kèm lý do | Các điều khoản chuyển tiếp của Luật 135/2025 và NĐ 217/2026 |
| **M3. Nhất quán + năng lực + vòng đời Finding** | Quy tắc 3.4 (tên, TMĐT, quy mô, thời gian), quy tắc năng lực theo 3 cửa sổ thời gian, giao việc, hạn xử lý, chứng cứ khắc phục, nhật ký kiểm toán | Ma trận tuân thủ của dự án, xuất Excel | Danh sách trường cần đối soát; quy trình xử lý Finding hiện hành |
| **M4. Trích xuất PDF/Word** | Agent trích xuất: hồ sơ → sự kiện/chứng cứ, **mỗi trường gắn trang/đoạn nguồn**, người xác nhận trước khi vào engine | Nạp 1 bộ hồ sơ thật đã ẩn danh, ra bảng trích xuất để duyệt | Bộ hồ sơ mẫu ẩn danh |
| **M5. Dashboard + Copilot** | Giao diện web: bản đồ chuỗi pháp lý, drill-down Legal Trace, hỏi đáp chỉ trên kho đã xác minh | Dashboard chạy được | Hạ tầng triển khai, số người dùng, phân quyền |

Nguyên tắc chung cho mọi mốc: không mốc nào nạp căn cứ chưa đối chiếu văn bản gốc mà gắn
`verified: true`. Mỗi quy tắc mới đi kèm test.

## 5a. Cập nhật 03/10/2026: đã làm trước một phần M2 (giai đoạn 2021-2026)

- Sổ văn bản 13 lĩnh vực, các mốc chuyển chế độ chính:
  - 01/01/2021: Luật 62/2020 sửa Luật XD, Luật Đầu tư 2020.
  - 26/01/2021: NĐ 06/2021.
  - 09/02/2021: NĐ 10/2021.
  - 03/03/2021: NĐ 15/2021.
  - 01/04/2021: NĐ 50/2021.
  - 01/01/2022: Luật BVMT 2020.
  - 20/06/2023: NĐ 35/2023.
  - 01/01/2024: Luật Đấu thầu 2023.
  - 27/02/2024: NĐ 24/2024.
  - 01/08/2024: Luật Đất đai 2024.
  - 30/12/2024: NĐ 175/2024.
  - 01/01/2025: Luật Đầu tư công 2024.
  - 01/07/2025: chứng chỉ năng lực tổ chức bị bãi bỏ, NĐ 140/2025, Luật PCCC 2024.
  - 01/01/2026: hiệu lực từng phần Luật 135/2025.
  - 01/07/2026: Luật 135/2025, NĐ 206, 207, 210, 217/2026.
- 12 quy tắc chuyển tiếp khung; đối soát căn cứ viện dẫn của từng văn bản dự án; bản đồ chế độ pháp lý.
- Mọi ngày tháng chưa ở mức văn bản gốc nên kết luận bị giới hạn ở mức VÀNG.
- Việc còn lại của M2: bóc điều khoản chuyển tiếp thật (điều/khoản, điều kiện chi tiết, nhất là chi phí),
  đối chiếu toàn bộ ngày hiệu lực lên mức `primary`, bổ sung Thông tư hướng dẫn.

## 6. Quyết định cần Ban QLDA chốt trước M1

1. **Hạ tầng**: một máy dùng cục bộ (SQLite, CLI và báo cáo) hay máy chủ nhiều người dùng ngay từ đầu?
   Đề xuất: cục bộ đến hết M3, lên máy chủ ở M5.
2. **Tích hợp Enterprise OS / `universal_metadata`**: tôi chưa có đặc tả của hệ thống này. Cần lược đồ
   hoặc tài liệu để thiết kế khóa định danh tương thích ngay từ M1.
3. **Người lập / người duyệt quy tắc**: ai chịu trách nhiệm xác nhận căn cứ pháp lý?
4. **Phạm vi chế độ pháp lý ở M1**: cả hai chế độ (2014/175 và 135/217) hay chỉ chế độ mới?
   Đề xuất: cả hai, vì dự án đang triển khai phần lớn nằm trong giai đoạn chuyển tiếp.
