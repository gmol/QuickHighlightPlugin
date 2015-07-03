#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gi.repository import Gtk, GtkSource, Keybinder, Gdk


class Popup(Gtk.Dialog):

    def __init__(self, window, popup_size, handler):

        Gtk.Dialog.__init__(self,
                    title=_('Quick Open'),
                    parent=window,
                    flags=Gtk.DialogFlags.DESTROY_WITH_PARENT | Gtk.DialogFlags.MODAL,
                    buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))

        # connect keyboard events
        self.connect('key-press-event', self.on_key_press_event)

        # set parent handler
        self.handler = handler

        # get list of lang syntax
        self.lang_manager = GtkSource.LanguageManager()
        lang_ids = self.lang_manager.get_language_ids()
        lang_ids.append("none")

        Gtk.Window.__init__(self, title="Treeviev")
        Gtk.Window.set_default_size(self, popup_size[0], popup_size[1])
        self.set_border_width(10)

        self.box = self.get_content_area()

        #Creating the ListStore model
        self.lang_liststore = Gtk.ListStore(str)
        for lang_id in lang_ids:
            self.lang_liststore.append([lang_id])
        self.current_filter_language = None

        self.treeview = Gtk.TreeView.new_with_model(self.lang_liststore)
        for i, column_title in enumerate(["Syntax"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.treeview.append_column(column)

        select = self.treeview.get_selection()
        select.connect("changed", self.on_tree_selection_changed)

        #setting up the layout, putting the treeview in a scrollwindow, and the buttons in a row
        self.scrollable_treelist = Gtk.ScrolledWindow()
        self.scrollable_treelist.set_vexpand(True)
        self.box.pack_start(self.scrollable_treelist, True, True, 0)

        self.scrollable_treelist.add(self.treeview)
        self.show_all()

        self._size = (0, 0)

    # handle resize event
    def do_configure_event(self, event):
        if self.get_realized():
            alloc = self.get_allocation()
            self._size = (alloc.width, alloc.height)

        return Gtk.Dialog.do_configure_event(self, event)
    
    # remember the dialog size
    def get_final_size(self):
        return self._size

    # handler for tree selection changed
    # not uses really
    def on_tree_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
#        if treeiter != None:
#            print "You selected", model[treeiter][0]

    # handle dialog button events
    def do_response(self, response):
        if response == Gtk.ResponseType.CANCEL:
            self.destroy()
        if response == Gtk.ResponseType.ACCEPT:
            lang = self.get_selected_lang()
            self.handler(lang)
            self.destroy()

    # handle keyboard events
    def on_key_press_event(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.destroy()
            return True
        elif event.keyval in [Gdk.KEY_Return, Gdk.KEY_KP_Enter]:
            lang = self.get_selected_lang()
            self.handler(lang)
            self.destroy()
        return False

    # get selected lang
    def get_selected_lang(self):
        selection = self.treeview.get_selection()
        if selection != None:
            model, treeiter = selection.get_selected()
            if treeiter != None:
                lang = self.lang_manager.get_language(model[treeiter][0])
                return lang
        return None
    
