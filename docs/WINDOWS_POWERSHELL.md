# Windows PowerShell quick start

This guide runs the **public, synthetic reference toolkit** on Windows 10/11 with Python 3.10 or newer. It does not install a camera/NPU inference runtime or a production safety system.

Open PowerShell in a directory where you have write access:

```powershell
git clone https://github.com/Yazhou-Li/edgesafe-vision.git
Set-Location edgesafe-vision
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe examples\demo.py
.\.venv\Scripts\python.exe examples\adapter_demo.py
.\.venv\Scripts\python.exe examples\end_to_end_demo.py
.\.venv\Scripts\edgesafe-doctor.exe
```

The commands use the virtual environment's executables directly; no PowerShell execution-policy change or administrator privileges should be necessary. If `py -3` is unavailable, install Python 3.10+ and use its `python` executable to create the environment.

To probe a **service you own or are authorized to test**, supply an explicit loopback target:

```powershell
.\.venv\Scripts\edgesafe-doctor.exe --http http://127.0.0.1:5000
```

A failed probe is expected when nothing is listening on that port. The CLI is a diagnostic tool, not a service installer.

## What this does not prove

Passing synthetic tests on Windows does not establish production camera compatibility, NPU acceleration, audio delivery, persistent service operation, or Windows installer stability. Those require separate hardware-specific acceptance tests. Never paste production endpoints, credentials, customer identifiers, or unredacted evidence into public issues.
