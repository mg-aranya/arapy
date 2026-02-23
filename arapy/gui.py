# arapy/gui.py
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
except ImportError as e:
    raise RuntimeError(
        "Tkinter is not available.\n"
        "On Debian/Ubuntu: sudo apt install python3-tk\n"
        "On Fedora: sudo dnf install python3-tkinter\n"
        "On macOS (Homebrew Python): brew install python-tk"
    ) from e

import shlex
import json
import io
import contextlib
from . import commands, config
from .api_endpoints import API_ENDPOINTS as APIPath
from .clearpass import ClearPassClient



class ArapyGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("arapy - ClearPass API GUI")
        self.geometry("900x600")

        self.dispatch = commands.DISPATCH

        # Client
        self.cp = ClearPassClient(
            config.SERVER,
            https_prefix=config.HTTPS,
            verify_ssl=config.VERIFY_SSL,
            timeout=config.DEFAULT_TIMEOUT,
        )
        try:
            self.token = self.cp.login(APIPath, config.CREDENTIALS)["access_token"]
        except Exception as e:
            messagebox.showerror("Login failed", str(e))
            self.destroy()
            return

        self._build_ui()

    def _build_ui(self):
        frm = ttk.Frame(self, padding=10)
        frm.pack(fill="both", expand=True)

        # Module/Service/Action dropdowns
        self.module_var = tk.StringVar()
        self.service_var = tk.StringVar()
        self.action_var = tk.StringVar()

        ttk.Label(frm, text="Module").grid(row=0, column=0, sticky="w")
        self.module_cb = ttk.Combobox(frm, textvariable=self.module_var, state="readonly")
        self.module_cb["values"] = sorted(self.dispatch.keys())
        self.module_cb.grid(row=0, column=1, sticky="ew")
        self.module_cb.bind("<<ComboboxSelected>>", self._on_module)

        ttk.Label(frm, text="Service").grid(row=1, column=0, sticky="w")
        self.service_cb = ttk.Combobox(frm, textvariable=self.service_var, state="readonly")
        self.service_cb.grid(row=1, column=1, sticky="ew")
        self.service_cb.bind("<<ComboboxSelected>>", self._on_service)

        ttk.Label(frm, text="Action").grid(row=2, column=0, sticky="w")
        self.action_cb = ttk.Combobox(frm, textvariable=self.action_var, state="readonly")
        self.action_cb.grid(row=2, column=1, sticky="ew")

        # Args entry + Browse button for --file=
        ttk.Label(frm, text="Args (space separated, e.g. --limit=5 --out=foo.csv)").grid(row=3, column=0, sticky="w")

        args_row = ttk.Frame(frm)
        args_row.grid(row=3, column=1, sticky="ew")

        self.args_entry = ttk.Entry(args_row)
        self.args_entry.pack(side="left", fill="x", expand=True)
        self.args_entry.insert(0, "limit=5 out=./logs/out.json")

        browse_btn = ttk.Button(args_row, text="Browse…", command=self._pick_file)
        browse_btn.pack(side="left", padx=(8, 0))

        self.verbose_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm, text="Verbose (also console)", variable=self.verbose_var).grid(row=4, column=1, sticky="w")

        run_btn = ttk.Button(frm, text="Run", command=self._run_command)
        run_btn.grid(row=5, column=1, sticky="e")

        # Output
        ttk.Label(frm, text="Output").grid(row=6, column=0, sticky="nw")
        self.output = tk.Text(frm, wrap="word")
        self.output.grid(row=6, column=1, sticky="nsew")

        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(6, weight=1)

        # Select defaults
        if self.module_cb["values"]:
            self.module_var.set(self.module_cb["values"][0])
            self._on_module()

    def _on_module(self, _evt=None):
        m = self.module_var.get()
        services = sorted(self.dispatch[m].keys())
        self.service_cb["values"] = services
        self.service_var.set(services[0] if services else "")
        self._on_service()

    def _on_service(self, _evt=None):
        m = self.module_var.get()
        s = self.service_var.get()
        actions = sorted(self.dispatch[m][s].keys()) if s else []
        self.action_cb["values"] = actions
        self.action_var.set(actions[0] if actions else "")

    def _pick_file(self):
        path = filedialog.askopenfilename(
            title="Select payload file",
            filetypes=[
                ("JSON files", "*.json"),
                ("CSV files", "*.csv"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return

        # Parse existing args safely (handles quotes/spaces)
        current = self.args_entry.get().strip()
        tokens = shlex.split(current) if current else []

        # Remove any existing file arg
        tokens = [t for t in tokens if not (t.startswith("--file=") or t.startswith("file="))]

        # Add new file arg
        tokens.append(f"--file={path}")

        # Rebuild string with safe quoting (for paths with spaces)
        new_text = " ".join(shlex.quote(t) for t in tokens)

        self.args_entry.delete(0, "end")
        self.args_entry.insert(0, new_text)


    def _parse_args(self) -> dict:
        raw = self.args_entry.get().strip()
        args = {"verbose": self.verbose_var.get()}

        if not raw:
            return args

        # Split by whitespace (just like a real CLI)
        parts = raw.split()

        for p in parts:
            if "=" not in p:
                raise ValueError(f"Bad arg '{p}', expected key=value")

            key, value = p.split("=", 1)
            key = key.strip()
            value = value.strip()

            # Support --key=value or key=value
            if key.startswith("--"):
                key = key[2:]

            args[key] = value

        return args

    def _run_command(self):
        # Clear output for a clean run (no history)
        self.output.delete("1.0", "end")
        self.output.insert("end", "")  # ensures widget has a valid insert point
        self.output.update_idletasks()  # repaint immediately

        m = self.module_var.get()
        s = self.service_var.get()
        a = self.action_var.get()

        try:
            args = self._parse_args()

            # GUI should show output; this controls your handlers' log_to_file(also_console=verbose)
            args["verbose"] = self.verbose_var.get()

            handler = self.dispatch[m][s][a]

            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                result = handler(self.cp, self.token, APIPath, args)

            captured = buf.getvalue().strip()

            if captured:
                self.output.insert("end", captured + "\n")
            else:
                if result is None:
                    self.output.insert("end", "OK\n")
                else:
                    self.output.insert("end", json.dumps(result, indent=2, ensure_ascii=False) + "\n")

            self.output.see("end")  # scroll to bottom (not required, but nice)

        except Exception as e:
            self.output.insert("end", f"ERROR: {e}\n")
            self.output.see("end")


def run_gui():
    app = ArapyGUI()
    app.mainloop()