"""Dokli TUI.

The TUI package's ``__init__`` must not import ``app`` (or anything else that
depends on ``textual``) at package-import time: the manifest/plan/apply path
imports ``dokli.tui.engine``, and running this ``__init__`` would otherwise
pull in ``textual`` even when the optional ``tui`` extra is not installed,
breaking the CLI entirely (see #121).

Import the app explicitly: ``from dokli.tui.app import DokliApp``.
"""
