"""List item widgets."""

from textual.widgets import Label, ListItem


class AddItem(ListItem):
    """Add item."""

    def __init__(self, item_name: str, *args, **kwargs) -> None:
        """Construct an add item."""
        super().__init__(*args, **kwargs)
        self.item_name = item_name

    def compose(self) -> "ComposeResult":
        """Compose the widget."""
        yield Label(f"✚ Add {self.item_name.title()}", id=f"add-{self.item_name.lower()}")