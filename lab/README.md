# Smart Lab Management & Evaluation System – Faculty Desktop (PyQt6)

Academic-style desktop UI for faculty to manage lab batches, monitor students, handle tasks, viva, exams, and reports. UI is reference-inspired (Edutech/ETLab) and uses mocked data only.

## Requirements
- Python 3.9+ (tested conceptually; works on Windows/Linux)
- PyQt6 (`pip install -r requirements.txt`)

## Run
```bash
python main.py
```

## Structure
- `main.py` – entrypoint, window shell with sidebar/top bar and stacked screens.
- `ui/theme.py` – colors, typography, base styles.
- `ui/common/` – reusable cards, badges, tables, buttons.
- `ui/screens/` – individual screen widgets (login, selection, dashboard, student list/progress/evaluation, live monitor, control, tasks, viva, exam, reports, settings).
- `data/mock_data.py` – sample data for UI.

## Notes
- UI-only; no real networking or PC control.
- Actions use placeholders/status messages to illustrate flows for viva/presentation.
- Styling sticks to indigo/teal with light backgrounds and status colors.

