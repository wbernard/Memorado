# SPDX-License-Identifier: GPL-3.0-or-later

import os
from pathlib import Path

from gi.repository import Gio

schema = Gio.Settings.new("im.bernard.Memorado")

data_dir = (
    Path(os.getenv("XDG_DATA_HOME"))
    if "XDG_DATA_HOME" in os.environ
    else Path.home() / ".local" / "share"
)

decks_dir = data_dir

