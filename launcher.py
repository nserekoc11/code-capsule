import os
import sys
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QFrame,
    QListWidget, QLabel, QHBoxLayout, QDialog, QLineEdit,
    QFormLayout, QDialogButtonBox, QCheckBox, QTabWidget,
    QFileDialog, QMessageBox, QSpinBox, QComboBox, QScrollArea,
    QStackedWidget, QTextEdit, QSizePolicy
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QSettings


# ── Shared stylesheet ────────────────────────────────────────────────────────
APP_STYLE = """
    QWidget {
        background-color: #0f172a;
        color: white;
        font-family: 'Segoe UI';
        font-size: 12px;
    }
    QFrame {
        background-color: #111c2e;
        border-radius: 12px;
    }
    QPushButton {
        background-color: #1e293b;
        padding: 10px;
        border-radius: 8px;
        text-align: left;
        padding-left: 14px;
    }
    QPushButton:hover {
        background-color: #334155;
        border: 1px solid #0062FF;
    }
    QLineEdit, QComboBox, QSpinBox {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 6px;
        padding: 6px 10px;
        color: white;
    }
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
        border: 1px solid #0062FF;
    }
    QComboBox QAbstractItemView {
        background-color: #1e293b;
        selection-background-color: #1d4ed8;
    }
    QCheckBox { spacing: 8px; }
    QCheckBox::indicator {
        width: 16px; height: 16px;
        border-radius: 4px;
        border: 1px solid #334155;
        background: #1e293b;
    }
    QCheckBox::indicator:checked {
        background-color: #1d4ed8;
        border-color: #1d4ed8;
    }
    QTabWidget::pane {
        border: 1px solid #1e293b;
        border-radius: 8px;
        background-color: #111c2e;
    }
    QTabBar::tab {
        background-color: #1e293b;
        color: #94a3b8;
        padding: 8px 20px;
        border-radius: 6px;
        margin-right: 4px;
    }
    QTabBar::tab:selected { background-color: #1d4ed8; color: white; }
    QTabBar::tab:hover:!selected { background-color: #334155; color: white; }
    QListWidget {
        background-color: #1e293b;
        border-radius: 8px;
        border: none;
        padding: 4px;
    }
    QListWidget::item { padding: 6px 10px; border-radius: 6px; }
    QListWidget::item:selected { background-color: #1d4ed8; }
    QListWidget::item:hover:!selected { background-color: #334155; }
    QLabel { background: transparent; }
    QScrollArea { border: none; background: transparent; }
    QScrollBar:vertical {
        background: #1e293b; width: 6px; border-radius: 3px;
    }
    QScrollBar::handle:vertical { background: #334155; border-radius: 3px; }
    QDialogButtonBox QPushButton { padding: 8px 20px; text-align: center; }
    QTextEdit {
        background-color: #0a1120;
        border: 1px solid #1e293b;
        border-radius: 8px;
        color: #22c55e;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 12px;
        padding: 8px;
    }
"""

NAV_BTN_DEFAULT = """
    QPushButton {
        background: transparent;
        border: none;
        color: #94a3b8;
        text-align: left;
        padding: 9px 12px;
        border-radius: 8px;
        font-size: 13px;
    }
    QPushButton:hover {
        background-color: #1e293b;
        color: white;
        border: none;
    }
"""

NAV_BTN_ACTIVE = """
    QPushButton {
        background-color: #1d4ed8;
        border: none;
        color: white;
        text-align: left;
        padding: 9px 12px;
        border-radius: 8px;
        font-size: 13px;
    }
"""


# ══════════════════════════════════════════════════════════════════════════════
# SETTINGS WINDOW
# ══════════════════════════════════════════════════════════════════════════════

class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings — Code Capsule")
        self.setMinimumSize(640, 500)
        self.setStyleSheet(APP_STYLE)

        self.prefs = QSettings("CodeCapsule", "Preferences")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        title_bar = QWidget()
        title_bar.setStyleSheet("background-color: #0a1120; padding: 0;")
        tb = QHBoxLayout(title_bar)
        tb.setContentsMargins(20, 16, 20, 16)
        lbl = QLabel("Settings")
        lbl.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        tb.addWidget(lbl)
        root.addWidget(title_bar)

        tabs = QTabWidget()
        tabs.addTab(self._paths_tab(),    "Paths")
        tabs.addTab(self._editor_tab(),   "Editor")
        tabs.addTab(self._terminal_tab(), "Terminal")
        tabs.addTab(self._advanced_tab(), "Advanced")

        body = QWidget()
        body.setStyleSheet("background-color: #0f172a;")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(16, 16, 16, 8)
        bl.addWidget(tabs)
        root.addWidget(body)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        btns.setStyleSheet("background-color: #0a1120; padding: 12px 16px;")
        btns.accepted.connect(self._save)
        btns.rejected.connect(self.reject)
        root.addWidget(btns)

    def _paths_tab(self):
        tab, form = self._scrollable_form()
        self.git_edit      = self._path_row(form, "Git executable",
            self.prefs.value("paths/git",      "apps/git/cmd/git.exe"))
        self.vscode_edit   = self._path_row(form, "VS Code executable",
            self.prefs.value("paths/vscode",   "apps/vscode/Code.exe"))
        self.python_edit   = self._path_row(form, "Python executable",
            self.prefs.value("paths/python",   "apps/python/python.exe"))
        self.projects_edit = self._path_row(form, "Projects folder",
            self.prefs.value("paths/projects", "projects"), folder=True)
        return tab

    def _editor_tab(self):
        tab, form = self._scrollable_form()

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 32)
        self.font_size_spin.setValue(int(self.prefs.value("editor/font_size", 14)))
        form.addRow("Font size", self.font_size_spin)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark (default)", "Light", "High Contrast"])
        idx = self.theme_combo.findText(self.prefs.value("editor/theme", "Dark (default)"))
        self.theme_combo.setCurrentIndex(max(idx, 0))
        form.addRow("Theme", self.theme_combo)

        self.autosave_chk = self._checkbox(form, "Enable autosave",  "editor/autosave",  True)
        self.minimap_chk  = self._checkbox(form, "Show minimap",     "editor/minimap",   True)
        self.wordwrap_chk = self._checkbox(form, "Word wrap",        "editor/word_wrap", False)
        return tab

    def _terminal_tab(self):
        tab, form = self._scrollable_form()

        self.shell_combo = QComboBox()
        self.shell_combo.addItems(["Git Bash", "CMD", "PowerShell"])
        idx = self.shell_combo.findText(self.prefs.value("terminal/default_shell", "Git Bash"))
        self.shell_combo.setCurrentIndex(max(idx, 0))
        form.addRow("Default shell", self.shell_combo)

        self.open_in_proj_chk = self._checkbox(
            form, "Open terminal in project folder",
            "terminal/open_in_project", True)
        return tab

    def _advanced_tab(self):
        tab, form = self._scrollable_form()
        self.updates_chk = self._checkbox(form, "Check for updates on startup", "advanced/check_updates", False)
        self.debug_chk   = self._checkbox(form, "Enable debug logging",         "advanced/debug_logging",  False)

        reset_btn = QPushButton("Reset all settings to defaults")
        reset_btn.setStyleSheet(
            "background-color: #7f1d1d; color: white;"
            "text-align: center; padding: 8px 16px; border-radius: 8px;")
        reset_btn.clicked.connect(self._reset)
        form.addRow("", reset_btn)
        return tab

    def _scrollable_form(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        inner = QWidget()
        inner.setStyleSheet("background: transparent;")
        form = QFormLayout(inner)
        form.setContentsMargins(16, 16, 16, 16)
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        scroll.setWidget(inner)
        return scroll, form

    def _path_row(self, form, label, default, folder=False):
        row = QWidget()
        row.setStyleSheet("background: transparent;")
        rl = QHBoxLayout(row)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(8)

        edit = QLineEdit(default)
        browse = QPushButton("Browse")
        browse.setFixedWidth(72)
        browse.setStyleSheet(
            "background-color: #1e293b; padding: 6px 10px; text-align: center; border-radius: 6px;")

        def pick():
            p = (QFileDialog.getExistingDirectory(self, f"Choose {label}")
                 if folder else
                 QFileDialog.getOpenFileName(self, f"Locate {label}")[0])
            if p:
                edit.setText(p)

        browse.clicked.connect(pick)
        rl.addWidget(edit)
        rl.addWidget(browse)
        form.addRow(label, row)
        return edit

    def _checkbox(self, form, label, pref_key, default):
        chk = QCheckBox(label)
        chk.setChecked(self.prefs.value(pref_key, default, type=bool))
        form.addRow("", chk)
        return chk

    def _save(self):
        self.prefs.setValue("paths/git",      self.git_edit.text())
        self.prefs.setValue("paths/vscode",   self.vscode_edit.text())
        self.prefs.setValue("paths/python",   self.python_edit.text())
        self.prefs.setValue("paths/projects", self.projects_edit.text())
        self.prefs.setValue("editor/font_size", self.font_size_spin.value())
        self.prefs.setValue("editor/theme",     self.theme_combo.currentText())
        self.prefs.setValue("editor/autosave",  self.autosave_chk.isChecked())
        self.prefs.setValue("editor/minimap",   self.minimap_chk.isChecked())
        self.prefs.setValue("editor/word_wrap", self.wordwrap_chk.isChecked())
        self.prefs.setValue("terminal/default_shell",   self.shell_combo.currentText())
        self.prefs.setValue("terminal/open_in_project", self.open_in_proj_chk.isChecked())
        self.prefs.setValue("advanced/check_updates",   self.updates_chk.isChecked())
        self.prefs.setValue("advanced/debug_logging",   self.debug_chk.isChecked())
        self.prefs.sync()
        QMessageBox.information(self, "Saved", "Settings saved successfully.")
        self.accept()

    def _reset(self):
        if QMessageBox.question(
            self, "Reset", "Reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            self.prefs.clear()
            self.prefs.sync()
            QMessageBox.information(self, "Reset", "Settings reset. Restart to apply.")
            self.reject()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _page_header(title, subtitle=""):
    """Returns a QWidget containing a styled page header."""
    w = QWidget()
    w.setStyleSheet("background: transparent;")
    vl = QVBoxLayout(w)
    vl.setContentsMargins(0, 0, 0, 8)
    vl.setSpacing(2)

    h = QLabel(title)
    h.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
    vl.addWidget(h)

    if subtitle:
        s = QLabel(subtitle)
        s.setStyleSheet("color: #94a3b8; font-size: 14px;")
        vl.addWidget(s)

    return w


# ══════════════════════════════════════════════════════════════════════════════
# MAIN UI
# ══════════════════════════════════════════════════════════════════════════════

class CodeCapsuleUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Code Capsule")
        self.setMinimumSize(1000, 600)
        self.setStyleSheet(APP_STYLE)

        self.prefs = QSettings("CodeCapsule", "Preferences")
        self._nav_buttons = {}

        root = QHBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.setLayout(root)

        self.build_sidebar(root)
        self.build_main(root)

        # Show Dashboard by default
        self._set_active_nav("Dashboard")

    # ── Sidebar ──────────────────────────────────────────────────────────────

    def build_sidebar(self, parent_layout):
        sidebar = QFrame()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #0a1120;
                border-radius: 0px;
                border-right: 1px solid #1e293b;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 20, 12, 12)
        layout.setSpacing(4)

        title = QLabel("Code Capsule")
        title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        title.setStyleSheet("color: white; padding-left: 4px; background: transparent; margin-bottom: 10px;")
        layout.addWidget(title)

        nav_items = [
            ("Dashboard", "🏠"),
            ("Projects",  "📁"),
            ("Tools",     "🔧"),
            ("Terminal",  "🖥"),
        ]

        for name, icon in nav_items:
            btn = QPushButton(f"  {icon}  {name}")
            btn.setStyleSheet(NAV_BTN_DEFAULT)
            btn.clicked.connect(lambda _, n=name: self._set_active_nav(n))
            layout.addWidget(btn)
            self._nav_buttons[name] = btn

        layout.addStretch()

        settings_btn = QPushButton("  ⚙  Settings")
        settings_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #1e293b;
                color: #94a3b8;
                text-align: left;
                padding: 9px 12px;
                border-radius: 8px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1e293b;
                color: white;
                border: 1px solid #334155;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
                color: white;
                border: 1px solid #1d4ed8;
            }
        """)
        settings_btn.clicked.connect(self.open_settings)
        layout.addWidget(settings_btn)

        sidebar.setLayout(layout)
        parent_layout.addWidget(sidebar)

    def _set_active_nav(self, active_name):
        for name, btn in self._nav_buttons.items():
            btn.setStyleSheet(NAV_BTN_ACTIVE if name == active_name else NAV_BTN_DEFAULT)

        page_index = {"Dashboard": 0, "Projects": 1, "Tools": 2, "Terminal": 3}
        self.stack.setCurrentIndex(page_index[active_name])

    # ── Main area with stacked pages ─────────────────────────────────────────

    def build_main(self, parent_layout):
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background-color: #0f172a;")

        self.stack.addWidget(self._build_dashboard_page())   # index 0
        self.stack.addWidget(self._build_projects_page())    # index 1
        self.stack.addWidget(self._build_tools_page())       # index 2
        self.stack.addWidget(self._build_terminal_page())    # index 3

        parent_layout.addWidget(self.stack)

    # ── Page builders ─────────────────────────────────────────────────────────

    def _scrollable_page(self):
        """Returns (scroll_widget, inner_layout) — add widgets to inner_layout."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: #0f172a; border: none;")

        inner = QWidget()
        inner.setStyleSheet("background-color: #0f172a;")
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(20)

        scroll.setWidget(inner)
        return scroll, layout

    # ── Dashboard ─────────────────────────────────────────────────────────────

    def _build_dashboard_page(self):
        page, ml = self._scrollable_page()

        ml.addWidget(_page_header("Welcome to Code Capsule", "Portable developer environment"))

        self._add_status_cards(ml)
        self._add_quick_launch(ml)
        self._add_recent_projects_mini(ml)

        ml.addStretch()
        return page

    def _add_status_cards(self, layout):
        row = QHBoxLayout()
        row.setSpacing(12)
        for name, installed in self._detect_tools().items():
            card = QFrame()
            card.setFixedHeight(90)
            card.setStyleSheet("""
                QFrame {
                    background-color: #111c2e;
                    border-radius: 12px;
                    border: 1px solid #1e293b;
                }
            """)
            cl = QVBoxLayout()
            cl.setContentsMargins(16, 12, 16, 12)

            t = QLabel(name)
            t.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            t.setStyleSheet("background: transparent; border: none;")

            s = QLabel("● Ready" if installed else "● Missing")
            s.setStyleSheet(
                f"color: {'#22c55e' if installed else '#ef4444'}; background: transparent; border: none;")

            cl.addWidget(t)
            cl.addWidget(s)
            card.setLayout(cl)
            row.addWidget(card)
        layout.addLayout(row)

    def _add_quick_launch(self, layout):
        lbl = QLabel("Quick Launch")
        lbl.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(lbl)

        row = QHBoxLayout()
        row.setSpacing(10)
        btn_style = """
            QPushButton {
                background-color: #1e293b;
                padding: 10px 14px;
                border-radius: 8px;
                font-size: 12px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #334155;
                border: 1px solid #0062FF;
            }
        """
        for label, handler in [
            ("💻  VS Code",    self.open_vscode_cc),
            ("🐙  Git Bash",   self.open_git_bash),
            ("🖥  CMD",        self.open_cmd),
            ("⚡  PowerShell", self.open_powershell),
        ]:
            btn = QPushButton(label)
            btn.setStyleSheet(btn_style)
            btn.clicked.connect(handler)
            row.addWidget(btn)
        layout.addLayout(row)

    def _add_recent_projects_mini(self, layout):
        """A compact recent-projects list on the dashboard."""
        lbl = QLabel("Recent Projects")
        lbl.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(lbl)

        lst = QListWidget()
        lst.setFixedHeight(160)
        lst.addItems(self._get_projects())
        lst.itemDoubleClicked.connect(self._open_selected_project)
        layout.addWidget(lst)

        hint = QLabel("Double-click a project to open it in VS Code")
        hint.setStyleSheet("color: #64748b; font-size: 11px;")
        layout.addWidget(hint)

    # ── Projects page ─────────────────────────────────────────────────────────

    def _build_projects_page(self):
        page, ml = self._scrollable_page()

        ml.addWidget(_page_header("Projects", "Manage your local projects"))

        # Toolbar
        hr = QHBoxLayout()
        hr.setSpacing(8)

        new_btn = QPushButton("+ New Project")
        new_btn.setFixedWidth(110)
        new_btn.setStyleSheet("""
            QPushButton {
                background-color: #1d4ed8; padding: 7px 10px;
                border-radius: 6px; font-size: 12px; text-align: center; color: white;
            }
            QPushButton:hover { background-color: #2563eb; }
        """)
        new_btn.clicked.connect(self._open_new_project_dialog)

        refresh_btn = QPushButton("↻  Refresh")
        refresh_btn.setFixedWidth(90)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #1e293b; padding: 7px 10px;
                border-radius: 6px; font-size: 12px; text-align: center;
            }
            QPushButton:hover { background-color: #334155; }
        """)

        open_folder_btn = QPushButton("📂  Open Folder")
        open_folder_btn.setFixedWidth(110)
        open_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #1e293b; padding: 7px 10px;
                border-radius: 6px; font-size: 12px; text-align: center;
            }
            QPushButton:hover { background-color: #334155; }
        """)
        open_folder_btn.clicked.connect(self._open_projects_folder)

        hr.addWidget(new_btn)
        hr.addWidget(refresh_btn)
        hr.addWidget(open_folder_btn)
        hr.addStretch()
        ml.addLayout(hr)

        # Project list
        self.project_list = QListWidget()
        self.project_list.addItems(self._get_projects())
        self.project_list.itemDoubleClicked.connect(self._open_selected_project)
        ml.addWidget(self.project_list)

        refresh_btn.clicked.connect(lambda: (
            self.project_list.clear(),
            self.project_list.addItems(self._get_projects())
        ))

        hint = QLabel("Double-click a project to open it in VS Code")
        hint.setStyleSheet("color: #64748b; font-size: 11px;")
        ml.addWidget(hint)

        ml.addStretch()
        return page

    def _open_projects_folder(self):
        script_dir   = os.path.dirname(os.path.abspath(__file__))
        projects_dir = self.prefs.value("paths/projects", os.path.join(script_dir, "projects"))
        os.makedirs(projects_dir, exist_ok=True)
        try:
            subprocess.Popen(["explorer", projects_dir])
        except Exception as e:
            print(f"Explorer error: {e}")

    # ── Tools page ────────────────────────────────────────────────────────────

    def _build_tools_page(self):
        page, ml = self._scrollable_page()

        ml.addWidget(_page_header("Tools", "Installed developer tools"))

        tools = [
            ("Git",     "paths/git",    "apps/git/cmd/git.exe",
             "Version control system",     "🐙"),
            ("VS Code", "paths/vscode", "apps/vscode/Code.exe",
             "Source code editor",         "💻"),
            ("Python",  "paths/python", "apps/python/python.exe",
             "Python runtime interpreter", "🐍"),
        ]

        for name, pref_key, fallback, desc, icon in tools:
            installed = self._check_tool(pref_key, fallback)
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: #111c2e;
                    border-radius: 12px;
                    border: 1px solid #1e293b;
                }
            """)
            cl = QHBoxLayout()
            cl.setContentsMargins(18, 14, 18, 14)
            cl.setSpacing(14)

            icon_lbl = QLabel(icon)
            icon_lbl.setFont(QFont("Segoe UI", 22))
            icon_lbl.setFixedWidth(36)
            icon_lbl.setStyleSheet("background: transparent; border: none;")

            info = QVBoxLayout()
            info.setSpacing(2)
            name_lbl = QLabel(name)
            name_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            name_lbl.setStyleSheet("background: transparent; border: none;")
            desc_lbl = QLabel(desc)
            desc_lbl.setStyleSheet("color: #64748b; background: transparent; border: none;")

            path_lbl = QLabel(self._resolve(pref_key, fallback))
            path_lbl.setStyleSheet("color: #475569; font-size: 10px; background: transparent; border: none;")

            info.addWidget(name_lbl)
            info.addWidget(desc_lbl)
            info.addWidget(path_lbl)

            status = QLabel("● Installed" if installed else "● Not found")
            status.setStyleSheet(
                f"color: {'#22c55e' if installed else '#ef4444'};"
                "background: transparent; border: none; font-size: 12px;")
            status.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            cl.addWidget(icon_lbl)
            cl.addLayout(info)
            cl.addStretch()
            cl.addWidget(status)
            card.setLayout(cl)
            ml.addWidget(card)

        # Quick-launch section
        ml.addSpacing(10)
        launch_lbl = QLabel("Launch")
        launch_lbl.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        ml.addWidget(launch_lbl)

        row = QHBoxLayout()
        row.setSpacing(10)
        btn_style = """
            QPushButton {
                background-color: #1e293b;
                padding: 10px 14px;
                border-radius: 8px;
                font-size: 12px;
                text-align: center;
            }
            QPushButton:hover { background-color: #334155; border: 1px solid #0062FF; }
        """
        for label, handler in [
            ("💻  VS Code",    self.open_vscode_cc),
            ("🐙  Git Bash",   self.open_git_bash),
            ("🖥  CMD",        self.open_cmd),
            ("⚡  PowerShell", self.open_powershell),
        ]:
            btn = QPushButton(label)
            btn.setStyleSheet(btn_style)
            btn.clicked.connect(handler)
            row.addWidget(btn)
        ml.addLayout(row)

        ml.addStretch()
        return page

    # ── Terminal page ─────────────────────────────────────────────────────────

    def _build_terminal_page(self):
        page, ml = self._scrollable_page()

        ml.addWidget(_page_header("Terminal", "Run commands in your project environment"))

        # Shell selector
        shell_row = QHBoxLayout()
        shell_row.setSpacing(8)

        shell_lbl = QLabel("Shell:")
        shell_lbl.setStyleSheet("color: #94a3b8;")
        shell_lbl.setFixedWidth(36)

        self.shell_selector = QComboBox()
        self.shell_selector.addItems(["Git Bash", "CMD", "PowerShell"])
        self.shell_selector.setFixedWidth(140)

        launch_btn = QPushButton("Launch External Terminal")
        launch_btn.setStyleSheet("""
            QPushButton {
                background-color: #1d4ed8; padding: 7px 14px;
                border-radius: 6px; font-size: 12px; text-align: center; color: white;
            }
            QPushButton:hover { background-color: #2563eb; }
        """)
        launch_btn.clicked.connect(self._launch_selected_shell)

        clear_btn = QPushButton("Clear Output")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #1e293b; padding: 7px 14px;
                border-radius: 6px; font-size: 12px; text-align: center;
            }
            QPushButton:hover { background-color: #334155; }
        """)
        clear_btn.clicked.connect(lambda: self.terminal_output.clear())

        shell_row.addWidget(shell_lbl)
        shell_row.addWidget(self.shell_selector)
        shell_row.addWidget(launch_btn)
        shell_row.addWidget(clear_btn)
        shell_row.addStretch()
        ml.addLayout(shell_row)

        # Output area
        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setMinimumHeight(200)
        self.terminal_output.setPlaceholderText("Command output appears here...")
        ml.addWidget(self.terminal_output)

        # Command input
        cmd_row = QHBoxLayout()
        cmd_row.setSpacing(8)

        prompt_lbl = QLabel("$")
        prompt_lbl.setStyleSheet("color: #22c55e; font-family: Consolas; font-size: 14px; background: transparent;")
        prompt_lbl.setFixedWidth(14)

        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText("Enter a command and press Run or hit Enter…")
        self.cmd_input.returnPressed.connect(self._run_command)

        run_btn = QPushButton("Run")
        run_btn.setFixedWidth(60)
        run_btn.setStyleSheet("""
            QPushButton {
                background-color: #1d4ed8; padding: 7px 10px;
                border-radius: 6px; font-size: 12px; text-align: center; color: white;
            }
            QPushButton:hover { background-color: #2563eb; }
        """)
        run_btn.clicked.connect(self._run_command)

        cmd_row.addWidget(prompt_lbl)
        cmd_row.addWidget(self.cmd_input)
        cmd_row.addWidget(run_btn)
        ml.addLayout(cmd_row)

        # Quick command shortcuts
        ml.addSpacing(4)
        quick_lbl = QLabel("Quick commands")
        quick_lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        ml.addWidget(quick_lbl)

        quick_row = QHBoxLayout()
        quick_row.setSpacing(8)
        quick_style = """
            QPushButton {
                background-color: #1e293b; padding: 7px 12px;
                border-radius: 6px; font-size: 11px; text-align: center;
            }
            QPushButton:hover { background-color: #334155; }
        """
        for label, cmd in [
            ("git status",  "git status"),
            ("git log",     "git log --oneline -10"),
            ("python -V",   "python --version"),
            ("ls / dir",    "dir" if sys.platform == "win32" else "ls -la"),
            ("pwd",         "cd" if sys.platform == "win32" else "pwd"),
        ]:
            b = QPushButton(label)
            b.setStyleSheet(quick_style)
            b.clicked.connect(lambda _, c=cmd: self._run_quick(c))
            quick_row.addWidget(b)

        ml.addLayout(quick_row)
        ml.addStretch()
        return page

    def _run_command(self):
        cmd = self.cmd_input.text().strip()
        if not cmd:
            return
        self.cmd_input.clear()
        self._execute_and_display(cmd)

    def _run_quick(self, cmd):
        self.cmd_input.setText(cmd)
        self._execute_and_display(cmd)

    def _execute_and_display(self, cmd):
        script_dir   = os.path.dirname(os.path.abspath(__file__))
        projects_dir = self.prefs.value("paths/projects", os.path.join(script_dir, "projects"))
        os.makedirs(projects_dir, exist_ok=True)

        self.terminal_output.append(f"<span style='color:#60a5fa;'>$ {cmd}</span>")
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True,
                cwd=projects_dir, timeout=15
            )
            if result.stdout:
                self.terminal_output.append(
                    f"<span style='color:#e2e8f0;'>{result.stdout.strip()}</span>")
            if result.stderr:
                self.terminal_output.append(
                    f"<span style='color:#f87171;'>{result.stderr.strip()}</span>")
        except subprocess.TimeoutExpired:
            self.terminal_output.append(
                "<span style='color:#fbbf24;'>Command timed out after 15s.</span>")
        except Exception as e:
            self.terminal_output.append(
                f"<span style='color:#f87171;'>Error: {e}</span>")

        self.terminal_output.append("")  # blank line separator

    def _launch_selected_shell(self):
        shell = self.shell_selector.currentText()
        if shell == "Git Bash":
            self.open_git_bash()
        elif shell == "CMD":
            self.open_cmd()
        else:
            self.open_powershell()

    # ── Shared helpers ────────────────────────────────────────────────────────

    def open_settings(self):
        SettingsWindow(self).exec()

    def _resolve(self, pref_key, fallback_relative):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        saved = self.prefs.value(pref_key, "")
        if saved and os.path.exists(saved):
            return saved
        return os.path.join(script_dir, fallback_relative)

    def _check_tool(self, pref_key, fallback):
        return os.path.exists(self._resolve(pref_key, fallback))

    def _detect_tools(self):
        return {
            "Git":     self._check_tool("paths/git",    "apps/git/cmd/git.exe"),
            "VS Code": self._check_tool("paths/vscode", "apps/vscode/Code.exe"),
            "Python":  self._check_tool("paths/python", "apps/python/python.exe"),
        }

    def _get_projects(self):
        script_dir   = os.path.dirname(os.path.abspath(__file__))
        projects_dir = self.prefs.value("paths/projects", os.path.join(script_dir, "projects"))
        os.makedirs(projects_dir, exist_ok=True)
        return [f for f in os.listdir(projects_dir)
                if os.path.isdir(os.path.join(projects_dir, f))]

    def _setup_environment(self):
        git_dir = os.path.dirname(self._resolve("paths/git", "apps/git/cmd/git.exe"))
        os.environ['PATH'] = git_dir + os.pathsep + os.environ.get('PATH', '')

    def open_vscode_cc(self):
        script_dir   = os.path.dirname(os.path.abspath(__file__))
        projects_dir = self.prefs.value("paths/projects", os.path.join(script_dir, "projects"))
        try:
            subprocess.Popen([self._resolve("paths/vscode", "apps/vscode/Code.exe"), projects_dir])
        except Exception as e:
            print(f"VS Code error: {e}")

    def open_git_bash(self):
        script_dir   = os.path.dirname(os.path.abspath(__file__))
        projects_dir = self.prefs.value("paths/projects", os.path.join(script_dir, "projects"))
        bash = os.path.join(script_dir, "apps", "git", "git-bash.exe")
        try:
            subprocess.Popen([bash], cwd=projects_dir)
        except Exception as e:
            print(f"Git Bash error: {e}")

    def open_cmd(self):
        script_dir   = os.path.dirname(os.path.abspath(__file__))
        projects_dir = self.prefs.value("paths/projects", os.path.join(script_dir, "projects"))
        os.makedirs(projects_dir, exist_ok=True)
        try:
            subprocess.Popen(["cmd.exe"], cwd=projects_dir,
                             creationflags=subprocess.CREATE_NEW_CONSOLE)
        except Exception as e:
            QMessageBox.critical(self, "Terminal error", f"CMD error: {e}")

    def open_powershell(self):
        script_dir   = os.path.dirname(os.path.abspath(__file__))
        projects_dir = self.prefs.value("paths/projects", os.path.join(script_dir, "projects"))
        os.makedirs(projects_dir, exist_ok=True)
        try:
            subprocess.Popen(["powershell.exe"], cwd=projects_dir,
                             creationflags=subprocess.CREATE_NEW_CONSOLE)
        except Exception:
            try:
                subprocess.Popen(["pwsh.exe"], cwd=projects_dir,
                                 creationflags=subprocess.CREATE_NEW_CONSOLE)
            except Exception as e:
                QMessageBox.critical(self, "Terminal error", f"PowerShell error: {e}")

    def _open_selected_project(self, item):
        script_dir   = os.path.dirname(os.path.abspath(__file__))
        projects_dir = self.prefs.value("paths/projects", os.path.join(script_dir, "projects"))
        try:
            subprocess.Popen([
                self._resolve("paths/vscode", "apps/vscode/Code.exe"),
                os.path.join(projects_dir, item.text())
            ])
        except Exception as e:
            print(f"Open project error: {e}")

    def _open_new_project_dialog(self):
        dialog = NewProjectDialog(self)
        if dialog.exec():
            self._create_project(dialog.name_input.text(), dialog.type_combo.currentText())

    def _create_project(self, name, project_type):
        if not name.strip():
            QMessageBox.warning(self, "Invalid Name", "Project name cannot be empty.")
            return

        script_dir   = os.path.dirname(os.path.abspath(__file__))
        projects_dir = self.prefs.value("paths/projects", os.path.join(script_dir, "projects"))
        project_path = os.path.join(projects_dir, name)

        if os.path.exists(project_path):
            QMessageBox.warning(self, "Project Exists", "A project with this name already exists.")
            return

        os.makedirs(project_path)

        with open(os.path.join(project_path, "README.md"), "w", encoding="utf-8") as f:
            f.write(f"# {name}\n")

        if project_type == "Python":
            with open(os.path.join(project_path, "main.py"), "w", encoding="utf-8") as f:
                f.write(
                    "def main():\n"
                    "    print('Hello from Code Capsule')\n\n"
                    "if __name__ == '__main__':\n"
                    "    main()\n"
                )
        elif project_type == "Flask":
            with open(os.path.join(project_path, "app.py"), "w", encoding="utf-8") as f:
                f.write(
                    "from flask import Flask\n\n"
                    "app = Flask(__name__)\n\n"
                    "@app.route('/')\n"
                    "def home():\n"
                    "    return 'Hello Flask'\n\n"
                    "if __name__ == '__main__':\n"
                    "    app.run(debug=True)\n"
                )
            os.makedirs(os.path.join(project_path, "templates"), exist_ok=True)
            os.makedirs(os.path.join(project_path, "static"),    exist_ok=True)

        try:
            self._setup_environment()
            subprocess.run(["git", "init"], cwd=project_path, capture_output=True, text=True)
        except Exception as e:
            print("Git init error:", e)

        self.project_list.clear()
        self.project_list.addItems(self._get_projects())

        try:
            subprocess.Popen([self._resolve("paths/vscode", "apps/vscode/Code.exe"), project_path])
        except Exception as e:
            print("VS Code launch error:", e)

        QMessageBox.information(self, "Project Created", f"{name} created successfully.")


# ══════════════════════════════════════════════════════════════════════════════
# NEW PROJECT DIALOG
# ══════════════════════════════════════════════════════════════════════════════

class NewProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Project")
        self.setMinimumWidth(320)
        self.setStyleSheet(APP_STYLE)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Create New Project")
        title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        layout.addWidget(title)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Project name…")
        layout.addWidget(self.name_input)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["Python", "Flask", "Empty Project"])
        layout.addWidget(self.type_combo)

        create_btn = QPushButton("Create Project")
        create_btn.setStyleSheet("""
            QPushButton {
                background-color: #1d4ed8; padding: 9px;
                border-radius: 7px; text-align: center; color: white; font-size: 13px;
            }
            QPushButton:hover { background-color: #2563eb; }
        """)
        create_btn.clicked.connect(self.accept)
        layout.addWidget(create_btn)

        self.setLayout(layout)


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CodeCapsuleUI()
    window.show()
    sys.exit(app.exec())