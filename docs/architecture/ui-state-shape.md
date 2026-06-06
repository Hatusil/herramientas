# UI State Shape

A typed dataclass replaces `self._main_ui.X = self._X` monkey-patching. Tab
widgets publish once at init; handlers read state directly. This is the
shape any new tab-based tool should follow.

## Dataclass shape

`PDFState` holds every widget reference a tab publishes. Each field uses the
exact CTk widget class — no `Any`, no widening — so an IDE flags type
mismatches at the call site.

```python
from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional
import customtkinter as ctk

@dataclass
class PDFContext:
    files: List[str] = field(default_factory=list)
    status_label: Optional[ctk.CTkLabel] = None
    process_async: Callable[..., Any] = None

@dataclass
class PDFState:
    annot_text: Optional[ctk.CTkEntry] = None
    rotate_var: Optional[ctk.StringVar] = None
    info_text: Optional[ctk.CTkTextbox] = None
    # ... one field per widget the tab owns ...
    ctx: PDFContext = field(default_factory=PDFContext)
```

`PDFContext` carries the three chrome handles (file list, status label,
async dispatcher) that handlers need but that don't belong on widget state.
Both classes live in `tools/pdf_tool/ui/state.py`.

## Publish-once-at-init rule

Tabs assign each widget to `self._state.<attr>` exactly once, at the end of
`_setup_frame()`. Click handlers never reassign — they read the typed field
directly. This makes the publish step a single reviewable block and removes
the dead duplicate `self._main_ui.X = self._X` lines that used to live in
every click handler.

```python
def _setup_frame(self) -> None:
    self._annot_text = create_entry(...)
    # ... build widgets ...
    self._state.annot_text = self._annot_text
    self._state.annot_page = self._annot_page
```

The orchestrator (`PDFToolUI`) instantiates `self._state = PDFState()` and
wires `self._state.ctx` before any tab is built. Tabs receive `state` via
their constructor.

## R12/R14 invariants

**R12** (`tests/test_arch_structure.py`): every tool with `ui/tabs/` MUST
ship `ui/state.py` containing a `@dataclass` class. Enforced by AST scan
after this change. The dataclass provides the typed surface area the rule
expects.

**R14** (`tests/test_arch_structure.py`): `tools/*/ui/tabs/*.py` MUST NOT
mutate `self._main_ui` via direct assignment or `setattr(self._main_ui, ...)`.
Enforced by AST scan after this change. Publish-once-at-init satisfies it by
construction: there is no second publish site left to mutate.

Both rules flip from `pytest.skip` (warning-only) to `assert not violations`
(strict) in the same commit that lands the refactor — see the test file
for the exact line.

## 10-line code skeleton

Copy this block into a sibling tool's `ui/state.py`, then add fields and a
`@dataclass` to match the new tool's widgets.

```python
from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional
import customtkinter as ctk
@dataclass
class ToolContext:
    files: List[str] = field(default_factory=list)
    status_label: Optional[ctk.CTkLabel] = None
    process_async: Callable[..., Any] = None
@dataclass
class ToolState:
    primary_input: Optional[ctk.CTkEntry] = None
    output_view: Optional[ctk.CTkTextbox] = None
    ctx: ToolContext = field(default_factory=ToolContext)
```

<!-- future: consider tests/test_pattern_doc.py that imports the skeleton and asserts it instantiates -->
