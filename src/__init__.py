from __future__ import annotations
from typing import Any

from aqt import mw, gui_hooks, DialogManager
from aqt.toolbar import Toolbar
from aqt.qt import *
from aqt.utils import showWarning

ADDON_NAME = "Focus on Single Deck"
ACTIVE = False

original_closeEvent = mw.closeEvent


def closeEvent(event: QCloseEvent) -> None:
    event.ignore()


def start_focus() -> None:
    global ACTIVE
    if ACTIVE:
        return
    if mw.state != "review":
        showWarning(
            "Focus mode can only be entered when you're reviewing a deck",
            parent=mw,
            title=ADDON_NAME,
        )
        return

    mw.closeEvent = closeEvent
    mw.toolbar.web.eval(
        """
        document.getElementById('focus').style.color = '#fbbf24';
    """
    )
    ACTIVE = True


def exit_focus() -> None:
    global ACTIVE
    mw.closeEvent = original_closeEvent
    mw.toolbar.web.eval(
        """
        document.getElementById('focus').style.color = '';
    """
    )
    ACTIVE = False


def add_link(links: list[str], top_toolbar: Toolbar) -> None:
    my_link = top_toolbar.create_link(
        cmd="focus_on_deck",
        label="Focus",
        tip="Enter focus mode",
        func=start_focus,
        id="focus",
    )
    links.append(my_link)


def on_state_change(new_state: str, old_state: str) -> None:
    if ACTIVE and old_state == "review" and mw.col.sched.getCard():
        mw.moveToState("review")
        return
    if new_state == "overview":
        exit_focus()


FORBIDDEN_DIALOGS = {
    "AddonsDialog",
    "Browser",
    "DeckStats",
    "NewDeckStats",
    "About",
    "Preferences",
}


def restricted_open(self: DialogManager, name: str, *args: Any, **kwargs: Any) -> Any:
    if ACTIVE and name in FORBIDDEN_DIALOGS:
        showWarning(
            "Sorry, you can't go there before finshing your deck!",
            parent=mw,
            title=ADDON_NAME,
        )
        return None
    return open_dialog(self, name, *args, **kwargs)


gui_hooks.top_toolbar_did_init_links.append(add_link)
gui_hooks.state_did_change.append(on_state_change)
open_dialog = DialogManager.open
DialogManager.open = restricted_open
