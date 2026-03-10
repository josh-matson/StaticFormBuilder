#!/usr/bin/env python3
"""
Drag-and-Drop HTML Form Builder
A tkinter application for visually building static HTML forms.
"""

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
import json
import re
import os

# ─── Theme Definitions ──────────────────────────────────────────────────────────

THEMES = {
    "Clean / Minimal": {
        "font_family": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
        "bg": "#ffffff", "text": "#333333", "accent": "#0066cc",
        "input_bg": "#ffffff", "input_border": "#cccccc", "input_radius": "2px",
        "label_weight": "600", "label_size": "0.9rem",
        "button_bg": "#0066cc", "button_text": "#ffffff", "button_radius": "3px",
        "shadow": "none", "form_padding": "2rem",
        "form_bg": "#ffffff", "form_border": "1px solid #e0e0e0",
        "extra_css": "",
        "preview": {
            "bg": "#ffffff", "form_bg": "#ffffff", "border": "#e0e0e0",
            "label": "#333333", "input_bg": "#ffffff", "input_bd": "#cccccc",
            "btn_bg": "#0066cc", "btn_fg": "#ffffff", "radius": 2,
        }
    },
    "Modern / Rounded": {
        "font_family": "'Inter', 'SF Pro Display', sans-serif",
        "bg": "#f0f4f8", "text": "#1a202c", "accent": "#4f7df9",
        "input_bg": "#ffffff", "input_border": "#e2e8f0", "input_radius": "10px",
        "label_weight": "500", "label_size": "0.85rem",
        "button_bg": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "button_text": "#ffffff", "button_radius": "10px",
        "shadow": "0 4px 24px rgba(0,0,0,0.08)", "form_padding": "2.5rem",
        "form_bg": "#ffffff", "form_border": "none",
        "extra_css": """
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    input:focus, textarea:focus, select:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102,126,234,0.15);
    }""",
        "preview": {
            "bg": "#f0f4f8", "form_bg": "#ffffff", "border": "#e2e8f0",
            "label": "#1a202c", "input_bg": "#ffffff", "input_bd": "#e2e8f0",
            "btn_bg": "#667eea", "btn_fg": "#ffffff", "radius": 10,
        }
    },
    "Classic / Formal": {
        "font_family": "'Georgia', 'Times New Roman', serif",
        "bg": "#faf8f5", "text": "#2c2c2c", "accent": "#8b4513",
        "input_bg": "#fffef9", "input_border": "#c4b99a", "input_radius": "0px",
        "label_weight": "700", "label_size": "0.9rem",
        "button_bg": "#8b4513", "button_text": "#ffffff", "button_radius": "0px",
        "shadow": "none", "form_padding": "2rem",
        "form_bg": "#fffef9", "form_border": "2px solid #c4b99a",
        "extra_css": """
    input, textarea, select {
        border-width: 2px;
    }
    h2 { font-style: italic; letter-spacing: 0.05em; }""",
        "preview": {
            "bg": "#faf8f5", "form_bg": "#fffef9", "border": "#c4b99a",
            "label": "#2c2c2c", "input_bg": "#fffef9", "input_bd": "#c4b99a",
            "btn_bg": "#8b4513", "btn_fg": "#ffffff", "radius": 0,
        }
    },
}

# ─── Element types ──────────────────────────────────────────────────────────────

ELEMENT_TYPES = [
    ("Text Input", "text"),
    ("Textarea", "textarea"),
    ("Checkbox", "checkbox"),
    ("Radio Button", "radio"),
    ("Dropdown", "select"),
    ("Date Picker", "date"),
    ("File Upload", "file"),
    ("Submit Button", "submit"),
]

NEEDS_OPTIONS = {"radio", "select", "checkbox"}

ELEMENT_ICONS = {
    "text": "Aa", "textarea": "¶", "checkbox": "☑", "radio": "◉",
    "select": "▾", "date": "📅", "file": "📎", "submit": "➤",
}


# ─── Theme Picker Dialog ───────────────────────────────────────────────────────

class ThemePickerDialog(tk.Toplevel):
    def __init__(self, parent, current_theme):
        super().__init__(parent)
        self.title("Choose a Theme")
        self.configure(bg="#1e1e2e")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.result = None

        tk.Label(self, text="SELECT A THEME", fg="#a6adc8", bg="#1e1e2e",
                 font=("Segoe UI", 10, "bold")).pack(pady=(16, 12))

        cards_frame = tk.Frame(self, bg="#1e1e2e")
        cards_frame.pack(padx=16, pady=(0, 16))

        for i, (name, theme) in enumerate(THEMES.items()):
            self._build_theme_card(cards_frame, name, theme["preview"], i, name == current_theme)

        tk.Button(self, text="Cancel", fg="#a6adc8", bg="#2a2a3d",
                  activebackground="#363655", font=("Segoe UI", 9),
                  relief=tk.FLAT, padx=16, pady=4, cursor="hand2",
                  command=self.destroy).pack(pady=(0, 12))

        self.update_idletasks()
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{px + (pw - w) // 2}+{py + (ph - h) // 2}")

    def _build_theme_card(self, parent, name, p, col, is_active):
        highlight = "#cba6f7" if is_active else "#45475a"
        outer = tk.Frame(parent, bg=highlight, padx=2, pady=2)
        outer.grid(row=0, column=col, padx=8, pady=4)

        card = tk.Frame(outer, bg="#2a2a3d", width=190, height=230)
        card.grid_propagate(False)
        card.pack_propagate(False)
        card.pack()

        name_lbl = tk.Label(card, text=name, fg="#cdd6f4", bg="#2a2a3d",
                            font=("Segoe UI", 9, "bold"))
        name_lbl.pack(pady=(8, 6))

        canvas = tk.Canvas(card, width=170, height=150, bg=p["bg"],
                           highlightthickness=1, highlightbackground=p["border"])
        canvas.pack(padx=10, pady=(0, 4))
        self._draw_form_preview(canvas, p)

        if is_active:
            btn_lbl = tk.Label(card, text="✓ Selected", fg="#a6e3a1", bg="#2a2a3d",
                               font=("Segoe UI", 9, "bold"))
        else:
            btn_lbl = tk.Label(card, text="Select", fg="#89b4fa", bg="#2a2a3d",
                               font=("Segoe UI", 9), cursor="hand2")
        btn_lbl.pack(pady=(2, 6))

        def select(e=None):
            self.result = name
            self.destroy()

        if not is_active:
            for w in (outer, card, name_lbl, canvas, btn_lbl):
                w.bind("<Button-1>", select)
                if w != canvas:
                    w.configure(cursor="hand2")

    def _draw_form_preview(self, canvas, p):
        cx, cy, w = 10, 10, 150
        r = min(p["radius"], 6)
        ir = min(p["radius"], 4)
        self._rrect(canvas, 5, 5, 165, 145, r, p["form_bg"], p["border"])

        canvas.create_text(cx+4, cy+4, text="Full Name", anchor="nw",
                           font=("Segoe UI", 7, "bold"), fill=p["label"])
        iy = cy + 18
        self._rrect(canvas, cx+2, iy, cx+w-2, iy+18, ir, p["input_bg"], p["input_bd"])

        canvas.create_text(cx+4, iy+26, text="Email Address", anchor="nw",
                           font=("Segoe UI", 7, "bold"), fill=p["label"])
        iy2 = iy + 40
        self._rrect(canvas, cx+2, iy2, cx+w-2, iy2+18, ir, p["input_bg"], p["input_bd"])

        canvas.create_text(cx+4, iy2+26, text="Message", anchor="nw",
                           font=("Segoe UI", 7, "bold"), fill=p["label"])
        iy3 = iy2 + 40
        self._rrect(canvas, cx+2, iy3, cx+w-2, iy3+14, ir, p["input_bg"], p["input_bd"])

        by = iy3 + 20
        br = min(p["radius"], 4)
        self._rrect(canvas, cx+2, by, cx+56, by+16, br, p["btn_bg"], p["btn_bg"])
        canvas.create_text(cx+29, by+8, text="Submit",
                           font=("Segoe UI", 6, "bold"), fill=p["btn_fg"])

    def _rrect(self, canvas, x1, y1, x2, y2, r, fill, outline):
        if r <= 1:
            canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=outline, width=1)
            return
        pts = [x1+r,y1, x2-r,y1, x2,y1, x2,y1+r, x2,y2-r, x2,y2,
               x2-r,y2, x1+r,y2, x1,y2, x1,y2-r, x1,y1+r, x1,y1, x1+r,y1]
        canvas.create_polygon(pts, fill=fill, outline=outline, smooth=True, width=1)


# ─── Options Dialog ─────────────────────────────────────────────────────────────

class OptionsDialog(tk.Toplevel):
    def __init__(self, parent, element_type, label):
        super().__init__(parent)
        self.title(f"Options for: {label}")
        self.configure(bg="#1e1e2e")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.result = None

        type_names = {"radio": "radio button", "select": "dropdown", "checkbox": "checkbox group"}
        tk.Label(self, text=f"Enter options for this {type_names.get(element_type, element_type)}:",
                 fg="#cdd6f4", bg="#1e1e2e", font=("Segoe UI", 10)).pack(padx=20, pady=(16, 4))
        tk.Label(self, text="One option per line", fg="#6c7086", bg="#1e1e2e",
                 font=("Segoe UI", 8)).pack(padx=20, pady=(0, 8))

        text_frame = tk.Frame(self, bg="#2a2a3d", padx=2, pady=2)
        text_frame.pack(padx=20, pady=(0, 12), fill=tk.BOTH)
        self.text = tk.Text(text_frame, width=35, height=8, bg="#2a2a3d", fg="#cdd6f4",
                            insertbackground="#cdd6f4", font=("Segoe UI", 10),
                            relief=tk.FLAT, wrap=tk.WORD, selectbackground="#45475a")
        self.text.pack(padx=4, pady=4)

        defaults = {"radio": "Option A\nOption B\nOption C",
                     "select": "Option 1\nOption 2\nOption 3",
                     "checkbox": "Choice 1\nChoice 2\nChoice 3"}
        self.text.insert("1.0", defaults.get(element_type, ""))
        self.text.tag_add("sel", "1.0", "end")
        self.text.focus_set()

        btn_frame = tk.Frame(self, bg="#1e1e2e")
        btn_frame.pack(pady=(0, 16))
        tk.Button(btn_frame, text="✓ Confirm", fg="#1e1e2e", bg="#a6e3a1",
                  activebackground="#94d990", font=("Segoe UI", 10, "bold"),
                  relief=tk.FLAT, padx=16, pady=4, cursor="hand2",
                  command=self._confirm).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_frame, text="Cancel", fg="#a6adc8", bg="#45475a",
                  activebackground="#585b70", font=("Segoe UI", 10),
                  relief=tk.FLAT, padx=16, pady=4, cursor="hand2",
                  command=self._cancel).pack(side=tk.LEFT, padx=4)

        self.update_idletasks()
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{px + (pw - w) // 2}+{py + (ph - h) // 2}")
        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self.wait_window()

    def _confirm(self):
        raw = self.text.get("1.0", tk.END).strip()
        options = [l.strip() for l in raw.split("\n") if l.strip()]
        if not options:
            messagebox.showwarning("No Options", "Please enter at least one option.", parent=self)
            return
        self.result = options
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()


# ─── Main Application ──────────────────────────────────────────────────────────

class FormBuilder(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HTML Form Builder")
        self.geometry("1100x750")
        self.minsize(900, 600)
        self.configure(bg="#1e1e2e")

        self.form_elements = []
        self.columns = 1
        self.selected_theme = "Clean / Minimal"
        self.selected_index = None
        self.current_save_path = None

        # Drag state
        self.drag_data = {
            "active": False,
            "source": None,       # "sidebar" or "canvas"
            "element_type": None,  # for sidebar drags
            "source_index": None,  # for canvas reorder drags
            "insert_index": None,  # computed insertion point
            "widget": None,        # floating drag indicator label
        }

        # Element card position tracking for insertion detection
        self.card_widgets = []     # list of (outer_frame, element_index)
        self.insert_indicator = None  # the visual insertion line widget

        self._build_ui()
        self._bind_keyboard_shortcuts()

    # ── UI ──────────────────────────────────────────────────────────────────

    def _build_ui(self):
        self._build_toolbar()
        main = tk.Frame(self, bg="#1e1e2e")
        main.pack(fill=tk.BOTH, expand=True)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)
        self._build_sidebar(main)
        self._build_canvas(main)

    def _bind_keyboard_shortcuts(self):
        self.bind("<Control-s>", lambda e: self._save_project())
        self.bind("<Control-S>", lambda e: self._save_project_as())
        self.bind("<Control-o>", lambda e: self._load_project())
        self.bind("<Control-e>", lambda e: self._export_html())

    def _build_toolbar(self):
        toolbar = tk.Frame(self, bg="#2a2a3d", height=50)
        toolbar.pack(fill=tk.X, side=tk.TOP)
        toolbar.pack_propagate(False)

        tk.Label(toolbar, text="⬡ Form Builder", fg="#cdd6f4", bg="#2a2a3d",
                 font=("Segoe UI", 14, "bold")).pack(side=tk.LEFT, padx=16)
        tk.Frame(toolbar, bg="#45475a", width=1).pack(side=tk.LEFT, fill=tk.Y, pady=8)

        tk.Label(toolbar, text="  Columns:", fg="#a6adc8", bg="#2a2a3d",
                 font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(12, 4))
        self.col_label = tk.Label(toolbar, text="1", fg="#cdd6f4", bg="#45475a",
                                  font=("Segoe UI", 11, "bold"), width=3, relief=tk.FLAT)
        self.col_label.pack(side=tk.LEFT)

        tk.Label(toolbar, text="  Theme:", fg="#a6adc8", bg="#2a2a3d",
                 font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(16, 4))
        self.theme_btn = tk.Button(toolbar, text="Clean / Minimal  ▾", fg="#cdd6f4",
                                   bg="#45475a", activebackground="#585b70",
                                   font=("Segoe UI", 10), relief=tk.FLAT, padx=10, pady=2,
                                   cursor="hand2", command=self._open_theme_picker)
        self.theme_btn.pack(side=tk.LEFT, padx=4)

        # Right-side buttons
        tk.Button(toolbar, text="📤 Export HTML", fg="#1e1e2e", bg="#a6e3a1",
                  activebackground="#94d990", font=("Segoe UI", 10, "bold"),
                  relief=tk.FLAT, padx=14, pady=4, cursor="hand2",
                  command=self._export_html).pack(side=tk.RIGHT, padx=12)
        tk.Button(toolbar, text="🗑 Clear", fg="#cdd6f4", bg="#f38ba8",
                  activebackground="#e07a96", font=("Segoe UI", 10, "bold"),
                  relief=tk.FLAT, padx=10, pady=4, cursor="hand2",
                  command=self._clear_all).pack(side=tk.RIGHT, padx=4)
        tk.Frame(toolbar, bg="#45475a", width=1).pack(side=tk.RIGHT, fill=tk.Y, pady=8, padx=6)
        tk.Button(toolbar, text="📂 Open", fg="#cdd6f4", bg="#89b4fa",
                  activebackground="#74a8f7", font=("Segoe UI", 10, "bold"),
                  relief=tk.FLAT, padx=10, pady=4, cursor="hand2",
                  command=self._load_project).pack(side=tk.RIGHT, padx=4)
        tk.Button(toolbar, text="Save As", fg="#cdd6f4", bg="#45475a",
                  activebackground="#585b70", font=("Segoe UI", 10),
                  relief=tk.FLAT, padx=10, pady=4, cursor="hand2",
                  command=self._save_project_as).pack(side=tk.RIGHT, padx=2)
        tk.Button(toolbar, text="💾 Save", fg="#1e1e2e", bg="#f9e2af",
                  activebackground="#f5d58a", font=("Segoe UI", 10, "bold"),
                  relief=tk.FLAT, padx=10, pady=4, cursor="hand2",
                  command=self._save_project).pack(side=tk.RIGHT, padx=2)

    def _build_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg="#282840", width=200)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)

        tk.Label(sidebar, text="ELEMENTS", fg="#a6adc8", bg="#282840",
                 font=("Segoe UI", 9, "bold"), anchor="w").pack(fill=tk.X, padx=16, pady=(16, 8))
        tk.Label(sidebar, text="Drag onto canvas →", fg="#6c7086", bg="#282840",
                 font=("Segoe UI", 8), anchor="w").pack(fill=tk.X, padx=16, pady=(0, 12))

        for display_name, etype in ELEMENT_TYPES:
            icon = ELEMENT_ICONS.get(etype, "•")
            frame = tk.Frame(sidebar, bg="#313150", cursor="hand2")
            frame.pack(fill=tk.X, padx=10, pady=3)

            icon_lbl = tk.Label(frame, text=icon, fg="#cba6f7", bg="#313150",
                                font=("Segoe UI", 14), width=2)
            icon_lbl.pack(side=tk.LEFT, padx=(8, 4), pady=6)
            text_lbl = tk.Label(frame, text=display_name, fg="#cdd6f4", bg="#313150",
                                font=("Segoe UI", 10), anchor="w")
            text_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=6)

            for w in (frame, icon_lbl, text_lbl):
                w.bind("<ButtonPress-1>", lambda e, t=etype: self._sidebar_drag_start(e, t))
                w.bind("<B1-Motion>", self._drag_motion)
                w.bind("<ButtonRelease-1>", self._drag_end)
                w.bind("<Enter>", lambda e, f=frame, il=icon_lbl, tl=text_lbl: (
                    f.configure(bg="#3b3b5c"), il.configure(bg="#3b3b5c"), tl.configure(bg="#3b3b5c")))
                w.bind("<Leave>", lambda e, f=frame, il=icon_lbl, tl=text_lbl: (
                    f.configure(bg="#313150"), il.configure(bg="#313150"), tl.configure(bg="#313150")))

    def _build_canvas(self, parent):
        canvas_wrapper = tk.Frame(parent, bg="#1e1e2e")
        canvas_wrapper.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        canvas_wrapper.rowconfigure(0, weight=1)
        canvas_wrapper.columnconfigure(0, weight=1)

        self.canvas_scroll = tk.Canvas(canvas_wrapper, bg="#1e1e2e", highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_wrapper, orient=tk.VERTICAL, command=self.canvas_scroll.yview)

        self.canvas_inner = tk.Frame(self.canvas_scroll, bg="#1e1e2e")
        self.canvas_inner.bind("<Configure>", lambda e: self.canvas_scroll.configure(
            scrollregion=self.canvas_scroll.bbox("all")))
        self.canvas_scroll.create_window((0, 0), window=self.canvas_inner, anchor="nw", tags="inner")
        self.canvas_scroll.configure(yscrollcommand=scrollbar.set)

        self.canvas_scroll.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas_scroll.bind("<Configure>", self._on_canvas_resize)
        self.canvas_scroll.bind("<MouseWheel>", lambda e: self.canvas_scroll.yview_scroll(
            int(-1 * (e.delta / 120)), "units"))

        # Global motion/release on the whole window so drags work smoothly
        self.bind("<B1-Motion>", self._drag_motion)
        self.bind("<ButtonRelease-1>", self._drag_end)

        # Floating column button
        btn_frame = tk.Frame(canvas_wrapper, bg="#1e1e2e")
        btn_frame.place(relx=1.0, rely=1.0, anchor="se", x=-24, y=-24)
        tk.Button(btn_frame, text="+", fg="#1e1e2e", bg="#f9e2af",
                  activebackground="#f5d58a", font=("Segoe UI", 18, "bold"),
                  relief=tk.FLAT, width=2, height=1, cursor="hand2",
                  command=self._cycle_columns).pack()
        tk.Label(btn_frame, text="Cols", fg="#6c7086", bg="#1e1e2e",
                 font=("Segoe UI", 8)).pack()

        self._refresh_canvas()

    def _on_canvas_resize(self, event):
        self.canvas_scroll.itemconfig("inner", width=event.width)

    # ── Theme Picker ────────────────────────────────────────────────────────

    def _open_theme_picker(self):
        dialog = ThemePickerDialog(self, self.selected_theme)
        self.wait_window(dialog)
        if dialog.result:
            self.selected_theme = dialog.result
            self.theme_btn.configure(text=f"{self.selected_theme}  ▾")

    # ── Drag & Drop System ──────────────────────────────────────────────────

    def _create_drag_ghost(self, text, event):
        """Create the floating label that follows the cursor during drag."""
        if self.drag_data.get("widget"):
            self.drag_data["widget"].destroy()
        ghost = tk.Label(self, text=text, fg="#cdd6f4", bg="#45475a",
                         font=("Segoe UI", 10, "bold"), relief=tk.SOLID, bd=1,
                         padx=8, pady=4)
        ghost.place(x=event.x_root - self.winfo_rootx() + 12,
                    y=event.y_root - self.winfo_rooty() - 10)
        # Make sure ghost doesn't eat mouse events
        ghost.bind("<B1-Motion>", self._drag_motion)
        ghost.bind("<ButtonRelease-1>", self._drag_end)
        self.drag_data["widget"] = ghost

    def _sidebar_drag_start(self, event, element_type):
        """Start a drag from the sidebar element picker."""
        name = next(d for d, t in ELEMENT_TYPES if t == element_type)
        icon = ELEMENT_ICONS.get(element_type, "•")

        self.drag_data.update({
            "active": True,
            "source": "sidebar",
            "element_type": element_type,
            "source_index": None,
            "insert_index": None,
        })
        self._create_drag_ghost(f" {icon}  {name} ", event)

    def _canvas_drag_start(self, event, index):
        """Start a drag from an existing canvas card to reorder."""
        el = self.form_elements[index]
        icon = ELEMENT_ICONS.get(el["type"], "•")

        self.drag_data.update({
            "active": True,
            "source": "canvas",
            "element_type": None,
            "source_index": index,
            "insert_index": None,
        })
        self._create_drag_ghost(f" {icon}  {el['label']} ", event)

        # Dim the source card
        self._refresh_canvas(dimmed_index=index)

    def _drag_motion(self, event):
        """Handle drag motion — update ghost position and insertion indicator."""
        if not self.drag_data["active"]:
            return

        # Move ghost
        ghost = self.drag_data.get("widget")
        if ghost:
            ghost.place(x=event.x_root - self.winfo_rootx() + 12,
                        y=event.y_root - self.winfo_rooty() - 10)

        # Check if cursor is over the canvas area
        canvas_x = self.canvas_scroll.winfo_rootx()
        canvas_y = self.canvas_scroll.winfo_rooty()
        canvas_w = self.canvas_scroll.winfo_width()
        canvas_h = self.canvas_scroll.winfo_height()
        mx, my = event.x_root, event.y_root

        if canvas_x <= mx <= canvas_x + canvas_w and canvas_y <= my <= canvas_y + canvas_h:
            self._update_insertion_indicator(my)
        else:
            self._remove_insertion_indicator()
            self.drag_data["insert_index"] = None

    def _drag_end(self, event):
        """Handle drop — insert or reorder element at the computed position."""
        if not self.drag_data["active"]:
            return

        # Clean up ghost
        ghost = self.drag_data.get("widget")
        if ghost:
            ghost.destroy()
            self.drag_data["widget"] = None

        source = self.drag_data["source"]
        insert_idx = self.drag_data["insert_index"]

        self._remove_insertion_indicator()
        self.drag_data["active"] = False

        # Check if we're over the canvas
        canvas_x = self.canvas_scroll.winfo_rootx()
        canvas_w = self.canvas_scroll.winfo_width()
        mx = event.x_root

        if mx < canvas_x or mx > canvas_x + canvas_w:
            # Dropped outside canvas — cancel
            if source == "canvas":
                self._refresh_canvas()
            return

        if source == "sidebar":
            etype = self.drag_data["element_type"]
            if insert_idx is None:
                insert_idx = len(self.form_elements)  # append at end
            self._prompt_and_add_element(etype, insert_idx)

        elif source == "canvas":
            src_idx = self.drag_data["source_index"]
            if insert_idx is None:
                insert_idx = len(self.form_elements)

            # Adjust index since we're moving within the same list
            if src_idx is not None and src_idx != insert_idx and insert_idx != src_idx + 1:
                el = self.form_elements.pop(src_idx)
                # After removing, adjust target index
                if insert_idx > src_idx:
                    insert_idx -= 1
                self.form_elements.insert(insert_idx, el)
                self.selected_index = insert_idx

            self._refresh_canvas()

    def _update_insertion_indicator(self, mouse_y):
        """Calculate which gap the cursor is over and show the indicator line."""
        if not self.card_widgets:
            self.drag_data["insert_index"] = 0
            return

        # Convert mouse_y (screen coords) to position relative to canvas_inner
        inner_y = mouse_y - self.canvas_inner.winfo_rooty()

        best_idx = len(self.form_elements)  # default: end
        best_y = None  # y position for the indicator in canvas_inner coords

        # Gather midpoints and gap positions for all cards
        card_positions = []
        for card_frame, elem_idx in self.card_widgets:
            try:
                cy = card_frame.winfo_rooty() - self.canvas_inner.winfo_rooty()
                ch = card_frame.winfo_height()
                mid = cy + ch // 2
                card_positions.append((elem_idx, cy, ch, mid))
            except tk.TclError:
                continue

        if not card_positions:
            self.drag_data["insert_index"] = 0
            return

        # Find insertion point
        src_idx = self.drag_data.get("source_index")

        # Before the first card
        first_cy = card_positions[0][1]
        if inner_y < card_positions[0][3]:
            best_idx = 0
            best_y = first_cy - 3
        else:
            # Between cards or after last
            for i, (eidx, cy, ch, mid) in enumerate(card_positions):
                if inner_y < mid:
                    best_idx = eidx
                    best_y = cy - 3
                    break
            else:
                # After the last card
                last = card_positions[-1]
                best_idx = last[0] + 1
                best_y = last[1] + last[2] + 1

        # Skip showing indicator at the source card's own position (no-op)
        if src_idx is not None and (best_idx == src_idx or best_idx == src_idx + 1):
            self._remove_insertion_indicator()
            self.drag_data["insert_index"] = src_idx
            return

        self.drag_data["insert_index"] = best_idx

        # Show or move the indicator line
        if best_y is not None:
            self._show_insertion_indicator(best_y)

    def _show_insertion_indicator(self, y_pos):
        """Display a colored horizontal line at y_pos within canvas_inner."""
        if self.insert_indicator is None:
            self.insert_indicator = tk.Frame(self.canvas_inner, bg="#cba6f7", height=3)
        self.insert_indicator.place(x=12, y=y_pos, relwidth=0.95, height=3)
        self.insert_indicator.lift()

    def _remove_insertion_indicator(self):
        """Hide the insertion indicator."""
        if self.insert_indicator:
            self.insert_indicator.place_forget()

    # ── Element Add / Edit ──────────────────────────────────────────────────

    def _prompt_and_add_element(self, etype, insert_index=None):
        display_name = next(d for d, t in ELEMENT_TYPES if t == etype)

        if etype == "submit":
            label = simpledialog.askstring("Submit Button", "Enter button text:",
                                           initialvalue="Submit", parent=self)
        else:
            label = simpledialog.askstring(f"New {display_name}",
                                           f"Enter label for this {display_name}:", parent=self)
        if not label:
            self._refresh_canvas()
            return

        element_id = re.sub(r'[^a-zA-Z0-9]+', '_', label.strip()).strip('_').lower()
        if not element_id:
            element_id = f"field_{len(self.form_elements)}"

        existing_ids = [el["id"] for el in self.form_elements]
        base_id = element_id
        counter = 1
        while element_id in existing_ids:
            element_id = f"{base_id}_{counter}"
            counter += 1

        options = []
        if etype in NEEDS_OPTIONS:
            dialog = OptionsDialog(self, etype, label)
            if dialog.result is None:
                self._refresh_canvas()
                return
            options = dialog.result

        new_el = {"type": etype, "label": label, "id": element_id, "options": options}

        if insert_index is not None and insert_index < len(self.form_elements):
            self.form_elements.insert(insert_index, new_el)
        else:
            self.form_elements.append(new_el)

        self._refresh_canvas()

    # ── Canvas Rendering ────────────────────────────────────────────────────

    def _refresh_canvas(self, dimmed_index=None):
        for widget in self.canvas_inner.winfo_children():
            widget.destroy()
        self.card_widgets = []
        self.insert_indicator = None

        if not self.form_elements:
            tk.Label(self.canvas_inner,
                     text="🎯  Drag elements here to build your form",
                     fg="#6c7086", bg="#1e1e2e", font=("Segoe UI", 13)).pack(pady=120)
            return

        # Title
        title_frame = tk.Frame(self.canvas_inner, bg="#1e1e2e")
        title_frame.pack(fill=tk.X, padx=12, pady=(12, 4))
        tk.Label(title_frame, text="Form Preview", fg="#cdd6f4", bg="#1e1e2e",
                 font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT)
        n = len(self.form_elements)
        tk.Label(title_frame, text=f"{n} element{'s' if n != 1 else ''}",
                 fg="#6c7086", bg="#1e1e2e", font=("Segoe UI", 9)).pack(side=tk.RIGHT)

        # Render in grid
        cols = self.columns
        row_frame = None
        for i, el in enumerate(self.form_elements):
            col_in_row = i % cols
            if col_in_row == 0:
                row_frame = tk.Frame(self.canvas_inner, bg="#1e1e2e")
                row_frame.pack(fill=tk.X, padx=12, pady=2)
                for c in range(cols):
                    row_frame.columnconfigure(c, weight=1, uniform="col")

            is_dimmed = (dimmed_index is not None and i == dimmed_index)
            card = self._make_element_card(row_frame, el, i, is_dimmed)
            card.grid(row=0, column=col_in_row, sticky="nsew", padx=4, pady=4)

            # Track card position for insertion detection
            self.card_widgets.append((card, i))

        # Bottom drop zone
        drop = tk.Label(self.canvas_inner, text="＋ Drop more elements here",
                        fg="#585b70", bg="#232338", font=("Segoe UI", 10), pady=20)
        drop.pack(fill=tk.X, padx=16, pady=(8, 16))

    def _make_element_card(self, parent, el, index, is_dimmed=False):
        is_selected = (index == self.selected_index) and not is_dimmed

        if is_dimmed:
            bg = "#222238"
            border_color = "#363655"
        elif is_selected:
            bg = "#363655"
            border_color = "#cba6f7"
        else:
            bg = "#2a2a3d"
            border_color = "#45475a"

        outer = tk.Frame(parent, bg=border_color, padx=1, pady=1)
        card = tk.Frame(outer, bg=bg)
        card.pack(fill=tk.BOTH, expand=True)

        fg_main = "#585b70" if is_dimmed else "#cdd6f4"
        fg_sub = "#45475a" if is_dimmed else "#a6adc8"
        fg_id = "#3b3b5c" if is_dimmed else "#585b70"

        # ── Top row: type label + actions ──
        top = tk.Frame(card, bg=bg)
        top.pack(fill=tk.X, padx=10, pady=(8, 2))

        icon = ELEMENT_ICONS.get(el["type"], "•")
        type_name = next(d for d, t in ELEMENT_TYPES if t == el["type"])
        tk.Label(top, text=f"{icon} {type_name}", fg=fg_sub, bg=bg,
                 font=("Segoe UI", 8)).pack(side=tk.LEFT)

        # Drag handle
        drag_handle = tk.Label(top, text="⠿", fg="#6c7086" if not is_dimmed else "#3b3b5c",
                               bg=bg, font=("Segoe UI", 12), cursor="fleur")
        drag_handle.pack(side=tk.LEFT, padx=(8, 0))

        if not is_dimmed:
            del_btn = tk.Label(top, text="✕", fg="#f38ba8", bg=bg,
                               font=("Segoe UI", 10, "bold"), cursor="hand2")
            del_btn.pack(side=tk.RIGHT)
            del_btn.bind("<Button-1>", lambda e, idx=index: self._delete_element(idx))

            if index > 0:
                up_btn = tk.Label(top, text="▲", fg="#a6adc8", bg=bg,
                                  font=("Segoe UI", 8), cursor="hand2")
                up_btn.pack(side=tk.RIGHT, padx=4)
                up_btn.bind("<Button-1>", lambda e, idx=index: self._move_element(idx, -1))

            if index < len(self.form_elements) - 1:
                down_btn = tk.Label(top, text="▼", fg="#a6adc8", bg=bg,
                                    font=("Segoe UI", 8), cursor="hand2")
                down_btn.pack(side=tk.RIGHT, padx=2)
                down_btn.bind("<Button-1>", lambda e, idx=index: self._move_element(idx, 1))

        # Label
        tk.Label(card, text=el["label"], fg=fg_main, bg=bg,
                 font=("Segoe UI", 11, "bold"), anchor="w").pack(fill=tk.X, padx=10, pady=(2, 1))

        # ID
        tk.Label(card, text=f"id: {el['id']}", fg=fg_id, bg=bg,
                 font=("Consolas", 8), anchor="w").pack(fill=tk.X, padx=10, pady=(0, 2))

        # Options display
        options = el.get("options", [])
        if options:
            opts_text = ", ".join(options[:5])
            if len(options) > 5:
                opts_text += f" (+{len(options) - 5} more)"
            tk.Label(card, text=f"Options: {opts_text}", fg=fg_sub, bg=bg,
                     font=("Segoe UI", 8), anchor="w", wraplength=250
                     ).pack(fill=tk.X, padx=10, pady=(0, 2))

        # Mini preview
        if not is_dimmed:
            self._render_mini_preview(card, el, bg)

        tk.Frame(card, bg=bg, height=6).pack()

        # ── Bind drag-to-reorder on the drag handle ──
        if not is_dimmed:
            drag_handle.bind("<ButtonPress-1>", lambda e, idx=index: self._canvas_drag_start(e, idx))

            # Click card to select
            def _select_click(e, idx=index):
                self._select_element(idx)
            for w in (card,):
                w.bind("<Button-1>", _select_click)

        return outer

    def _render_mini_preview(self, parent, el, bg):
        etype = el["type"]
        options = el.get("options", [])
        preview = tk.Frame(parent, bg=bg)
        preview.pack(fill=tk.X, padx=10, pady=2)

        if etype == "text":
            e = tk.Entry(preview, bg="#3b3b5c", fg="#cdd6f4", relief=tk.FLAT,
                         insertbackground="#cdd6f4", font=("Segoe UI", 9))
            e.insert(0, "  Text input...")
            e.configure(state="disabled")
            e.pack(fill=tk.X)
        elif etype == "textarea":
            tk.Text(preview, bg="#3b3b5c", fg="#cdd6f4", relief=tk.FLAT,
                    height=2, font=("Segoe UI", 9), state="disabled").pack(fill=tk.X)
        elif etype == "checkbox":
            if options:
                for opt in options[:4]:
                    tk.Checkbutton(preview, text=opt, bg=bg, fg="#cdd6f4",
                                   selectcolor="#3b3b5c", activebackground=bg,
                                   font=("Segoe UI", 9)).pack(anchor="w")
                if len(options) > 4:
                    tk.Label(preview, text=f"  +{len(options)-4} more...",
                             fg="#6c7086", bg=bg, font=("Segoe UI", 8)).pack(anchor="w")
            else:
                tk.Checkbutton(preview, text=el["label"], bg=bg, fg="#cdd6f4",
                               selectcolor="#3b3b5c", activebackground=bg,
                               font=("Segoe UI", 9)).pack(anchor="w")
        elif etype == "radio":
            if options:
                for opt in options[:4]:
                    tk.Radiobutton(preview, text=opt, bg=bg, fg="#cdd6f4",
                                   selectcolor="#3b3b5c", activebackground=bg,
                                   font=("Segoe UI", 9)).pack(anchor="w")
                if len(options) > 4:
                    tk.Label(preview, text=f"  +{len(options)-4} more...",
                             fg="#6c7086", bg=bg, font=("Segoe UI", 8)).pack(anchor="w")
            else:
                tk.Radiobutton(preview, text="Option", bg=bg, fg="#cdd6f4",
                               selectcolor="#3b3b5c", activebackground=bg,
                               font=("Segoe UI", 9)).pack(anchor="w")
        elif etype == "select":
            display_vals = options[:5] if options else ["Option 1", "Option 2"]
            cb = ttk.Combobox(preview, values=display_vals, state="disabled", width=20)
            cb.set(display_vals[0] if display_vals else "Select...")
            cb.pack(fill=tk.X)
        elif etype == "date":
            e = tk.Entry(preview, bg="#3b3b5c", fg="#cdd6f4", relief=tk.FLAT,
                         font=("Segoe UI", 9))
            e.insert(0, "  yyyy-mm-dd")
            e.configure(state="disabled")
            e.pack(fill=tk.X)
        elif etype == "file":
            tk.Label(preview, text="📂 Choose file...", fg="#a6adc8", bg="#3b3b5c",
                     font=("Segoe UI", 9), anchor="w", padx=6, pady=3).pack(fill=tk.X)
        elif etype == "submit":
            tk.Label(preview, text=el["label"], fg="#1e1e2e", bg="#a6e3a1",
                     font=("Segoe UI", 10, "bold"), pady=4).pack(fill=tk.X)

    # ── Element Actions ─────────────────────────────────────────────────────

    def _select_element(self, index):
        self.selected_index = index
        self._refresh_canvas()

    def _delete_element(self, index):
        del self.form_elements[index]
        self.selected_index = None
        self._refresh_canvas()

    def _move_element(self, index, direction):
        new_index = index + direction
        if 0 <= new_index < len(self.form_elements):
            self.form_elements[index], self.form_elements[new_index] = \
                self.form_elements[new_index], self.form_elements[index]
            self.selected_index = new_index
            self._refresh_canvas()

    def _cycle_columns(self):
        self.columns = (self.columns % 3) + 1
        self.col_label.config(text=str(self.columns))
        self._refresh_canvas()

    def _clear_all(self):
        if not self.form_elements:
            return
        if messagebox.askyesno("Clear All", "Remove all form elements?"):
            self.form_elements.clear()
            self.selected_index = None
            self._refresh_canvas()

    # ── Save / Load ─────────────────────────────────────────────────────────

    def _get_project_data(self):
        return {"version": 2, "theme": self.selected_theme,
                "columns": self.columns, "elements": self.form_elements}

    def _load_project_data(self, data):
        self.selected_theme = data.get("theme", "Clean / Minimal")
        self.columns = data.get("columns", 1)
        self.form_elements = data.get("elements", [])
        for el in self.form_elements:
            if "options" not in el:
                el["options"] = []
        self.selected_index = None
        self.col_label.config(text=str(self.columns))
        self.theme_btn.configure(text=f"{self.selected_theme}  ▾")
        self._refresh_canvas()

    def _save_project(self):
        if self.current_save_path:
            self._write_project(self.current_save_path)
        else:
            self._save_project_as()

    def _save_project_as(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".formbuilder",
            filetypes=[("Form Builder Project", "*.formbuilder"), ("JSON Files", "*.json")],
            initialfile="my_form.formbuilder", title="Save Project")
        if not filepath:
            return
        self.current_save_path = filepath
        self._write_project(filepath)

    def _write_project(self, filepath):
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self._get_project_data(), f, indent=2, ensure_ascii=False)
            self.title(f"HTML Form Builder — {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save project:\n{e}")

    def _load_project(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Form Builder Project", "*.formbuilder"),
                       ("JSON Files", "*.json"), ("All Files", "*.*")],
            title="Open Project")
        if not filepath:
            return
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.current_save_path = filepath
            self._load_project_data(data)
            self.title(f"HTML Form Builder — {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Load Error", f"Could not load project:\n{e}")

    # ── HTML Export ──────────────────────────────────────────────────────────

    def _export_html(self):
        if not self.form_elements:
            messagebox.showwarning("Empty Form", "Add some elements first!")
            return
        theme = THEMES[self.selected_theme]
        filepath = filedialog.asksaveasfilename(
            defaultextension=".html", filetypes=[("HTML Files", "*.html")],
            initialfile="form.html", title="Export Form as HTML")
        if not filepath:
            return
        html = self._generate_html(theme, self.columns)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        messagebox.showinfo("Exported!", f"Form saved to:\n{filepath}")

    def _generate_html(self, theme, cols):
        elements_html = ""
        for el in self.form_elements:
            elements_html += self._element_to_html(el)

        grid_css = ""
        if cols > 1:
            grid_css = f"""
    .form-grid {{
        display: grid;
        grid-template-columns: repeat({cols}, 1fr);
        gap: 1.25rem;
    }}
    .form-grid .form-group {{ margin-bottom: 0; }}
    @media (max-width: 600px) {{ .form-grid {{ grid-template-columns: 1fr; }} }}"""

        btn_bg = theme["button_bg"]
        button_style = f"background: {btn_bg};" if btn_bg.startswith("linear") else f"background-color: {btn_bg};"

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Form</title>
    <style>
    {theme['extra_css']}
    *, *::before, *::after {{ box-sizing: border-box; }}
    body {{
        font-family: {theme['font_family']};
        background-color: {theme['bg']}; color: {theme['text']};
        margin: 0; padding: 2rem; line-height: 1.6;
    }}
    .form-container {{
        max-width: 720px; margin: 0 auto;
        background: {theme['form_bg']}; border: {theme['form_border']};
        border-radius: {theme['input_radius']}; box-shadow: {theme['shadow']};
        padding: {theme['form_padding']};
    }}
    .form-group {{ margin-bottom: 1.25rem; }}
    label {{
        display: block; margin-bottom: 0.35rem;
        font-weight: {theme['label_weight']}; font-size: {theme['label_size']};
        color: {theme['text']};
    }}
    input[type="text"], input[type="date"], input[type="file"], textarea, select {{
        width: 100%; padding: 0.6rem 0.8rem;
        border: 1px solid {theme['input_border']};
        border-radius: {theme['input_radius']};
        background-color: {theme['input_bg']}; color: {theme['text']};
        font-family: inherit; font-size: 0.95rem;
        transition: border-color 0.2s, box-shadow 0.2s; outline: none;
    }}
    textarea {{ resize: vertical; min-height: 80px; }}
    input[type="checkbox"], input[type="radio"] {{
        margin-right: 0.5rem; accent-color: {theme['accent']};
    }}
    .checkbox-label, .radio-label {{
        display: flex; align-items: center;
        font-weight: normal; cursor: pointer; margin-bottom: 0.35rem;
    }}
    button[type="submit"] {{
        {button_style} color: {theme['button_text']}; border: none;
        border-radius: {theme['button_radius']}; padding: 0.75rem 2rem;
        font-size: 1rem; font-weight: 600; cursor: pointer;
        transition: opacity 0.2s; font-family: inherit;
    }}
    button[type="submit"]:hover {{ opacity: 0.9; }}
    {grid_css}
    </style>
</head>
<body>
    <div class="form-container">
        <form action="#" method="POST">
            {"<div class='form-grid'>" if cols > 1 else ""}
{elements_html}
            {"</div>" if cols > 1 else ""}
        </form>
    </div>
</body>
</html>"""

    def _element_to_html(self, el):
        etype, label, eid = el["type"], el["label"], el["id"]
        options = el.get("options", [])
        ind = "            "

        if etype == "text":
            return f'{ind}<div class="form-group">\n{ind}    <label for="{eid}">{label}</label>\n{ind}    <input type="text" id="{eid}" name="{eid}" placeholder="Enter {label.lower()}">\n{ind}</div>\n'
        elif etype == "textarea":
            return f'{ind}<div class="form-group">\n{ind}    <label for="{eid}">{label}</label>\n{ind}    <textarea id="{eid}" name="{eid}" placeholder="Enter {label.lower()}"></textarea>\n{ind}</div>\n'
        elif etype == "checkbox":
            if options:
                items = ""
                for opt in options:
                    ov = re.sub(r'[^a-zA-Z0-9]+', '_', opt.strip()).strip('_').lower()
                    items += f'{ind}    <label class="checkbox-label">\n{ind}        <input type="checkbox" id="{eid}_{ov}" name="{eid}" value="{ov}">\n{ind}        {opt}\n{ind}    </label>\n'
                return f'{ind}<div class="form-group">\n{ind}    <label>{label}</label>\n{items}{ind}</div>\n'
            return f'{ind}<div class="form-group">\n{ind}    <label class="checkbox-label">\n{ind}        <input type="checkbox" id="{eid}" name="{eid}">\n{ind}        {label}\n{ind}    </label>\n{ind}</div>\n'
        elif etype == "radio":
            if options:
                items = ""
                for opt in options:
                    ov = re.sub(r'[^a-zA-Z0-9]+', '_', opt.strip()).strip('_').lower()
                    items += f'{ind}    <label class="radio-label">\n{ind}        <input type="radio" id="{eid}_{ov}" name="{eid}" value="{ov}">\n{ind}        {opt}\n{ind}    </label>\n'
                return f'{ind}<div class="form-group">\n{ind}    <label>{label}</label>\n{items}{ind}</div>\n'
            return f'{ind}<div class="form-group">\n{ind}    <label class="radio-label">\n{ind}        <input type="radio" id="{eid}" name="{eid}" value="{eid}">\n{ind}        {label}\n{ind}    </label>\n{ind}</div>\n'
        elif etype == "select":
            oh = f'{ind}        <option value="" disabled selected>Select {label.lower()}...</option>\n'
            if options:
                for opt in options:
                    ov = re.sub(r'[^a-zA-Z0-9]+', '_', opt.strip()).strip('_').lower()
                    oh += f'{ind}        <option value="{ov}">{opt}</option>\n'
            else:
                for i in range(1, 4):
                    oh += f'{ind}        <option value="option{i}">Option {i}</option>\n'
            return f'{ind}<div class="form-group">\n{ind}    <label for="{eid}">{label}</label>\n{ind}    <select id="{eid}" name="{eid}">\n{oh}{ind}    </select>\n{ind}</div>\n'
        elif etype == "date":
            return f'{ind}<div class="form-group">\n{ind}    <label for="{eid}">{label}</label>\n{ind}    <input type="date" id="{eid}" name="{eid}">\n{ind}</div>\n'
        elif etype == "file":
            return f'{ind}<div class="form-group">\n{ind}    <label for="{eid}">{label}</label>\n{ind}    <input type="file" id="{eid}" name="{eid}">\n{ind}</div>\n'
        elif etype == "submit":
            return f'{ind}<div class="form-group">\n{ind}    <button type="submit">{label}</button>\n{ind}</div>\n'
        return ""


# ─── Entry Point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = FormBuilder()
    app.mainloop()
