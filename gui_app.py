import os
import queue
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

from capture_core import CaptureOptions, capture_urls, save_browser_session
from utils import clean_url_list

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class WebCaptureApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("웹사이트 화면 자동 캡처 도구 (Web Capture Tool)")
        self.geometry("780x680")
        self.minsize(680, 560)

        # 상태 제어 변수
        self.is_running = False
        self.stop_requested = False
        self.msg_queue = queue.Queue()
        self.session_file = Path("storage_state.json")

        self._build_ui()
        self._check_queue()

    def _build_ui(self):
        # 1. 파일 및 저장 폴더 설정 섹션
        frame_io = ctk.CTkFrame(self)
        frame_io.pack(fill="x", padx=15, pady=(15, 8))

        ctk.CTkLabel(frame_io, text="URL 파일 경로:", font=("맑은 고딕", 12, "bold")).grid(row=0, column=0, padx=10, pady=8, sticky="w")
        default_url_file = str(Path("web site.txt").resolve()) if Path("web site.txt").exists() else ""
        self.entry_url_file = ctk.CTkEntry(frame_io, width=480)
        self.entry_url_file.insert(0, default_url_file)
        self.entry_url_file.grid(row=0, column=1, padx=5, pady=8, sticky="ew")
        ctk.CTkButton(frame_io, text="파일 찾기", width=80, command=self._browse_url_file).grid(row=0, column=2, padx=10, pady=8)

        ctk.CTkLabel(frame_io, text="저장 폴더 경로:", font=("맑은 고딕", 12, "bold")).grid(row=1, column=0, padx=10, pady=8, sticky="w")
        default_dir = str(Path.home() / "Downloads" / "doto_captures")
        self.entry_output_dir = ctk.CTkEntry(frame_io, width=480)
        self.entry_output_dir.insert(0, default_dir)
        self.entry_output_dir.grid(row=1, column=1, padx=5, pady=8, sticky="ew")
        ctk.CTkButton(frame_io, text="폴더 선택", width=80, command=self._browse_output_dir).grid(row=1, column=2, padx=10, pady=8)

        frame_io.columnconfigure(1, weight=1)

        # 2. 캡처 옵션 & 세션 관리 섹션
        frame_opt = ctk.CTkFrame(self)
        frame_opt.pack(fill="x", padx=15, pady=8)

        self.var_full_page = tk.BooleanVar(value=True)
        self.chk_full_page = ctk.CTkCheckBox(frame_opt, text="전체 페이지 스크롤 캡처(Full Page)", variable=self.var_full_page)
        self.chk_full_page.grid(row=0, column=0, padx=15, pady=10, sticky="w")

        ctk.CTkLabel(frame_opt, text="추가 렌더링 대기(초):").grid(row=0, column=1, padx=(10, 5), pady=10, sticky="e")
        self.entry_delay = ctk.CTkEntry(frame_opt, width=50)
        self.entry_delay.insert(0, "1.0")
        self.entry_delay.grid(row=0, column=2, padx=5, pady=10, sticky="w")

        self.btn_session = ctk.CTkButton(
            frame_opt, text="브라우저 로그인 및 세션 저장", fg_color="#3B8ED0", hover_color="#36719F",
            command=self._launch_login_session
        )
        self.btn_session.grid(row=0, column=3, padx=15, pady=10, sticky="e")
        frame_opt.columnconfigure(3, weight=1)

        # 3. 실행 버튼 및 프로그레스 바 섹션
        frame_action = ctk.CTkFrame(self)
        frame_action.pack(fill="x", padx=15, pady=8)

        self.btn_start = ctk.CTkButton(
            frame_action, text="캡처 시작", fg_color="#2CC985", hover_color="#229965",
            font=("맑은 고딕", 14, "bold"), height=38, command=self._start_capture
        )
        self.btn_start.pack(side="left", padx=10, pady=10, expand=True, fill="x")

        self.btn_stop = ctk.CTkButton(
            frame_action, text="작업 중단", fg_color="#D32F2F", hover_color="#9A0007",
            font=("맑은 고딕", 14, "bold"), height=38, state="disabled", command=self._stop_capture
        )
        self.btn_stop.pack(side="right", padx=10, pady=10, expand=True, fill="x")

        # 진행률 표시
        self.lbl_progress = ctk.CTkLabel(self, text="준비 완료", font=("맑은 고딕", 11))
        self.lbl_progress.pack(anchor="w", padx=20, pady=(5, 2))

        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.pack(fill="x", padx=15, pady=(0, 10))
        self.progress_bar.set(0)

        # 4. 실시간 로그 창
        ctk.CTkLabel(self, text="실행 로그:", font=("맑은 고딕", 12, "bold")).pack(anchor="w", padx=15, pady=(5, 2))
        self.txt_log = ctk.CTkTextbox(self, height=220)
        self.txt_log.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def _browse_url_file(self):
        f = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if f:
            self.entry_url_file.delete(0, tk.END)
            self.entry_url_file.insert(0, f)

    def _browse_output_dir(self):
        d = filedialog.askdirectory()
        if d:
            self.entry_output_dir.delete(0, tk.END)
            self.entry_output_dir.insert(0, d)

    def _append_log(self, text: str):
        self.msg_queue.put(("log", text))

    def _check_queue(self):
        while not self.msg_queue.empty():
            msg_type, data = self.msg_queue.get_nowait()
            if msg_type == "log":
                self.txt_log.insert(tk.END, data + "\n")
                self.txt_log.see(tk.END)
            elif msg_type == "progress":
                idx, total, url = data
                val = idx / total if total > 0 else 0
                self.progress_bar.set(val)
                self.lbl_progress.configure(text=f"진행 중: {idx} / {total} ({(val*100):.1f}%) - {url}")
            elif msg_type == "finished":
                results = data
                self.is_running = False
                self.btn_start.configure(state="normal")
                self.btn_stop.configure(state="disabled")
                self.lbl_progress.configure(text="작업 완료")
                messagebox.showinfo("완료", f"캡처 작업이 완료되었습니다!\n총 {results['total']}개 중 성공 {results['success']}개, 실패 {results['failed']}개")

        self.after(100, self._check_queue)

    def _launch_login_session(self):
        url_file = self.entry_url_file.get().strip()
        start_url = "https://doto.kr/dashboard"
        if url_file and Path(url_file).exists():
            with open(url_file, "r", encoding="utf-8") as f:
                urls = clean_url_list(f.readlines())
                if urls:
                    start_url = urls[0]

        threading.Thread(target=self._run_login_thread, args=(start_url,), daemon=True).start()

    def _run_login_thread(self, start_url: str):
        self._append_log("브라우저 창을 엽니다. 로그인을 완료한 후 브라우저 창을 닫아주세요.")
        try:
            success = save_browser_session(start_url, self.session_file)
            if success:
                self._append_log(f"로그인 세션이 성공적으로 저장되었습니다 ({self.session_file.name}).")
            else:
                self._append_log("세션 저장 실패")
        except Exception as e:
            self._append_log(f"세션 저장 중 오류 발생: {e}")

    def _start_capture(self):
        url_path = self.entry_url_file.get().strip()
        out_dir = self.entry_output_dir.get().strip()

        if not url_path or not Path(url_path).exists():
            messagebox.showerror("오류", "유효한 URL 파일 경로를 선택해 주세요.")
            return

        if not out_dir:
            messagebox.showerror("오류", "저장 폴더 경로를 지정해 주세요.")
            return

        try:
            with open(url_path, "r", encoding="utf-8") as f:
                urls = clean_url_list(f.readlines())
        except Exception as e:
            messagebox.showerror("오류", f"URL 파일을 읽을 수 없습니다: {e}")
            return

        if not urls:
            messagebox.showwarning("알림", "유효한 웹사이트 URL이 없습니다.")
            return

        try:
            delay = float(self.entry_delay.get())
        except ValueError:
            delay = 1.0

        options = CaptureOptions(
            full_page=self.var_full_page.get(),
            delay_seconds=delay
        )

        self.is_running = True
        self.stop_requested = False
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.progress_bar.set(0)
        self.lbl_progress.configure(text=f"총 {len(urls)}개 작업 시작...")
        self.txt_log.delete("1.0", tk.END)

        worker = threading.Thread(
            target=self._capture_worker,
            args=(urls, Path(out_dir), options),
            daemon=True
        )
        worker.start()

    def _stop_capture(self):
        if self.is_running:
            self.stop_requested = True
            self._append_log("작업 중단 요청 중...")

    def _capture_worker(self, urls, out_dir, options):
        def on_prog(idx, total, url):
            self.msg_queue.put(("progress", (idx, total, url)))

        def on_l(msg):
            self.msg_queue.put(("log", msg))

        def is_stop():
            return self.stop_requested

        session_to_use = self.session_file if self.session_file.exists() else None
        results = capture_urls(
            urls=urls,
            output_dir=out_dir,
            options=options,
            session_file=session_to_use,
            on_progress=on_prog,
            on_log=on_l,
            is_stopped=is_stop
        )
        self.msg_queue.put(("finished", results))

if __name__ == "__main__":
    app = WebCaptureApp()
    app.mainloop()
