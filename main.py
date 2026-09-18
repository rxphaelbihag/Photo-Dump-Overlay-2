from tkinter import *
from tkinter import ttk
from tkinter import filedialog, messagebox
import tkinter
from imagesize import get
from PIL import Image, ImageTk, ImageOps
import os
from concurrent.futures import ThreadPoolExecutor
from overlay_utils import apply_overlay


class FormApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo Dump Overlay")
        self.window_width = 900
        self.window_height = 600
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()
        self.center_x = int((self.screen_width / 2) - (self.window_width / 2))
        self.center_y = int((self.screen_height / 2) - (self.window_height / 2))
        self.root.geometry(f"{self.window_width}x{self.window_height}+{self.center_x}+{self.center_y-50}")
        self.root.resizable(False, False)
        self.LINESPACE = 1
        self.BIGLINESPACE = 20

        Label(root, text="Photo Dump Overlay", font=("Arial", 16, "bold")).grid(
            row=0, column=0, columnspan=3, pady=(10, 0))

        # --- FRAMES ---
        info_frame_outer = Frame(root, width=330, height=450, relief="solid", borderwidth=1)
        info_frame_outer.grid(row=1, column=0, padx=(10, 5), pady=5, sticky='n')
        info_frame_outer.grid_propagate(False)
        info_frame_outer.pack_propagate(False)

        preview_frame = Frame(root, width=535, height=450, relief="solid", borderwidth=1)
        preview_frame.grid(row=1, column=1, padx=(5, 10), pady=5, sticky='n')
        preview_frame.grid_propagate(False)
        preview_frame.pack_propagate(False)

        Label(preview_frame, text="PREVIEW", font=("Arial", 10, "bold")).pack(
            anchor='w', padx=5, pady=(5, 2))

        preview_area = Frame(preview_frame, bg='grey')
        preview_area.pack(fill='both', expand=True, padx=5, pady=5)

        # --- SCROLLBAR ---
        canvas = Canvas(info_frame_outer, highlightthickness=0)
        scrollbar = ttk.Scrollbar(info_frame_outer, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)

        info_frame = Frame(canvas)
        canvas_window = canvas.create_window((0, 0), window=info_frame, anchor='nw')

        canvas.bind('<Configure>', lambda e: canvas.itemconfig(canvas_window, width=e.width))
        info_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.bind_all('<MouseWheel>', lambda e: canvas.yview_scroll(int(-e.delta / 120), 'units'))

        # --- TEXT VARIABLES ---
        self.folder_var = StringVar(value="No folder selected yet.")
        self.size_var = StringVar(value="--")
        self.contains_var = StringVar(value="--")
        self.orientations_var = StringVar(value="--")
        self.types_var = StringVar(value="--")
        self.dims_var = StringVar(value="--")
        self.overlay_var = StringVar(value="No file selected yet.")
        self.overlaytype_var = StringVar(value="--")
        self.overlaydims_var = StringVar(value="--")
        self.output_var = StringVar(value="No folder selected yet.")
        self.outputname_var = StringVar(value="overlayed_")

        # --- STATE ---
        self.input_folder = None
        self.overlay_landscape_path = None
        self.overlay_portrait_path = None
        self.output_folder = None
        self.abort_flag = False

        # --- FUNCTIONS ---
        def choose_folder(is_input):
            folder = filedialog.askdirectory()
            if not folder:
                return
            if is_input:
                self.input_folder = folder
                self.folder_var.set(folder)
                get_file_info(folder)
                update_preview()
            else:
                self.output_folder = folder
                self.output_var.set(folder)

        def show_preview(frame, pil_image, max_size=(500, 400)):
            for widget in frame.winfo_children():
                widget.destroy()
            pil_image = ImageOps.exif_transpose(pil_image)
            pil_image.thumbnail(max_size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(pil_image)
            label = Label(frame, image=photo, bg='grey', pady=5)
            label.image = photo
            label.pack()

        def choose_overlay_files():
            files = filedialog.askopenfilenames(
                title="Select overlay file(s) — 1 for both, 2 for landscape+portrait",
                filetypes=[("Image files", "*.png *.webp *.gif *.bmp *.jpg *.jpeg")])
            if not files:
                return
            self.overlay_landscape_path = files[0]
            self.overlay_portrait_path = files[1] if len(files) > 1 else files[0]
            self.overlay_var.set(files[0] if len(files) == 1
                                 else f"{os.path.basename(files[0])}, {os.path.basename(files[1])}")
            ext = os.path.splitext(files[0])[1].lower()
            self.overlaytype_var.set(ext if ext else "No extension")
            w, h = get(files[0])
            self.overlaydims_var.set(f"{w}x{h}")
            update_preview()

        def get_all_files_recursively(root_dir: str) -> list[str]:
            all_files = []
            for dirpath, _, filenames in os.walk(root_dir):
                for filename in filenames:
                    all_files.append(os.path.join(dirpath, filename))
            return all_files

        def get_file_types(files):
            return {os.path.splitext(f)[1].lower()
                    for f in files if os.path.splitext(f)[1]}

        def get_file_dimensions(files):
            dims = set()
            for f in files:
                try:
                    w, h = get(f)
                    dims.add(f"{w}x{h}")
                except Exception:
                    pass
            return dims

        def get_file_orientations(files):
            counts = {"Landscape": 0, "Portrait": 0, "Square": 0}
            for f in files:
                try:
                    w, h = get(f)
                except Exception:
                    continue
                if w > h:
                    counts["Landscape"] += 1
                elif w < h:
                    counts["Portrait"] += 1
                else:
                    counts["Square"] += 1
            return counts

        def get_file_info(folder):
            all_files = get_all_files_recursively(folder)
            self.size_var.set(f"{sum(os.path.getsize(f) for f in all_files) / (1024*1024):.2f} MB")
            self.contains_var.set(f"{len(all_files)} files")
            self.types_var.set(", ".join(get_file_types(all_files)))
            self.dims_var.set(", ".join(get_file_dimensions(all_files)))
            self.orientations_var.set(
                ", ".join(f"{k}: {v}" for k, v in get_file_orientations(all_files).items() if v > 0))

        def build_composite(base_path, overlay_landscape, overlay_portrait):
            base = Image.open(base_path).convert("RGBA")
            base = ImageOps.exif_transpose(base)

            bw, bh = base.size
            overlay_path = overlay_landscape if bw >= bh else overlay_portrait
            if not overlay_path:
                return base

            overlay = Image.open(overlay_path).convert("RGBA")
            overlay = ImageOps.fit(overlay, base.size,
                                   method=Image.Resampling.LANCZOS,
                                   centering=(0.5, 0.5))

            base.paste(overlay, (0, 0), overlay)
            return base

        def update_preview():
            if not self.input_folder or not self.overlay_landscape_path:
                return
            files = get_all_files_recursively(self.input_folder)
            if not files:
                return
            first = files[0]
            try:
                composite = build_composite(
                    first, self.overlay_landscape_path, self.overlay_portrait_path)
                show_preview(preview_area, composite)
            except Exception as e:
                print(f"Preview failed: {e}")

        def abort_all():
            self.abort_flag = True

        def overlay_all():
            if not self.input_folder:
                messagebox.showwarning("Missing", "Please select an input folder.")
                return
            if not self.overlay_landscape_path:
                messagebox.showwarning("Missing", "Please select an overlay file.")
                return
            if not self.output_folder:
                messagebox.showwarning("Missing", "Please select an output folder.")
                return

            files = get_all_files_recursively(self.input_folder)
            name_prefix = self.outputname_var.get().strip() or "overlayed_"
            total = len(files)
            count = 0
            skipped = 0

            self.abort_flag = False
            self.progress['maximum'] = total
            self.progress['value'] = 0
            self.progress_label.config(text=f"0 / {total}")
            self.root.update_idletasks()

            def process_one(f):
                out_name = f"{name_prefix}{os.path.basename(f)}"
                out_path = os.path.join(self.output_folder, out_name)
                apply_overlay(f, self.overlay_landscape_path,
                              self.overlay_portrait_path, out_path)

            max_workers = min(8, os.cpu_count() or 4)

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(process_one, f): f for f in files}
                done = 0
                for future in futures:
                    if self.abort_flag:
                        for fut in futures:
                            fut.cancel()
                        break
                    try:
                        future.result()
                        count += 1
                    except Exception as e:
                        skipped += 1
                        print(f"Skipped: {e}")

                    done += 1
                    self.progress['value'] = done
                    self.progress_label.config(text=f"{done} / {total}")
                    self.root.update_idletasks()

            if self.abort_flag:
                messagebox.showinfo("Aborted",
                                    f"Stopped after {done} of {total} files.\n"
                                    f"Completed: {count}, Skipped: {skipped}")
            else:
                messagebox.showinfo("Done",
                                    f"Overlayed {count} of {total} files.\n"
                                    f"Skipped: {skipped}")

            self.progress['value'] = 0
            self.progress_label.config(text="")
            self.abort_flag = False

        # =========================================================
        # SECTION: INPUT
        # =========================================================
        input_section = Frame(info_frame)
        input_section.pack(fill='x', pady=(5, 0))

        Label(input_section, text="INPUT", font=("Arial", 10, "bold")).pack(
            anchor='w', padx=5, pady=(5, 2))

        row = Frame(input_section); row.pack(fill='x', padx=5, pady=self.LINESPACE)
        Label(row, text="Input files:").pack(side='left', anchor='n')
        Label(row, textvariable=self.folder_var, wraplength=210,
              justify='left').pack(side='left', anchor='n', padx=(5, 0))

        Button(input_section, text="Browse Folder",
               command=lambda: choose_folder(True)).pack(
            anchor='w', padx=5, pady=(self.LINESPACE, self.BIGLINESPACE))

        for label, var in [
            ("Size:", self.size_var),
            ("Contains:", self.contains_var),
            ("File types:", self.types_var),
            ("File dimensions:", self.dims_var),
            ("Orientations:", self.orientations_var),
        ]:
            row = Frame(input_section); row.pack(fill='x', padx=5, pady=self.LINESPACE)
            Label(row, text=label).pack(side='left', anchor='n')
            Label(row, textvariable=var, wraplength=210,
                  justify='left').pack(side='left', anchor='n', padx=(5, 0))

        ttk.Separator(info_frame, orient='horizontal').pack(
            fill='x', padx=10, pady=(5, 10))

        # =========================================================
        # SECTION: OVERLAY
        # =========================================================
        overlay_section = Frame(info_frame)
        overlay_section.pack(fill='x', pady=(5, 0))

        Label(overlay_section, text="OVERLAY", font=("Arial", 10, "bold")).pack(
            anchor='w', padx=5, pady=(5, 2))

        row = Frame(overlay_section); row.pack(fill='x', padx=5, pady=self.LINESPACE)
        Label(row, text="Overlay file/s:").pack(side='left', anchor='n')
        Label(row, textvariable=self.overlay_var, wraplength=210,
              justify='left').pack(side='left', anchor='n', padx=(5, 0))

        Button(overlay_section, text="Browse File(s)",
               command=choose_overlay_files).pack(
            anchor='w', padx=5, pady=(self.LINESPACE, self.BIGLINESPACE))

        for label, var in [
            ("File type:", self.overlaytype_var),
            ("File dimensions:", self.overlaydims_var),
        ]:
            row = Frame(overlay_section); row.pack(fill='x', padx=5, pady=self.LINESPACE)
            Label(row, text=label).pack(side='left', anchor='n')
            Label(row, textvariable=var, wraplength=210,
                  justify='left').pack(side='left', anchor='n', padx=(5, 0))

        ttk.Separator(info_frame, orient='horizontal').pack(
            fill='x', padx=10, pady=(5, 10))

        # =========================================================
        # SECTION: OUTPUT
        # =========================================================
        output_section = Frame(info_frame)
        output_section.pack(fill='x', pady=(5, 0))

        Label(output_section, text="OUTPUT", font=("Arial", 10, "bold")).pack(
            anchor='w', padx=5, pady=(5, 2))

        row = Frame(output_section); row.pack(fill='x', padx=5, pady=self.LINESPACE)
        Label(row, text="Output folder:").pack(side='left', anchor='n')
        Label(row, textvariable=self.output_var, wraplength=210,
              justify='left').pack(side='left', anchor='n', padx=(5, 0))

        Button(output_section, text="Browse Folder",
               command=lambda: choose_folder(False)).pack(
            anchor='w', padx=5, pady=(self.LINESPACE, self.BIGLINESPACE))

        row = Frame(output_section); row.pack(fill='x', padx=5, pady=self.LINESPACE)
        Label(row, text="Output name:").pack(side='left', anchor='n')
        Entry(row, textvariable=self.outputname_var, width=25).pack(
            side='left', anchor='n', padx=(5, 0))

        # =========================================================
        # BOTTOM BAR: buttons + progress bar (centered)
        # =========================================================
        bottom_bar = Frame(root)
        bottom_bar.grid(row=2, column=0, columnspan=2, pady=(10, 15))

        btn_row = Frame(bottom_bar)
        btn_row.pack(pady=(0, 5))

        Button(btn_row, text="Overlay All", command=overlay_all,
               width=15).pack(side='left', padx=5)
        Button(btn_row, text="Abort", command=abort_all,
               width=10).pack(side='left', padx=5)

        self.progress = ttk.Progressbar(bottom_bar, orient='horizontal',
                                        length=400, mode='determinate')
        self.progress.pack()

        self.progress_label = Label(bottom_bar, text="")
        self.progress_label.pack(pady=(3, 0))


if __name__ == "__main__":
    root = tkinter.Tk()
    app = FormApp(root)
    root.mainloop()