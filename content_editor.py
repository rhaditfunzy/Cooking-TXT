"""Cooking TXT Content Editor: GUI Tkinter untuk mengelola bahan dan resep."""
from __future__ import annotations
import json
import re
import shutil
import unicodedata
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Any

ROOT = Path(__file__).resolve().parent
ING_DIR = ROOT / "data" / "ingredients"
REC_DIR = ROOT / "data" / "recipes"
ING_IMG = ROOT / "assets" / "images" / "ingredients"
REC_IMG = ROOT / "assets" / "images" / "recipes"
MAX_STEPS = 5


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")


def number(value: str, label: str, *, integer: bool = False, minimum: float = 0) -> int | float:
    try:
        result = int(value) if integer else float(value.strip().replace(",", "."))
    except (ValueError, AttributeError):
        raise ValueError(f"{label} harus berupa {'bilangan bulat' if integer else 'angka'}.")
    if result < minimum:
        raise ValueError(f"{label} minimal {minimum}.")
    return result


def records(folder: Path) -> tuple[list[tuple[Path, dict[str, Any]]], list[str]]:
    folder.mkdir(parents=True, exist_ok=True)
    found, errors = [], []
    for path in sorted(folder.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("JSON harus berupa object")
            found.append((path, data))
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"{path.name}: {exc}")
    return found, errors


def save_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    try:
        temp.write_text(json.dumps(data, ensure_ascii=False, indent=4) + "\n", encoding="utf-8")
        temp.replace(path)
    finally:
        temp.unlink(missing_ok=True)


def copy_image(parent: tk.Widget, variable: tk.StringVar, folder: Path) -> None:
    source_name = filedialog.askopenfilename(
        parent=parent, title="Pilih gambar",
        filetypes=[("Gambar", "*.png *.jpg *.jpeg *.webp *.bmp"), ("Semua file", "*.*")],
    )
    if not source_name:
        return
    source = Path(source_name)
    try:
        folder.mkdir(parents=True, exist_ok=True)
        if source.resolve().parent == folder.resolve():
            target = source
        else:
            target = folder / source.name
            index = 2
            while target.exists():
                target = folder / f"{source.stem}_{index}{source.suffix}"
                index += 1
            shutil.copy2(source, target)
        variable.set(target.relative_to(ROOT).as_posix())
    except (OSError, ValueError) as exc:
        messagebox.showerror("Gagal memilih gambar", str(exc), parent=parent)


class Editor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cooking TXT — Content Editor")
        self.geometry("1180x800")
        self.minsize(1180, 720)
        self.configure(bg="#eef2f7")
        for folder in (ING_DIR, REC_DIR, ING_IMG, REC_IMG):
            folder.mkdir(parents=True, exist_ok=True)
        self._style()
        header = ttk.Frame(self, style="Header.TFrame", padding=(26, 20))
        header.pack(fill="x")
        title_row = ttk.Frame(header, style="Header.TFrame")
        title_row.pack(fill="x")
        ttk.Label(title_row, text="COOKING TXT", style="HeaderTitle.TLabel").pack(side="left")
        ttk.Label(title_row, text="CONTENT STUDIO  /  DATA MANAGER", style="HeaderPill.TLabel").pack(side="right", padx=(8, 0))
        ttk.Label(header, text="Kelola bahan makanan dan resep tanpa perlu mengedit file JSON.", style="HeaderSub.TLabel").pack(anchor="w", pady=(7, 0))
        self.tabs = ttk.Notebook(self, style="Modern.TNotebook")
        self.tabs.pack(fill="both", expand=True, padx=22, pady=(18, 10))
        self.ingredients = IngredientTab(self.tabs, self)
        self.recipes = RecipeTab(self.tabs, self)
        self.tabs.add(self.ingredients, text="  BAHAN MAKANAN  ")
        self.tabs.add(self.recipes, text="  RESEP  ")
        footer = ttk.Frame(self, style="Footer.TFrame", padding=(24, 8))
        footer.pack(fill="x")
        ttk.Label(footer, text=f"FOLDER PROJECT  ·  {ROOT}", style="Muted.TLabel").pack(side="left")
        ttk.Label(footer, text="Simpan perubahan, lalu buka ulang game untuk memuat data terbaru.", style="Muted.TLabel").pack(side="right")

    def _style(self):
        s = ttk.Style(self)
        try:
            s.theme_use("clam")
        except tk.TclError:
            pass
        s.configure(".", font=("Segoe UI", 10))
        s.configure("TFrame", background="#eef2f7")
        s.configure("TLabel", background="#eef2f7", foreground="#1e293b")
        s.configure("Header.TFrame", background="#17263c")
        s.configure("HeaderTitle.TLabel", background="#17263c", foreground="#ffffff", font=("Segoe UI", 19, "bold"))
        s.configure("HeaderSub.TLabel", background="#17263c", foreground="#c5d1e0", font=("Segoe UI", 10))
        s.configure("HeaderPill.TLabel", background="#263b57", foreground="#dbeafe", padding=(12, 6), font=("Segoe UI", 8, "bold"))
        s.configure("Footer.TFrame", background="#eef2f7")
        s.configure("Muted.TLabel", background="#eef2f7", foreground="#64748b", font=("Segoe UI", 8))
        s.configure("Card.TFrame", background="#ffffff")
        s.configure("TLabelframe", background="#ffffff", bordercolor="#dce3ed", relief="solid")
        s.configure("TLabelframe.Label", background="#ffffff", foreground="#334155", font=("Segoe UI", 9, "bold"))
        s.configure("Modern.TNotebook", background="#eef2f7", borderwidth=0)
        s.configure("Modern.TNotebook.Tab", background="#e2e8f0", foreground="#475569", padding=(20, 12), font=("Segoe UI", 9, "bold"), borderwidth=0)
        s.map("Modern.TNotebook.Tab", background=[("selected", "#ffffff"), ("active", "#dbeafe")], foreground=[("selected", "#1d4ed8"), ("active", "#1e40af")])
        s.configure("Treeview", rowheight=34, background="#ffffff", fieldbackground="#ffffff", foreground="#243247", borderwidth=0, font=("Segoe UI", 9))
        s.configure("Treeview.Heading", background="#edf2f7", foreground="#475569", font=("Segoe UI", 9, "bold"), padding=(8, 8), relief="flat")
        s.map("Treeview", background=[("selected", "#dbeafe")], foreground=[("selected", "#1e3a8a")])
        s.configure("TEntry", padding=(9, 8), fieldbackground="#ffffff")
        s.configure("TCombobox", padding=(8, 7), fieldbackground="#ffffff")
        s.configure("TButton", padding=(11, 8), background="#e8edf4", foreground="#243247", bordercolor="#d5deea")
        s.map("TButton", background=[("active", "#dbe5f1"), ("pressed", "#cbd8e8")])
        s.configure("Accent.TButton", padding=(16, 9), background="#2563eb", foreground="#ffffff", bordercolor="#2563eb", font=("Segoe UI", 9, "bold"))
        s.map("Accent.TButton", background=[("active", "#1d4ed8"), ("pressed", "#1e40af")], foreground=[("active", "#ffffff")])
        s.configure("Compact.TButton", padding=(7, 4), font=("Segoe UI", 8))

    def refresh_recipe_ingredients(self):
        if hasattr(self, "recipes"):
            self.recipes.refresh_ingredient_names()


class EditorTab(ttk.Frame):
    def __init__(self, parent, app, folder: Path):
        super().__init__(parent, padding=14)
        self.app, self.folder = app, folder
        self.entries: list[tuple[Path, dict[str, Any]]] = []
        self.current_path: Path | None = None

    def build_left(self, parent, title, new_command, delete_command):
        panel = ttk.Frame(parent, style="Card.TFrame", padding=14)
        panel.pack(fill="both", expand=True, padx=(0, 10), pady=0)
        ttk.Label(panel, text=title, font=("Segoe UI", 11, "bold"), foreground="#17263c", background="#ffffff").pack(anchor="w", pady=(0, 4))
        ttk.Label(panel, text="Pilih item untuk melihat atau mengubah detailnya.", font=("Segoe UI", 8), foreground="#94a3b8", background="#ffffff").pack(anchor="w", pady=(0, 12))
        body = ttk.Frame(panel, style="Card.TFrame")
        body.pack(fill="both", expand=True)
        self.listbox = tk.Listbox(body, width=30, activestyle="none", relief="flat", borderwidth=0,
                                  highlightthickness=1, highlightbackground="#e2e8f0", highlightcolor="#93c5fd",
                                  bg="#ffffff", fg="#334155", selectbackground="#dbeafe",
                                  selectforeground="#1e40af", font=("Segoe UI", 9),
                                  selectborderwidth=0, exportselection=False)
        scroll = ttk.Scrollbar(body, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scroll.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        actions = ttk.Frame(panel, style="Card.TFrame")
        actions.pack(fill="x", pady=(9, 0))
        ttk.Button(actions, text="＋  Buat Baru", command=new_command, style="Accent.TButton").pack(side="left", fill="x", expand=True)
        ttk.Button(actions, text="Hapus", command=delete_command).pack(side="left", padx=(7, 0))
        return panel

    def field(self, parent, label, variable, row, *, values=None, readonly=False):
        ttk.Label(parent, text=label, background="#ffffff").grid(row=row, column=0, sticky="w", padx=(0, 12), pady=6)
        if values is not None:
            widget = ttk.Combobox(parent, textvariable=variable, values=values, width=37, state="readonly" if readonly else "normal")
        else:
            widget = ttk.Entry(parent, textvariable=variable, width=40)
        widget.grid(row=row, column=1, sticky="ew", pady=6)
        parent.grid_columnconfigure(1, weight=1)
        return widget

    def image_field(self, parent, variable, row, folder):
        ttk.Label(parent, text="Path gambar", background="#ffffff").grid(row=row, column=0, sticky="w", padx=(0, 12), pady=6)
        box = ttk.Frame(parent, style="Card.TFrame")
        box.grid(row=row, column=1, sticky="ew", pady=6)
        box.grid_columnconfigure(0, weight=1)
        ttk.Entry(box, textvariable=variable).grid(row=0, column=0, sticky="ew")
        ttk.Button(box, text="Pilih & salin...", command=lambda: copy_image(self, variable, folder)).grid(row=0, column=1, padx=(6, 0))
        ttk.Label(parent, text="Opsional. Gambar akan disalin ke folder assets yang sesuai.", background="#ffffff", foreground="#64748b", font=("Segoe UI", 8)).grid(row=row + 1, column=1, sticky="w")

    def refresh_list(self, selected_id=None):
        self.entries, errors = records(self.folder)
        self.listbox.delete(0, tk.END)
        chosen = None
        for i, (path, data) in enumerate(self.entries):
            item_id = str(data.get("id", path.stem))
            self.listbox.insert(tk.END, f"{data.get('name', item_id)}  ·  {item_id}")
            if selected_id == item_id:
                chosen = i
        if chosen is not None:
            self.listbox.selection_set(chosen)
            self.listbox.see(chosen)
        if errors:
            messagebox.showwarning("File JSON bermasalah", "\n".join(errors), parent=self)

    def selected(self):
        selection = self.listbox.curselection()
        return self.entries[selection[0]] if selection and selection[0] < len(self.entries) else None

    def check_id(self, item_id):
        for path, data in self.entries:
            if data.get("id") == item_id and path != self.current_path:
                raise ValueError(f"ID '{item_id}' sudah dipakai oleh {path.name}.")

    def delete_file(self, kind):
        selected = self.selected()
        if not selected:
            messagebox.showinfo("Pilih data", f"Pilih {kind} yang ingin dihapus terlebih dahulu.", parent=self)
            return
        path, data = selected
        if not messagebox.askyesno(f"Hapus {kind}?", f"Hapus '{data.get('name', path.stem)}'?", parent=self):
            return
        try:
            path.unlink()
            self.new_item()
            self.refresh_list()
            messagebox.showinfo("Berhasil", f"{kind.capitalize()} berhasil dihapus.", parent=self)
        except OSError as exc:
            messagebox.showerror("Gagal menghapus", str(exc), parent=self)


class IngredientTab(EditorTab):
    def __init__(self, parent, app):
        super().__init__(parent, app, ING_DIR)
        self.name, self.item_id = tk.StringVar(), tk.StringVar()
        self.category, self.price = tk.StringVar(value="other"), tk.StringVar(value="5")
        self.image, self.description = tk.StringVar(), tk.StringVar()
        split = ttk.Panedwindow(self, orient="horizontal")
        split.pack(fill="both", expand=True)
        left, right = ttk.Frame(split, style="Card.TFrame"), ttk.Frame(split, style="Card.TFrame", padding=22)
        split.add(left, weight=1); split.add(right, weight=3)
        self.after(100, lambda: split.sashpos(0, 300))
        self.build_left(left, "Daftar Bahan", self.new_item, lambda: self.delete_file("bahan"))
        self.listbox.bind("<<ListboxSelect>>", self.load_selected)
        ttk.Label(right, text="Buat dan kelola bahan", font=("Segoe UI", 16, "bold"), foreground="#17263c", background="#ffffff").pack(anchor="w", pady=(0, 3))
        ttk.Label(right, text="Lengkapi informasi bahan yang akan tersedia di market dan resep.", font=("Segoe UI", 9), foreground="#64748b", background="#ffffff").pack(anchor="w", pady=(0, 18))
        form = ttk.Frame(right, style="Card.TFrame"); form.pack(fill="x")
        self.field(form, "Nama bahan *", self.name, 0)
        self.field(form, "ID bahan *", self.item_id, 1)
        self.field(form, "Kategori *", self.category, 2, values=["meat", "vegetable", "other"])
        self.field(form, "Harga beli per unit *", self.price, 3)
        self.image_field(form, self.image, 4, ING_IMG)
        ttk.Label(form, text="Deskripsi", background="#ffffff").grid(row=6, column=0, sticky="w", padx=(0, 12), pady=6)
        ttk.Entry(form, textvariable=self.description).grid(row=6, column=1, sticky="ew", pady=6)
        ttk.Label(right, text="ID otomatis dibuat dari nama. Harga boleh 0. Kategori umum: meat, vegetable, other.",
                  background="#ffffff", foreground="#64748b", font=("Segoe UI", 8), wraplength=650).pack(anchor="w", pady=(8, 0))
        buttons = ttk.Frame(right, style="Card.TFrame"); buttons.pack(fill="x", pady=(18, 0))
        ttk.Button(buttons, text="Bersihkan / Bahan Baru", command=self.new_item).pack(side="left")
        ttk.Button(buttons, text="Simpan Bahan", command=self.save_item, style="Accent.TButton").pack(side="right")
        self.refresh_list(); self.new_item()

    def new_item(self):
        self.current_path = None
        if hasattr(self, "listbox"): self.listbox.selection_clear(0, tk.END)
        self.name.set(""); self.item_id.set(""); self.category.set("other")
        self.price.set("5"); self.image.set(""); self.description.set("")

    def load_selected(self, _event=None):
        selected = self.selected()
        if not selected: return
        path, data = selected; self.current_path = path
        self.name.set(str(data.get("name", ""))); self.item_id.set(str(data.get("id", "")))
        self.category.set(str(data.get("category", "other"))); self.price.set(str(data.get("market_price", 0)))
        self.image.set(str(data.get("image", ""))); self.description.set(str(data.get("description", "")))

    def save_item(self):
        name = self.name.get().strip()
        item_id = slugify(self.item_id.get()) or slugify(name)
        category = self.category.get().strip()
        if not name or not item_id or not category:
            messagebox.showerror("Data belum lengkap", "Nama, ID, dan kategori wajib diisi.", parent=self); return
        try:
            price = number(self.price.get(), "Harga bahan", integer=True, minimum=0)
            self.check_id(item_id)
            target = self.folder / f"{item_id}.json"
            if target.exists() and target != self.current_path:
                raise ValueError(f"File {target.name} sudah ada. Gunakan ID lain.")
            data = {"id": item_id, "name": name, "category": category, "market_price": price,
                    "image": self.image.get().strip(), "description": self.description.get().strip()}
            save_json(target, data)
            old = self.current_path; self.current_path = target
            if old and old != target: old.unlink(missing_ok=True)
            self.refresh_list(item_id); self.app.refresh_recipe_ingredients()
            messagebox.showinfo("Berhasil", f"Bahan '{name}' tersimpan di data/ingredients/{target.name}.", parent=self)
        except (ValueError, OSError) as exc:
            messagebox.showerror("Tidak dapat menyimpan bahan", str(exc), parent=self)


class StepDialog(tk.Toplevel):
    def __init__(self, parent, ingredients, step=None):
        super().__init__(parent)
        self.title("Atur bahan resep"); self.resizable(False, False)
        self.result = None; self.transient(parent); self.grab_set()
        self.lookup = {f"{x['name']} ({x['id']})": x["id"] for x in ingredients}
        reverse = {v: k for k, v in self.lookup.items()}
        self.choice = tk.StringVar(value=reverse.get(str((step or {}).get("id", "")), ""))
        self.quantity = tk.StringVar(value=str((step or {}).get("quantity", 1)))
        self.timing = tk.StringVar(value=str((step or {}).get("timing", 0)))
        body = ttk.Frame(self, padding=16); body.pack(fill="both", expand=True)
        ttk.Label(body, text="Bahan makanan").grid(row=0, column=0, sticky="w", padx=(0, 12), pady=6)
        combo = ttk.Combobox(body, textvariable=self.choice, values=list(self.lookup), state="readonly", width=36)
        combo.grid(row=0, column=1, sticky="ew", pady=6)
        ttk.Label(body, text="Jumlah unit").grid(row=1, column=0, sticky="w", padx=(0, 12), pady=6)
        ttk.Spinbox(body, from_=1, to=999, textvariable=self.quantity, width=12).grid(row=1, column=1, sticky="w", pady=6)
        ttk.Label(body, text="Timing (detik)").grid(row=2, column=0, sticky="w", padx=(0, 12), pady=6)
        ttk.Entry(body, textvariable=self.timing, width=14).grid(row=2, column=1, sticky="w", pady=6)
        ttk.Label(body, text="Jeda dari aksi memasak sebelumnya. Boleh 0 atau desimal.", foreground="#64748b",
                  font=("Segoe UI", 8)).grid(row=3, column=0, columnspan=2, sticky="w", pady=(2, 12))
        buttons = ttk.Frame(body); buttons.grid(row=4, column=0, columnspan=2, sticky="e")
        ttk.Button(buttons, text="Batal", command=self.destroy).pack(side="right")
        ttk.Button(buttons, text="Simpan", command=self._save, style="Accent.TButton").pack(side="right", padx=(0, 7))
        self.bind("<Return>", lambda _e: self._save()); self.bind("<Escape>", lambda _e: self.destroy())
        self.wait_visibility(); combo.focus_set()

    def _save(self):
        if self.choice.get() not in self.lookup:
            messagebox.showerror("Pilih bahan", "Pilih bahan dari daftar.", parent=self); return
        try:
            qty = number(self.quantity.get(), "Jumlah unit", integer=True, minimum=1)
            timing = number(self.timing.get(), "Timing", minimum=0)
        except ValueError as exc:
            messagebox.showerror("Nilai tidak valid", str(exc), parent=self); return
        self.result = {"id": self.lookup[self.choice.get()], "quantity": qty, "timing": timing}
        self.destroy()


class RecipeTab(EditorTab):
    """Recipe editor with a fixed list panel and an always-visible ingredient builder."""

    WHITE = "#ffffff"
    INK = "#17263c"
    MUTED = "#64748b"
    BORDER = "#dce4ee"
    SOFT = "#f5f8fc"
    BLUE = "#2563eb"

    def __init__(self, parent, app):
        super().__init__(parent, app, REC_DIR)
        self.name, self.item_id = tk.StringVar(), tk.StringVar()
        self.difficulty = tk.StringVar(value="easy")
        self.cooking_time = tk.StringVar(value="20")
        self.base_price = tk.StringVar(value="50")
        self.image, self.description = tk.StringVar(), tk.StringVar()
        self.steps: list[dict[str, Any]] = []
        self.ingredient_items: list[dict[str, str]] = []
        self.ingredient_lookup: dict[str, str] = {}
        self.step_choice = tk.StringVar()
        self.step_quantity = tk.StringVar(value="1")
        self.step_timing = tk.StringVar(value="0")
        self.editing_step: int | None = None

        # Grid layout is intentional: unlike the old Panedwindow sash, the list
        # cannot accidentally collapse to a few pixels on Windows/ttk themes.
        shell = ttk.Frame(self)
        shell.pack(fill="both", expand=True, padx=12, pady=12)
        shell.columnconfigure(0, minsize=245, weight=0)
        shell.columnconfigure(1, weight=1)
        shell.rowconfigure(0, weight=1)

        left = tk.Frame(shell, bg=self.WHITE, highlightthickness=1, highlightbackground=self.BORDER)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        right = tk.Frame(shell, bg=self.SOFT, highlightthickness=1, highlightbackground=self.BORDER)
        right.grid(row=0, column=1, sticky="nsew")

        self._build_recipe_list(left)
        self._build_recipe_form(right)
        self.refresh_ingredient_names()
        self.refresh_list()
        self.new_item()

    def refresh_list(self, selected_id=None):
        super().refresh_list(selected_id)
        if hasattr(self, "recipe_count"):
            self.recipe_count.set(f"{len(self.entries)} resep")

    def _section_title(self, parent, title: str, subtitle: str | None = None):
        tk.Label(parent, text=title, bg=self.WHITE, fg=self.INK,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w")
        if subtitle:
            tk.Label(parent, text=subtitle, bg=self.WHITE, fg=self.MUTED,
                     font=("Segoe UI", 8), wraplength=220, justify="left").pack(anchor="w", pady=(3, 0))

    def _build_recipe_list(self, parent):
        parent.configure(padx=14, pady=14)
        self._section_title(parent, "Daftar resep", "Pilih resep untuk melihat atau mengubahnya.")
        self.recipe_count = tk.StringVar(value="0 resep")
        tk.Label(parent, textvariable=self.recipe_count, bg=self.WHITE, fg=self.BLUE,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(12, 6))

        list_wrap = tk.Frame(parent, bg=self.WHITE)
        list_wrap.pack(fill="both", expand=True)
        self.listbox = tk.Listbox(
            list_wrap, relief="flat", borderwidth=0,
            highlightthickness=1, highlightbackground=self.BORDER, highlightcolor="#93c5fd",
            bg=self.WHITE, fg="#334155", selectbackground="#dbeafe",
            selectforeground="#1e40af", font=("Segoe UI", 9),
            selectborderwidth=0, exportselection=False, activestyle="none"
        )
        scroll = ttk.Scrollbar(list_wrap, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scroll.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.listbox.bind("<<ListboxSelect>>", self.load_selected)

        actions = tk.Frame(parent, bg=self.WHITE)
        actions.pack(fill="x", pady=(12, 0))
        ttk.Button(actions, text="＋  Resep baru", command=self.new_item,
                   style="Accent.TButton").pack(fill="x", pady=(0, 7))
        ttk.Button(actions, text="Hapus resep", command=lambda: self.delete_file("resep")).pack(fill="x")

    def _build_recipe_form(self, parent):
        parent.configure(padx=14, pady=12)
        # Header
        header = tk.Frame(parent, bg=self.SOFT)
        header.pack(fill="x", pady=(0, 10))
        tk.Label(header, text="Pembuat resep", bg=self.SOFT, fg=self.INK,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w")
        tk.Label(header, text="Isi detail masakan, lalu tambahkan bahan ke urutan memasak.",
                 bg=self.SOFT, fg=self.MUTED, font=("Segoe UI", 9)).pack(anchor="w", pady=(3, 0))

        # Pin save/clear actions to the bottom so they never disappear below
        # the expanding recipe-step table on smaller Windows displays.
        actions = tk.Frame(parent, bg=self.SOFT)
        actions.pack(side="bottom", fill="x", pady=(8, 0))
        ttk.Button(actions, text="Bersihkan form", command=self.new_item).pack(side="left")
        ttk.Button(actions, text="Simpan resep", command=self.save_item,
                   style="Accent.TButton").pack(side="right")

        # Compact metadata card: labels sit beside inputs to preserve height.
        details = tk.LabelFrame(parent, text="  Detail masakan  ", bg=self.WHITE, fg=self.INK,
                                font=("Segoe UI", 9, "bold"), bd=1, relief="solid",
                                highlightthickness=0, padx=9, pady=6)
        details.pack(fill="x", pady=(0, 8))
        for col in (1, 3, 4, 5):
            details.columnconfigure(col, weight=1)

        def inline(label, variable, row, label_col, input_col, *, values=None, colspan=1):
            tk.Label(details, text=label, bg=self.WHITE, fg=self.INK,
                     font=("Segoe UI", 8, "bold")).grid(
                         row=row, column=label_col, sticky="w", padx=(0, 5), pady=3)
            if values is not None:
                widget = ttk.Combobox(details, textvariable=variable, values=values,
                                      state="readonly", width=12)
            else:
                widget = ttk.Entry(details, textvariable=variable, width=16)
            widget.grid(row=row, column=input_col, columnspan=colspan,
                        sticky="ew", padx=(0, 9), pady=3)
            return widget

        inline("Nama *", self.name, 0, 0, 1)
        inline("ID resep *", self.item_id, 0, 2, 3, colspan=3)
        inline("Kesulitan", self.difficulty, 1, 0, 1, values=["easy", "normal", "hard"])
        inline("Waktu ambil (dtk) *", self.cooking_time, 1, 2, 3)
        inline("Harga jual *", self.base_price, 1, 4, 5)

        tk.Label(details, text="Gambar", bg=self.WHITE, fg=self.INK,
                 font=("Segoe UI", 8, "bold")).grid(row=2, column=0, sticky="w", padx=(0, 5), pady=2)
        ttk.Entry(details, textvariable=self.image).grid(row=2, column=1, sticky="ew", pady=2, padx=(0, 5))
        ttk.Button(details, text="Pilih…", command=lambda: copy_image(self, self.image, REC_IMG),
                   style="Compact.TButton").grid(row=2, column=2, sticky="ew", pady=2, padx=(0, 8))
        tk.Label(details, text="Deskripsi", bg=self.WHITE, fg=self.INK,
                 font=("Segoe UI", 8, "bold")).grid(row=2, column=3, sticky="w", padx=(0, 5), pady=2)
        ttk.Entry(details, textvariable=self.description).grid(
            row=2, column=4, columnspan=2, sticky="ew", pady=2)

        # Ingredient builder is a visible, inline editor. No modal window is
        # required, so ingredient selection cannot be hidden below the fold.
        steps = tk.LabelFrame(parent, text="  Urutan bahan saat memasak  ", bg=self.WHITE, fg=self.INK,
                              font=("Segoe UI", 9, "bold"), bd=1, relief="solid",
                              padx=10, pady=8)
        steps.pack(fill="both", expand=True)

        tk.Label(steps, text="Pilih bahan, jumlah unit, dan jeda waktunya. Maksimal 5 langkah per resep.",
                 bg=self.WHITE, fg=self.MUTED, font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 8))

        builder = tk.Frame(steps, bg=self.WHITE)
        builder.pack(fill="x", pady=(0, 6))
        builder.columnconfigure(0, weight=1)
        builder.columnconfigure(1, weight=0)
        builder.columnconfigure(2, weight=0)
        tk.Label(builder, text="Bahan makanan", bg=self.WHITE, fg=self.INK,
                 font=("Segoe UI", 8, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 8))
        tk.Label(builder, text="Jumlah", bg=self.WHITE, fg=self.INK,
                 font=("Segoe UI", 8, "bold")).grid(row=0, column=1, sticky="w", padx=(0, 8))
        tk.Label(builder, text="Timing (detik)", bg=self.WHITE, fg=self.INK,
                 font=("Segoe UI", 8, "bold")).grid(row=0, column=2, sticky="w")

        self.step_combo = ttk.Combobox(builder, textvariable=self.step_choice, state="readonly", width=34)
        self.step_combo.grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(3, 0))
        self.step_qty = ttk.Spinbox(builder, from_=1, to=999, textvariable=self.step_quantity, width=7)
        self.step_qty.grid(row=1, column=1, sticky="w", padx=(0, 8), pady=(3, 0))
        self.step_time = ttk.Entry(builder, textvariable=self.step_timing, width=10)
        self.step_time.grid(row=1, column=2, sticky="w", pady=(3, 0))

        builder_actions = tk.Frame(steps, bg=self.WHITE)
        builder_actions.pack(fill="x", pady=(6, 6))
        ttk.Button(builder_actions, text="＋ Tambah", command=self.add_step,
                   style="Accent.TButton").pack(side="left")
        ttk.Button(builder_actions, text="Perbarui", command=self.update_step,
                   style="Compact.TButton").pack(side="left", padx=(5, 0))
        ttk.Button(builder_actions, text="Hapus", command=self.remove_step,
                   style="Compact.TButton").pack(side="left", padx=(5, 0))
        ttk.Button(builder_actions, text="↑", command=lambda: self.move_step(-1),
                   style="Compact.TButton").pack(side="left", padx=(5, 0))
        ttk.Button(builder_actions, text="↓", command=lambda: self.move_step(1),
                   style="Compact.TButton").pack(side="left", padx=(5, 0))
        ttk.Button(builder_actions, text="Reset pilihan", command=self.clear_step_editor,
                   style="Compact.TButton").pack(side="left", padx=(5, 0))
        self.count_label = tk.Label(builder_actions, text="0 / 5 bahan", bg=self.WHITE, fg=self.BLUE,
                                    font=("Segoe UI", 8, "bold"))
        self.count_label.pack(side="right", padx=(4, 0))

        tree_wrap = tk.Frame(steps, bg=self.WHITE)
        tree_wrap.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(tree_wrap, columns=("no", "ingredient", "qty", "timing"),
                                 show="headings", height=2, selectmode="browse")
        self.tree.heading("no", text="#")
        self.tree.heading("ingredient", text="BAHAN")
        self.tree.heading("qty", text="JUMLAH")
        self.tree.heading("timing", text="TIMING")
        self.tree.column("no", width=42, minwidth=42, stretch=False, anchor="center")
        self.tree.column("ingredient", width=260, minwidth=130, stretch=True, anchor="w")
        self.tree.column("qty", width=82, minwidth=70, stretch=False, anchor="center")
        self.tree.column("timing", width=110, minwidth=85, stretch=False, anchor="center")
        tree_scroll = ttk.Scrollbar(tree_wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self._on_step_selected)


    def _field_cell(self, parent, label, variable, row, column, *, values=None,
                    readonly=False, colspan=1):
        cell = tk.Frame(parent, bg=self.WHITE)
        cell.grid(row=row, column=column, columnspan=colspan, sticky="ew",
                  padx=(0 if column == 0 else 7, 7 if column < 2 else 0), pady=4)
        cell.columnconfigure(0, weight=1)
        tk.Label(cell, text=label, bg=self.WHITE, fg=self.INK,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0, 3))
        if values is not None:
            widget = ttk.Combobox(cell, textvariable=variable, values=values,
                                  state="readonly" if readonly else "normal")
        else:
            widget = ttk.Entry(cell, textvariable=variable)
        widget.pack(fill="x")
        return widget

    def refresh_ingredient_names(self):
        data, errors = records(ING_DIR)
        self.ingredient_items = [
            {"id": str(d["id"]), "name": str(d.get("name", d["id"]))}
            for _p, d in data if d.get("id")
        ]
        self.ingredient_lookup = {f"{x['name']}  ·  {x['id']}": x["id"] for x in self.ingredient_items}
        if hasattr(self, "step_combo"):
            self.step_combo.configure(values=list(self.ingredient_lookup.keys()))
            # Keep a selected ingredient only if it still exists.
            if self.step_choice.get() not in self.ingredient_lookup:
                self.step_choice.set("")
            self.render_steps()
        if errors:
            messagebox.showwarning("File bahan bermasalah", "\n".join(errors), parent=self)

    def render_steps(self):
        if not hasattr(self, "tree"):
            return
        self.tree.delete(*self.tree.get_children())
        names = {x["id"]: x["name"] for x in self.ingredient_items}
        for i, step in enumerate(self.steps):
            self.tree.insert("", "end", iid=str(i), values=(
                f"{i + 1:02d}", names.get(step.get("id"), f"Bahan tidak ditemukan: {step.get('id', '?')}"),
                step.get("quantity", 1), f"{step.get('timing', 0)} dtk"
            ))
        self.count_label.configure(text=f"{len(self.steps)} / {MAX_STEPS} bahan")

    def selected_step(self):
        selected = self.tree.selection()
        if not selected:
            return None
        try:
            index = int(selected[0])
        except (TypeError, ValueError):
            return None
        return index if 0 <= index < len(self.steps) else None

    def _on_step_selected(self, _event=None):
        index = self.selected_step()
        if index is None:
            return
        step = self.steps[index]
        display = next((label for label, item_id in self.ingredient_lookup.items()
                        if item_id == step.get("id")), "")
        self.step_choice.set(display)
        self.step_quantity.set(str(step.get("quantity", 1)))
        self.step_timing.set(str(step.get("timing", 0)))
        self.editing_step = index

    def clear_step_editor(self):
        self.tree.selection_remove(self.tree.selection())
        self.editing_step = None
        self.step_choice.set("")
        self.step_quantity.set("1")
        self.step_timing.set("0")

    def _read_step_form(self):
        choice = self.step_choice.get()
        if choice not in self.ingredient_lookup:
            raise ValueError("Pilih bahan makanan dari daftar terlebih dahulu.")
        qty = number(self.step_quantity.get(), "Jumlah unit", integer=True, minimum=1)
        timing = number(self.step_timing.get(), "Timing", minimum=0)
        return {"id": self.ingredient_lookup[choice], "quantity": qty, "timing": timing}

    def add_step(self):
        if len(self.steps) >= MAX_STEPS:
            messagebox.showwarning("Batas bahan", "Satu resep maksimal 5 langkah bahan.", parent=self)
            return
        if not self.ingredient_items:
            messagebox.showwarning("Belum ada bahan", "Tambahkan bahan di tab Bahan Makanan terlebih dahulu.", parent=self)
            return
        try:
            self.steps.append(self._read_step_form())
        except ValueError as exc:
            messagebox.showerror("Data langkah belum valid", str(exc), parent=self)
            return
        self.render_steps()
        self.clear_step_editor()

    def update_step(self):
        index = self.selected_step()
        if index is None:
            messagebox.showinfo("Pilih langkah", "Klik satu baris bahan di tabel yang ingin diperbarui.", parent=self)
            return
        try:
            updated = self._read_step_form()
        except ValueError as exc:
            messagebox.showerror("Data langkah belum valid", str(exc), parent=self)
            return
        self.steps[index] = updated
        self.render_steps()
        self.tree.selection_set(str(index))
        self.tree.focus(str(index))

    def edit_step(self):
        # Compatibility alias for older callers/documentation.
        self.update_step()

    def remove_step(self):
        index = self.selected_step()
        if index is None:
            messagebox.showinfo("Pilih langkah", "Klik satu baris bahan yang ingin dihapus.", parent=self)
            return
        self.steps.pop(index)
        self.render_steps()
        self.clear_step_editor()

    def move_step(self, direction: int):
        index = self.selected_step()
        if index is None:
            messagebox.showinfo("Pilih langkah", "Klik satu baris bahan yang ingin dipindahkan.", parent=self)
            return
        target = index + direction
        if not 0 <= target < len(self.steps):
            return
        self.steps[index], self.steps[target] = self.steps[target], self.steps[index]
        self.render_steps()
        self.tree.selection_set(str(target))
        self.tree.focus(str(target))

    def new_item(self):
        self.current_path = None
        if hasattr(self, "listbox"):
            self.listbox.selection_clear(0, tk.END)
        self.name.set("")
        self.item_id.set("")
        self.difficulty.set("easy")
        self.cooking_time.set("20")
        self.base_price.set("50")
        self.image.set("")
        self.description.set("")
        self.steps = []
        if hasattr(self, "tree"):
            self.render_steps()
            self.clear_step_editor()

    def load_selected(self, _event=None):
        selected = self.selected()
        if not selected:
            return
        path, data = selected
        self.current_path = path
        self.name.set(str(data.get("name", "")))
        self.item_id.set(str(data.get("id", "")))
        self.difficulty.set(str(data.get("difficulty", "easy")))
        self.cooking_time.set(str(data.get("cooking_time", 20)))
        self.base_price.set(str(data.get("base_price", 50)))
        self.image.set(str(data.get("image", "")))
        self.description.set(str(data.get("description", "")))
        self.steps = [dict(x) for x in data.get("ingredients", []) if isinstance(x, dict)]
        self.render_steps()
        self.clear_step_editor()

    def save_item(self):
        name = self.name.get().strip()
        item_id = slugify(self.item_id.get()) or slugify(name)
        difficulty = self.difficulty.get().strip()
        if not name or not item_id:
            messagebox.showerror("Data belum lengkap", "Nama dan ID resep wajib diisi.", parent=self)
            return
        if difficulty not in {"easy", "normal", "hard"}:
            messagebox.showerror("Kesulitan tidak valid", "Pilih easy, normal, atau hard.", parent=self)
            return
        if not 1 <= len(self.steps) <= MAX_STEPS:
            messagebox.showerror("Jumlah bahan tidak valid", "Resep harus berisi 1 sampai 5 langkah bahan.", parent=self)
            return
        available = {x["id"] for x in self.ingredient_items}
        missing = [x.get("id", "?") for x in self.steps if x.get("id") not in available]
        if missing:
            messagebox.showerror("Bahan tidak ditemukan", "Bahan ini tidak tersedia: " + ", ".join(missing), parent=self)
            return
        try:
            cook_time = number(self.cooking_time.get(), "Waktu mengambil makanan", minimum=0)
            price = number(self.base_price.get(), "Harga dasar jual", integer=True, minimum=1)
            self.check_id(item_id)
            target = self.folder / f"{item_id}.json"
            if target.exists() and target != self.current_path:
                raise ValueError(f"File {target.name} sudah ada. Gunakan ID lain.")
            data = {
                "id": item_id,
                "name": name,
                "difficulty": difficulty,
                "ingredients": self.steps,
                "cooking_time": cook_time,
                "base_price": price,
                "image": self.image.get().strip(),
                "description": self.description.get().strip(),
            }
            save_json(target, data)
            old = self.current_path
            self.current_path = target
            if old and old != target:
                old.unlink(missing_ok=True)
            self.refresh_list(item_id)
            messagebox.showinfo("Berhasil", f"Resep '{name}' tersimpan di data/recipes/{target.name}.", parent=self)
        except (ValueError, OSError) as exc:
            messagebox.showerror("Tidak dapat menyimpan resep", str(exc), parent=self)

if __name__ == "__main__":
    try:
        Editor().mainloop()
    except tk.TclError as exc:
        print(f"Content Editor tidak dapat membuka jendela: {exc}")
        print("Pastikan Python di Windows terpasang dengan dukungan Tkinter.")
        raise
