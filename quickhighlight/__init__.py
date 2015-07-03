from gettext import gettext as _
from gi.repository import GObject, Gtk, Gedit
from .popup import Popup

# Menu item example, insert a new item in the Tools menu
ui_str = """<ui>
  <menubar name="MenuBar">
    <menu name="ToolsMenu" action="Tools">
      <placeholder name="ToolsOps_2">
        <menuitem name="QuickHighlight" action="QuickHighlight"/>
      </placeholder>
    </menu>
  </menubar>
</ui>
"""
class QuickHighlightWindowActivatable(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = "QuickHighlightWindowActivatable"

    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        self._popup_size = (450, 500)
        self._popup = None
        # Insert menu items
        self._insert_menu()

    def do_deactivate(self):
        # Remove any installed menu items
        self._remove_menu()

        self._action_group = None

    def get_popup_size(self):
        return self._popup_size

    def set_popup_size(self, size):
        self._popup_size = size

    def _insert_menu(self):
        # Get the Gtk.UIManager
        manager = self.window.get_ui_manager()

        # Create a new action group
        self._action_group = Gtk.ActionGroup("QuickHighlightPluginActions")
        self._action_group.add_actions([("QuickHighlight", None, _("Switch syntax highlight"),
                                         "<Shift><Control>h", _("Switch between document syntax highlight modes"),
                                         self.on_switch_syntax_highlight)])

        # Insert the action group
        manager.insert_action_group(self._action_group, -1)

        # Merge the UI
        self._ui_id = manager.add_ui_from_string(ui_str)

    def _remove_menu(self):
        # Get the Gtk.UIManager
        manager = self.window.get_ui_manager()

        # Remove the ui
        manager.remove_ui(self._ui_id)

        # Remove the action group
        manager.remove_action_group(self._action_group)

        # Make sure the manager updates
        manager.ensure_update()

    def do_update_state(self):
        self._action_group.set_sensitive(self.window.get_active_document() != None)


    def _create_popup(self):
        self._popup = Popup(self.window, self.get_popup_size(), self.on_syntax_selected)
        self.window.get_group().add_window(self._popup)
        self._popup.set_default_size(*self.get_popup_size())
        self._popup.set_transient_for(self.window)
        self._popup.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self._popup.connect('destroy', self.on_popup_destroy)


    #
    # Callbacks
    #

    # Menu activate handlers
    def on_switch_syntax_highlight(self, action):
        doc = self.window.get_active_document()
        if not doc:
            return

        if not self._popup:
            self._create_popup()

        self._popup.show()

    def on_popup_destroy(self, popup, user_data=None):
        # read the previous popup size
        self.set_popup_size(popup.get_final_size())
        self._popup = None

    def on_syntax_selected(self, selected_lang):
        doc = self.window.get_active_document()
        if not selected_lang:
            # set to plain text
            doc.set_language(selected_lang)
            return
        if not doc:
            return
        doc.set_language(selected_lang)
    

