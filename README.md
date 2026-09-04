# Anime Recommender

## Running the project

From the repository root, the recommended command is:

```powershell
.\.venv\Scripts\python.exe -m src.recommender
```

You can also run the file directly:

```powershell
.\.venv\Scripts\python.exe src\recommender.py
```

The module handles both launch styles. Package execution is generally preferable because Python keeps the repository root as the import root; direct execution instead puts `src` on the import path and uses the sibling-module import.

In VS Code, select `.venv\Scripts\python.exe` with **Python: Select Interpreter** before running the project. Using the system `python` can produce a separate missing-dependency error because the project packages are installed in `.venv`.
