#!/usr/bin/env python3
"""
Drag-and-Drop HTML Form Builder
A tkinter application for visually building static HTML forms.
"""

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog, font as tkfont
import json
import re
import os

# ─── Theme Definitions (for HTML export) ───────────────────────────────────────

THEMES = {
    "Clean / Minimal": {
        "font_family": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
        "bg": "#ffffff",
        "text": "#333333",
        "accent": "#0066cc",
        "input_bg": "#ffffff",
        "input_border": "#cccccc",
        "input_radius": "2px",
        "label_weight": "600",
        "label_size": "0.9rem",
        "button_bg": "#0066cc",
        "button_text": "#ffffff",
        "button_radius": "3px",
        "shadow": "none",
        "form_padding": "2rem",
        "form_bg": "#ffffff",
        "form_border": "1px solid #e0e0e0",
        "extra_css": "",
    },
    "Modern / Rounded": {
        "font_family": "'Inter', 'SF Pro Display', sans-serif",
        "bg": "#f0f4f8",
        "text": "#1a202c",
        "accent": "#4f7df9",
        "input_bg": "#ffffff",
        "input_border": "#e2e8f0",
        "input_radius": "10px",
        "label_weight": "500",
        "label_size": "0.85rem",
        "button_bg": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "button_text": "#ffffff",
        "button_radius": "10px",
        "shadow": "0 4px 24px rgba(0,0,0,0.08)",
        "form_padding": "2.5rem",
        "form_bg": "#ffffff",
        "form_border": "none",
        "extra_css": """
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    input:focus, textarea:focus, select:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102,126,234,0.15);
    }""",
    },
    "Classic / Formal": {
        "font_family": "'Georgia', 'Times New Roman', serif",
        "bg": "#faf8f5",
        "text": "#2c2c2c",
        "accent": "#8b4513",
        "input_bg": "#fffef9",
        "input_border": "#c4b99a",
        "input_radius": "0px",
        "label_weight": "700",
        "label_size": "0.9rem",
        "button_bg": "#8b4513",
        "button_text": "#ffffff",
        "button_radius": "0px",
        "shadow": "none",
        "form_padding": "2rem",
        "form_bg": "#fffef9",
        "form_border": "2px solid #c4b99a",
        "extra_css": """
    input, textarea, select {
        border-width: 2px;
    }
    h2 { font-style: italic; letter-spacing: 0.05em; }""",
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

ELEMENT_ICONS = {
    "text": "Aa",
    "textarea": "¶",
    "checkbox": "☑",
    "radio": "◉",
    "select": "▾",
    "date": "📅",
    "file": "📎",
    "submit": "➤",
}


# ─── Main Application ──────────────────────────────────────────────────────────

class FormBuilder(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HTML Form Builder")
        self.geometry("1100x750")
        self.minsize(900, 600)
        self.configure(bg="#1e1e2e")

        self.form_elements = []  # list of dicts
        self.columns = 1
        self.selected_theme = tk.StringVar(value="Clean / Minimal")
        self.selected_index = None  # currently selected element index
        self.drag_data = {"type": None, "widget": None}

        self._build_ui()

    # ── UI Construction ─────────────────────────────────────────────────────

    def _build_ui(self):
        # Top toolbar
        self._build_toolbar()

        # Main content area
        main = tk.Frame(self, bg="#1e1e2e")
        main.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        # Left sidebar: element picker
        self._build_sidebar(main)

        # Center: canvas / form preview
        self._build_canvas(main)

    def _build_toolbar(self):
        toolbar = tk.Frame(self, bg="#2a2a3d", height=50)
        toolbar.pack(fill=tk.X, side=tk.TOP)
        toolbar.pack_propagate(False)

        # Title
        tk.Label(
            toolbar, text="⬡ Form Builder", fg="#cdd6f4",
            bg="#2a2a3d", font=("Segoe UI", 14, "bold")
        ).pack(side=tk.LEFT, padx=16)

        # Separator
        tk.Frame(toolbar, bg="#45475a", width=1).pack(side=tk.LEFT, fill=tk.Y, pady=8)

        # Column indicator
        tk.Label(
            toolbar, text="  Columns:", fg="#a6adc8",
            bg="#2a2a3d", font=("Segoe UI", 10)
        ).pack(side=tk.LEFT, padx=(12, 4))

        self.col_label = tk.Label(
            toolbar, text="1", fg="#cdd6f4",
            bg="#45475a", font=("Segoe UI", 11, "bold"),
            width=3, relief=tk.FLAT
        )
        self.col_label.pack(side=tk.LEFT)

        # Theme selector
        tk.Label(
            toolbar, text="  Theme:", fg="#a6adc8",
            bg="#2a2a3d", font=("Segoe UI", 10)
        ).pack(side=tk.LEFT, padx=(16, 4))

        theme_menu = ttk.Combobox(
            toolbar, textvariable=self.selected_theme,
            values=list(THEMES.keys()), state="readonly", width=18
        )
        theme_menu.pack(side=tk.LEFT, padx=4)

        # Right side buttons
        export_btn = tk.Button(
            toolbar, text="💾 Export HTML", fg="#1e1e2e", bg="#a6e3a1",
            activebackground="#94d990", font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT, padx=14, pady=4, cursor="hand2",
            command=self._export_html
        )
        export_btn.pack(side=tk.RIGHT, padx=12)

        clear_btn = tk.Button(
            toolbar, text="🗑 Clear All", fg="#cdd6f4", bg="#f38ba8",
            activebackground="#e07a96", font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT, padx=14, pady=4, cursor="hand2",
            command=self._clear_all
        )
        clear_btn.pack(side=tk.RIGHT, padx=4)

    def _build_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg="#282840", width=200)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)

        # Header
        tk.Label(
            sidebar, text="ELEMENTS", fg="#a6adc8", bg="#282840",
            font=("Segoe UI", 9, "bold"), anchor="w"
        ).pack(fill=tk.X, padx=16, pady=(16, 8))

        # Drag hint
        tk.Label(
            sidebar, text="Drag onto canvas →", fg="#6c7086", bg="#282840",
            font=("Segoe UI", 8), anchor="w"
        ).pack(fill=tk.X, padx=16, pady=(0, 12))

        # Element buttons
        for display_name, etype in ELEMENT_TYPES:
            icon = ELEMENT_ICONS.get(etype, "•")
            frame = tk.Frame(sidebar, bg="#313150", cursor="hand2")
            frame.pack(fill=tk.X, padx=10, pady=3)

            icon_lbl = tk.Label(
                frame, text=icon, fg="#cba6f7", bg="#313150",
                font=("Segoe UI", 14), width=2
            )
            icon_lbl.pack(side=tk.LEFT, padx=(8, 4), pady=6)

            text_lbl = tk.Label(
                frame, text=display_name, fg="#cdd6f4", bg="#313150",
                font=("Segoe UI", 10), anchor="w"
            )
            text_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=6)

            # Bind drag events to the frame and its children
            for widget in (frame, icon_lbl, text_lbl):
                widget.bind("<ButtonPress-1>", lambda e, t=etype: self._drag_start(e, t))
                widget.bind("<B1-Motion>", self._drag_motion)
                widget.bind("<ButtonRelease-1>", self._drag_end)

                # Hover effects
                widget.bind("<Enter>", lambda e, f=frame: f.configure(bg="#3b3b5c"))
                widget.bind("<Leave>", lambda e, f=frame: f.configure(bg="#313150"))
                widget.bind("<Enter>", lambda e, f=frame, il=icon_lbl, tl=text_lbl: (
                    f.configure(bg="#3b3b5c"),
                    il.configure(bg="#3b3b5c"),
                    tl.configure(bg="#3b3b5c"),
                ))
                widget.bind("<Leave>", lambda e, f=frame, il=icon_lbl, tl=text_lbl: (
                    f.configure(bg="#313150"),
                    il.configure(bg="#313150"),
                    tl.configure(bg="#313150"),
                ))

    def _build_canvas(self, parent):
        canvas_wrapper = tk.Frame(parent, bg="#1e1e2e")
        canvas_wrapper.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        canvas_wrapper.rowconfigure(0, weight=1)
        canvas_wrapper.columnconfigure(0, weight=1)

        # Scrollable canvas area
        self.canvas_scroll = tk.Canvas(canvas_wrapper, bg="#1e1e2e", highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_wrapper, orient=tk.VERTICAL, command=self.canvas_scroll.yview)

        self.canvas_inner = tk.Frame(self.canvas_scroll, bg="#1e1e2e")
        self.canvas_inner.bind("<Configure>", lambda e: self.canvas_scroll.configure(
            scrollregion=self.canvas_scroll.bbox("all")
        ))
        self.canvas_scroll.create_window((0, 0), window=self.canvas_inner, anchor="nw", tags="inner")
        self.canvas_scroll.configure(yscrollcommand=scrollbar.set)

        self.canvas_scroll.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Bind resize to adjust inner frame width
        self.canvas_scroll.bind("<Configure>", self._on_canvas_resize)

        # Drop zone label (shown when empty)
        self.drop_label = tk.Label(
            self.canvas_inner,
            text="🎯  Drag elements here to build your form",
            fg="#6c7086", bg="#1e1e2e",
            font=("Segoe UI", 13)
        )
        self.drop_label.pack(pady=120)

        # Floating column add button
        self._build_column_button(canvas_wrapper)

        # Bind canvas for drop target
        for w in (self.canvas_scroll, self.canvas_inner, self.drop_label):
            w.bind("<ButtonRelease-1>", self._drag_end)

        # Enable mousewheel scrolling
        self.canvas_scroll.bind("<MouseWheel>", lambda e: self.canvas_scroll.yview_scroll(
            int(-1 * (e.delta / 120)), "units"
        ))

    def _on_canvas_resize(self, event):
        self.canvas_scroll.itemconfig("inner", width=event.width)

    def _build_column_button(self, parent):
        btn_frame = tk.Frame(parent, bg="#1e1e2e")
        btn_frame.place(relx=1.0, rely=1.0, anchor="se", x=-24, y=-24)

        col_btn = tk.Button(
            btn_frame, text="+", fg="#1e1e2e", bg="#f9e2af",
            activebackground="#f5d58a",
            font=("Segoe UI", 18, "bold"),
            relief=tk.FLAT, width=2, height=1, cursor="hand2",
            command=self._cycle_columns
        )
        col_btn.pack()

        tk.Label(
            btn_frame, text="Cols", fg="#6c7086", bg="#1e1e2e",
            font=("Segoe UI", 8)
        ).pack()

    # ── Drag & Drop ─────────────────────────────────────────────────────────

    def _drag_start(self, event, element_type):
        self.drag_data["type"] = element_type

        # Create a floating drag indicator
        if self.drag_data.get("widget"):
            self.drag_data["widget"].destroy()

        name = next(d for d, t in ELEMENT_TYPES if t == element_type)
        icon = ELEMENT_ICONS.get(element_type, "•")

        drag_label = tk.Label(
            self, text=f" {icon}  {name} ", fg="#cdd6f4", bg="#45475a",
            font=("Segoe UI", 10, "bold"), relief=tk.SOLID, bd=1,
            padx=8, pady=4
        )
        drag_label.place(x=event.x_root - self.winfo_rootx(),
                         y=event.y_root - self.winfo_rooty())
        self.drag_data["widget"] = drag_label

    def _drag_motion(self, event):
        if self.drag_data.get("widget"):
            x = event.x_root - self.winfo_rootx()
            y = event.y_root - self.winfo_rooty()
            self.drag_data["widget"].place(x=x + 12, y=y - 10)

    def _drag_end(self, event):
        if self.drag_data.get("widget"):
            self.drag_data["widget"].destroy()
            self.drag_data["widget"] = None

        if not self.drag_data["type"]:
            return

        # Check if dropped on canvas area (rough check)
        drop_x = event.x_root - self.winfo_rootx()
        etype = self.drag_data["type"]
        self.drag_data["type"] = None

        # Only add if dropped roughly on the right side (canvas area)
        if drop_x > 200:
            self._prompt_and_add_element(etype)

    def _prompt_and_add_element(self, etype):
        display_name = next(d for d, t in ELEMENT_TYPES if t == etype)

        if etype == "submit":
            label = simpledialog.askstring(
                "Submit Button",
                "Enter button text:",
                initialvalue="Submit",
                parent=self
            )
        else:
            label = simpledialog.askstring(
                f"New {display_name}",
                f"Enter label for this {display_name}:",
                parent=self
            )

        if not label:
            return

        # Generate ID from label
        element_id = re.sub(r'[^a-zA-Z0-9]+', '_', label.strip()).strip('_').lower()
        if not element_id:
            element_id = f"field_{len(self.form_elements)}"

        # Ensure unique ID
        existing_ids = [el["id"] for el in self.form_elements]
        base_id = element_id
        counter = 1
        while element_id in existing_ids:
            element_id = f"{base_id}_{counter}"
            counter += 1

        self.form_elements.append({
            "type": etype,
            "label": label,
            "id": element_id,
        })

        self._refresh_canvas()

    # ── Canvas Rendering ────────────────────────────────────────────────────

    def _refresh_canvas(self):
        for widget in self.canvas_inner.winfo_children():
            widget.destroy()

        if not self.form_elements:
            self.drop_label = tk.Label(
                self.canvas_inner,
                text="🎯  Drag elements here to build your form",
                fg="#6c7086", bg="#1e1e2e",
                font=("Segoe UI", 13)
            )
            self.drop_label.pack(pady=120)
            return

        # Title area
        title_frame = tk.Frame(self.canvas_inner, bg="#1e1e2e")
        title_frame.pack(fill=tk.X, padx=12, pady=(12, 4))
        tk.Label(
            title_frame, text="Form Preview", fg="#cdd6f4", bg="#1e1e2e",
            font=("Segoe UI", 12, "bold")
        ).pack(side=tk.LEFT)

        count_text = f"{len(self.form_elements)} element{'s' if len(self.form_elements) != 1 else ''}"
        tk.Label(
            title_frame, text=count_text, fg="#6c7086", bg="#1e1e2e",
            font=("Segoe UI", 9)
        ).pack(side=tk.RIGHT)

        # Render elements in column grid
        cols = self.columns
        row_frame = None

        for i, el in enumerate(self.form_elements):
            col_in_row = i % cols
            if col_in_row == 0:
                row_frame = tk.Frame(self.canvas_inner, bg="#1e1e2e")
                row_frame.pack(fill=tk.X, padx=12, pady=2)
                for c in range(cols):
                    row_frame.columnconfigure(c, weight=1, uniform="col")

            card = self._make_element_card(row_frame, el, i)
            card.grid(row=0, column=col_in_row, sticky="nsew", padx=4, pady=4)

        # Spacer at bottom for drop zone
        drop_zone = tk.Label(
            self.canvas_inner,
            text="＋ Drop more elements here",
            fg="#585b70", bg="#232338",
            font=("Segoe UI", 10),
            pady=20
        )
        drop_zone.pack(fill=tk.X, padx=16, pady=(8, 16))
        drop_zone.bind("<ButtonRelease-1>", self._drag_end)

    def _make_element_card(self, parent, el, index):
        is_selected = (index == self.selected_index)
        bg = "#363655" if is_selected else "#2a2a3d"
        border_color = "#cba6f7" if is_selected else "#45475a"

        outer = tk.Frame(parent, bg=border_color, padx=1, pady=1)
        card = tk.Frame(outer, bg=bg)
        card.pack(fill=tk.BOTH, expand=True)

        # Top row: icon + type label + action buttons
        top = tk.Frame(card, bg=bg)
        top.pack(fill=tk.X, padx=10, pady=(8, 2))

        icon = ELEMENT_ICONS.get(el["type"], "•")
        type_name = next(d for d, t in ELEMENT_TYPES if t == el["type"])

        tk.Label(
            top, text=f"{icon} {type_name}", fg="#a6adc8", bg=bg,
            font=("Segoe UI", 8)
        ).pack(side=tk.LEFT)

        # Delete button
        del_btn = tk.Label(
            top, text="✕", fg="#f38ba8", bg=bg,
            font=("Segoe UI", 10, "bold"), cursor="hand2"
        )
        del_btn.pack(side=tk.RIGHT)
        del_btn.bind("<Button-1>", lambda e, idx=index: self._delete_element(idx))

        # Move up button
        if index > 0:
            up_btn = tk.Label(
                top, text="▲", fg="#a6adc8", bg=bg,
                font=("Segoe UI", 8), cursor="hand2"
            )
            up_btn.pack(side=tk.RIGHT, padx=4)
            up_btn.bind("<Button-1>", lambda e, idx=index: self._move_element(idx, -1))

        # Move down button
        if index < len(self.form_elements) - 1:
            down_btn = tk.Label(
                top, text="▼", fg="#a6adc8", bg=bg,
                font=("Segoe UI", 8), cursor="hand2"
            )
            down_btn.pack(side=tk.RIGHT, padx=2)
            down_btn.bind("<Button-1>", lambda e, idx=index: self._move_element(idx, 1))

        # Label text
        tk.Label(
            card, text=el["label"], fg="#cdd6f4", bg=bg,
            font=("Segoe UI", 11, "bold"), anchor="w"
        ).pack(fill=tk.X, padx=10, pady=(2, 1))

        # ID display
        tk.Label(
            card, text=f"id: {el['id']}", fg="#585b70", bg=bg,
            font=("Consolas", 8), anchor="w"
        ).pack(fill=tk.X, padx=10, pady=(0, 2))

        # Mini preview of the element
        self._render_mini_preview(card, el, bg)

        # Bottom padding
        tk.Frame(card, bg=bg, height=6).pack()

        # Click to select
        for w in card.winfo_children():
            w.bind("<Button-1>", lambda e, idx=index: self._select_element(idx))

        return outer

    def _render_mini_preview(self, parent, el, bg):
        etype = el["type"]
        preview = tk.Frame(parent, bg=bg)
        preview.pack(fill=tk.X, padx=10, pady=2)

        if etype == "text":
            e = tk.Entry(preview, bg="#3b3b5c", fg="#cdd6f4", relief=tk.FLAT,
                         insertbackground="#cdd6f4", font=("Segoe UI", 9))
            e.insert(0, "  Text input...")
            e.configure(state="disabled")
            e.pack(fill=tk.X)
        elif etype == "textarea":
            t = tk.Text(preview, bg="#3b3b5c", fg="#cdd6f4", relief=tk.FLAT,
                        height=2, font=("Segoe UI", 9), state="disabled")
            t.pack(fill=tk.X)
        elif etype == "checkbox":
            tk.Checkbutton(preview, text=el["label"], bg=bg, fg="#cdd6f4",
                           selectcolor="#3b3b5c", activebackground=bg,
                           font=("Segoe UI", 9)).pack(anchor="w")
        elif etype == "radio":
            tk.Radiobutton(preview, text="Option", bg=bg, fg="#cdd6f4",
                           selectcolor="#3b3b5c", activebackground=bg,
                           font=("Segoe UI", 9)).pack(anchor="w")
        elif etype == "select":
            cb = ttk.Combobox(preview, values=["Option 1", "Option 2"],
                              state="disabled", width=20)
            cb.set("Select...")
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

    # ── HTML Export ──────────────────────────────────────────────────────────

    def _export_html(self):
        if not self.form_elements:
            messagebox.showwarning("Empty Form", "Add some elements first!")
            return

        theme_name = self.selected_theme.get()
        theme = THEMES[theme_name]
        cols = self.columns

        filepath = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML Files", "*.html")],
            initialfile="form.html",
            title="Export Form as HTML"
        )

        if not filepath:
            return

        html = self._generate_html(theme, theme_name, cols)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)

        messagebox.showinfo("Exported!", f"Form saved to:\n{filepath}")

    def _generate_html(self, theme, theme_name, cols):
        # Build element HTML
        elements_html = ""
        for el in self.form_elements:
            elements_html += self._element_to_html(el)

        # Column grid CSS
        grid_css = ""
        if cols > 1:
            grid_css = f"""
    .form-grid {{
        display: grid;
        grid-template-columns: repeat({cols}, 1fr);
        gap: 1.25rem;
    }}
    .form-grid .form-group {{
        margin-bottom: 0;
    }}
    @media (max-width: 600px) {{
        .form-grid {{
            grid-template-columns: 1fr;
        }}
    }}"""

        # Determine button background style
        btn_bg = theme["button_bg"]
        if btn_bg.startswith("linear"):
            button_style = f"background: {btn_bg};"
        else:
            button_style = f"background-color: {btn_bg};"

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Form</title>
    <style>
    {theme['extra_css']}

    *, *::before, *::after {{
        box-sizing: border-box;
    }}

    body {{
        font-family: {theme['font_family']};
        background-color: {theme['bg']};
        color: {theme['text']};
        margin: 0;
        padding: 2rem;
        line-height: 1.6;
    }}

    .form-container {{
        max-width: 720px;
        margin: 0 auto;
        background: {theme['form_bg']};
        border: {theme['form_border']};
        border-radius: {theme['input_radius']};
        box-shadow: {theme['shadow']};
        padding: {theme['form_padding']};
    }}

    .form-group {{
        margin-bottom: 1.25rem;
    }}

    label {{
        display: block;
        margin-bottom: 0.35rem;
        font-weight: {theme['label_weight']};
        font-size: {theme['label_size']};
        color: {theme['text']};
    }}

    input[type="text"],
    input[type="date"],
    input[type="file"],
    textarea,
    select {{
        width: 100%;
        padding: 0.6rem 0.8rem;
        border: 1px solid {theme['input_border']};
        border-radius: {theme['input_radius']};
        background-color: {theme['input_bg']};
        color: {theme['text']};
        font-family: inherit;
        font-size: 0.95rem;
        transition: border-color 0.2s, box-shadow 0.2s;
        outline: none;
    }}

    textarea {{
        resize: vertical;
        min-height: 80px;
    }}

    input[type="checkbox"],
    input[type="radio"] {{
        margin-right: 0.5rem;
        accent-color: {theme['accent']};
    }}

    .checkbox-label,
    .radio-label {{
        display: inline-flex;
        align-items: center;
        font-weight: normal;
        cursor: pointer;
    }}

    button[type="submit"] {{
        {button_style}
        color: {theme['button_text']};
        border: none;
        border-radius: {theme['button_radius']};
        padding: 0.75rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: opacity 0.2s;
        font-family: inherit;
    }}

    button[type="submit"]:hover {{
        opacity: 0.9;
    }}
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
        return html

    def _element_to_html(self, el):
        etype = el["type"]
        label = el["label"]
        eid = el["id"]
        indent = "            "

        if etype == "text":
            return f"""{indent}<div class="form-group">
{indent}    <label for="{eid}">{label}</label>
{indent}    <input type="text" id="{eid}" name="{eid}" placeholder="Enter {label.lower()}">
{indent}</div>
"""
        elif etype == "textarea":
            return f"""{indent}<div class="form-group">
{indent}    <label for="{eid}">{label}</label>
{indent}    <textarea id="{eid}" name="{eid}" placeholder="Enter {label.lower()}"></textarea>
{indent}</div>
"""
        elif etype == "checkbox":
            return f"""{indent}<div class="form-group">
{indent}    <label class="checkbox-label">
{indent}        <input type="checkbox" id="{eid}" name="{eid}">
{indent}        {label}
{indent}    </label>
{indent}</div>
"""
        elif etype == "radio":
            return f"""{indent}<div class="form-group">
{indent}    <label class="radio-label">
{indent}        <input type="radio" id="{eid}" name="{eid}" value="{eid}">
{indent}        {label}
{indent}    </label>
{indent}</div>
"""
        elif etype == "select":
            return f"""{indent}<div class="form-group">
{indent}    <label for="{eid}">{label}</label>
{indent}    <select id="{eid}" name="{eid}">
{indent}        <option value="" disabled selected>Select {label.lower()}...</option>
{indent}        <option value="option1">Option 1</option>
{indent}        <option value="option2">Option 2</option>
{indent}        <option value="option3">Option 3</option>
{indent}    </select>
{indent}</div>
"""
        elif etype == "date":
            return f"""{indent}<div class="form-group">
{indent}    <label for="{eid}">{label}</label>
{indent}    <input type="date" id="{eid}" name="{eid}">
{indent}</div>
"""
        elif etype == "file":
            return f"""{indent}<div class="form-group">
{indent}    <label for="{eid}">{label}</label>
{indent}    <input type="file" id="{eid}" name="{eid}">
{indent}</div>
"""
        elif etype == "submit":
            return f"""{indent}<div class="form-group">
{indent}    <button type="submit">{label}</button>
{indent}</div>
"""
        return ""


# ─── Entry Point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = FormBuilder()
    app.mainloop()