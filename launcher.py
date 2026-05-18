import os
import sys
import subprocess
from tkinter import dialog
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QFrame,
    QListWidget, QLabel, QHBoxLayout, QDialog, QLineEdit,
    QFormLayout, QDialogButtonBox, QCheckBox, QTabWidget,
    QFileDialog, QMessageBox, QSpinBox, QComboBox, QScrollArea
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

        # ── Title bar
        title_bar = QWidget()
        title_bar.setStyleSheet("background-color: #0a1120; padding: 0;")
        tb = QHBoxLayout(title_bar)
        tb.setContentsMargins(20, 16, 20, 16)
        lbl = QLabel("Settings")
        lbl.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        tb.addWidget(lbl)
        root.addWidget(title_bar)

        # ── Tabs
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

    # ── Tab builders ──────────────────────────────────────────────────────────
    def _paths_tab(self):
        tab, form = self._scrollable_form()
        self.git_edit     = self._path_row(form, "Git executable",
            self.prefs.value("paths/git",      "apps/git/cmd/git.exe"))
        self.vscode_edit  = self._path_row(form, "VS Code executable",
            self.prefs.value("paths/vscode",   "apps/vscode/Code.exe"))
        self.python_edit  = self._path_row(form, "Python executable",
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

        self.autosave_chk  = self._checkbox(form, "Enable autosave",  "editor/autosave",  True)
        self.minimap_chk   = self._checkbox(form, "Show minimap",     "editor/minimap",   True)
        self.wordwrap_chk  = self._checkbox(form, "Word wrap",        "editor/word_wrap", False)
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
        self.updates_chk = self._checkbox(form, "Check for updates on startup",
                                           "advanced/check_updates", False)
        self.debug_chk   = self._checkbox(form, "Enable debug logging",
                                           "advanced/debug_logging",  False)

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
# LAUNCHER  (kept for compatibility)
# ══════════════════════════════════════════════════════════════════════════════

class Launcher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Code Capsule")
        layout = QVBoxLayout()
        git_btn = QPushButton("Test Git")
        git_btn.clicked.connect(self.open_git)
        vscode_btn = QPushButton("Open VS Code")
        vscode_btn.clicked.connect(self.open_vscode)
        layout.addWidget(git_btn)
        layout.addWidget(vscode_btn)
        self.setLayout(layout)

    def open_vscode(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        subprocess.Popen([os.path.join(script_dir, "apps", "vscode", "Code.exe")])

    def setup_environment(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        git_path = os.path.join(script_dir, "apps", "git", "cmd")
        os.environ['PATH'] = git_path + os.pathsep + os.environ['PATH']

    def open_git(self):
        self.setup_environment()
        try:
            result = subprocess.run(["git", "--version"], capture_output=True, text=True)
            print("Git:", result.stdout.strip())
        except Exception as e:
            print(f"Git error: {e}")


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

        for name in ["Dashboard", "Projects", "Tools", "Terminal"]:
            btn = QPushButton(f"  {name}")
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

    def build_main(self, parent_layout):
        main = QWidget()
        main.setStyleSheet("background-color: #0f172a;")
        ml = QVBoxLayout()
        ml.setSpacing(20)
        ml.setContentsMargins(28, 24, 28, 24)

        header = QLabel("Welcome to Code Capsule")
        header.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        subtitle = QLabel("Portable developer environment")
        subtitle.setStyleSheet("color: #94a3b8; font-size: 14px;")

        ml.addWidget(header)
        ml.addWidget(subtitle)

        self.add_status_cards(ml)
        self.add_quick_launch(ml)
        self.add_recent_projects(ml)

        main.setLayout(ml)
        parent_layout.addWidget(main)

    def add_status_cards(self, layout):
        row = QHBoxLayout()
        row.setSpacing(12)
        for name, installed in self.detect_tools().items():
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

    def add_quick_launch(self, layout):
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

    def add_recent_projects(self, layout):
        hr = QHBoxLayout()
        lbl = QLabel("Projects")
        lbl.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        hr.addWidget(lbl)
        hr.addStretch()

        new_btn = QPushButton("+ New Project")
        new_btn.setFixedWidth(90)
        new_btn.setStyleSheet("""
            QPushButton {
                background-color: #1e293b; padding: 6px 10px;
                border-radius: 6px; font-size: 11px; text-align: center;
            }
            QPushButton:hover { background-color: #334155; }
        """)
        new_btn.clicked.connect(self.open_new_project_dialog)

        refresh = QPushButton("↻  Refresh")
        refresh.setFixedWidth(90)
        refresh.setStyleSheet("""
            QPushButton {
                background-color: #1e293b; padding: 6px 10px;
                border-radius: 6px; font-size: 11px; text-align: center;
            }
            QPushButton:hover { background-color: #334155; }
        """)
        refresh.clicked.connect(lambda: (
            self.project_list.clear(),
            self.project_list.addItems(self.get_projects())
        ))
        hr.addWidget(new_btn)
        hr.addWidget(refresh)
        layout.addLayout(hr)

        self.project_list = QListWidget()
        self.project_list.addItems(self.get_projects())
        self.project_list.itemDoubleClicked.connect(self.open_selected_project)
        layout.addWidget(self.project_list)

    def open_new_project_dialog(self):
        dialog = NewProjectDialog(self)

        if dialog.exec():
            self.create_project(
                dialog.name_input.text(),
                dialog.type_combo.currentText()
            )

    def create_project(self, name, project_type):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        projects_dir = self.prefs.value(
            "paths/projects",
            os.path.join(script_dir, "projects")
        )
        project_path = os.path.join(projects_dir, name)
        os.makedirs(project_path, exist_ok=True)

        # Refresh the project list after creating a new project
        self.project_list.clear()
        self.project_list.addItems(self.get_projects())

    def open_settings(self):
        SettingsWindow(self).exec()

    def _resolve(self, pref_key, fallback_relative):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        saved = self.prefs.value(pref_key, "")
        if saved and os.path.exists(saved):
            return saved
        return os.path.join(script_dir, fallback_relative)

    def check_tool(self, pref_key, fallback):
        return os.path.exists(self._resolve(pref_key, fallback))

    def detect_tools(self):
        return {
            "Git":     self.check_tool("paths/git",    "apps/git/cmd/git.exe"),
            "VS Code": self.check_tool("paths/vscode", "apps/vscode/Code.exe"),
            "Python":  self.check_tool("paths/python", "apps/python/python.exe"),
        }

    def get_projects(self):
        script_dir   = os.path.dirname(os.path.abspath(__file__))
        projects_dir = self.prefs.value("paths/projects",
                                         os.path.join(script_dir, "projects"))
        os.makedirs(projects_dir, exist_ok=True)
        return [f for f in os.listdir(projects_dir)
                if os.path.isdir(os.path.join(projects_dir, f))]

    def setup_environment_cc(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        git_dir = os.path.dirname(self._resolve("paths/git", "apps/git/cmd/git.exe"))
        os.environ['PATH'] = git_dir + os.pathsep + os.environ.get('PATH', '')

    def open_vscode_cc(self):
        script_dir   = os.path.dirname(os.path.abspath(__file__))
        projects_dir = self.prefs.value("paths/projects",
                                         os.path.join(script_dir, "projects"))
        try:
            subprocess.Popen([self._resolve("paths/vscode", "apps/vscode/Code.exe"),
                              projects_dir])
        except Exception as e:
            print(f"VS Code error: {e}")

    def open_git_bash(self):
        script_dir   = os.path.dirname(os.path.abspath(__file__))
        projects_dir = self.prefs.value("paths/projects",
                                         os.path.join(script_dir, "projects"))
        bash = os.path.join(script_dir, "apps", "git", "git-bash.exe")
        try:
            subprocess.Popen([bash], cwd=projects_dir)
        except Exception as e:
            print(f"Git Bash error: {e}")

    def open_cmd(self):
        script_dir   = os.path.dirname(os.path.abspath(__file__))
        projects_dir = self.prefs.value("paths/projects",
                                         os.path.join(script_dir, "projects"))
        os.makedirs(projects_dir, exist_ok=True)

        try:
            subprocess.Popen(
                ["cmd.exe"],
                cwd=projects_dir,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        except Exception as e:
            QMessageBox.critical(self, "Terminal error", f"CMD error: {e}")

    def open_powershell(self):
        script_dir   = os.path.dirname(os.path.abspath(__file__))
        projects_dir = self.prefs.value("paths/projects",
                                         os.path.join(script_dir, "projects"))
        os.makedirs(projects_dir, exist_ok=True)

        try:
            subprocess.Popen(
                ["powershell.exe"],
                cwd=projects_dir,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        except Exception:
            try:
                subprocess.Popen(
                    ["pwsh.exe"],
                    cwd=projects_dir,
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            except Exception as e:
                QMessageBox.critical(self, "Terminal error", f"PowerShell error: {e}")

    def open_selected_project(self, item):
        script_dir   = os.path.dirname(os.path.abspath(__file__))
        projects_dir = self.prefs.value("paths/projects", 
                                        os.path.join(script_dir, "projects"))
        try:
            subprocess.Popen([
                self._resolve("paths/vscode", "apps/vscode/Code.exe"),
                os.path.join(projects_dir, item.text())
            ])
        except Exception as e:
            print(f"Open project error: {e}")


#Create Project Dialog
class NewProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("New Project")

        layout = QVBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Project Name")

        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "Python",
            "Flask",
            "Empty Project"
        ])

        create_btn = QPushButton("Create")

        create_btn.clicked.connect(self.accept)

        layout.addWidget(self.name_input)
        layout.addWidget(self.type_combo)
        layout.addWidget(create_btn)

        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CodeCapsuleUI()
    window.show()
    sys.exit(app.exec())
