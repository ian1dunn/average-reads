#!/usr/bin/python3
import random
import threading
import tkinter

import pathlib
from AverageReadsMain import validate_sign_in, validate_sign_up, sign_up_new_user, sign_in_user, \
    get_collection_view_data, \
    get_collections, read_book, rate_book, add_to_collection, create_collection, remove_from_collection, \
    book_in_collection, get_rating_on_book, delete_collection, change_collection_name, query_search, try_follow_user, \
    get_following, get_user, unfollow_user, get_book, sign_out_user, get_num_books_and_pages, States, process_finished

import tkinter.ttk as ttk
import pygubu

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "UI\\average_reads_pygubu.ui"


class AverageReadsPygubuApp:
    def __init__(self, master=None):
        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(PROJECT_PATH)
        builder.add_from_file(PROJECT_UI)
        # Main widget
        self.mainwindow = builder.get_object("toplevel1", master)

        self.email_var = None
        self.password_var = None
        self.first_name_var = None
        self.last_name_var = None
        self.username_var = None
        self.search_sort_var = None
        self.search_text_var = None
        self.collection_filter_text_var = None
        self.sort_by_var = None
        self.sort_order_var = None
        self.results_text_var = None
        self.collection_name_error_var = None
        self.following_error_var = None
        self.save_frame_var = None
        builder.import_variables(self,
                                 ['email_var',
                                  'password_var',
                                  'first_name_var',
                                  'last_name_var',
                                  'username_var',
                                  'search_sort_var',
                                  'search_text_var',
                                  'collection_filter_text_var',
                                  'sort_by_var',
                                  'sort_order_var',
                                  'results_text_var',
                                  'collection_name_error_var',
                                  'following_error_var',
                                  'save_frame_var'])

        self.setup_ttk_styles()

        main(self)

        builder.connect_callbacks(self)

    def run(self):
        self.mainwindow.mainloop()

    def setup_ttk_styles(self):
        # ttk styles configuration
        self.style = style = ttk.Style()
        optiondb = style.master
        PRIMARY_COLOR = [
            "#0d0f14",
            "#212733",
            "#323a4d",
            "#424d66",
            "#536180"
        ]

        HEADER = {
            "Font": [
                ("Cascadia Code", 14),
                ("Cascadia Code SemiBold", 10),
                ("Cascadia Code SemiBold", 8)
            ],
            "Color": [
                "white",
                "#e6e6e6",
                "#cccccc"
            ]
        }

        ENTRY_TEXT_COLOR = "white"

        MAIN_BTN_COLOR = "#f72d2d"
        SECONDARY_BTN_COLOR = "#f79f2d"
        style.theme_use("alt")

        style.configure("Header.TLabel", font=HEADER["Font"][0], background=PRIMARY_COLOR[1],
                        foreground=HEADER["Color"][0])
        style.configure("Header1.TLabel", font=HEADER["Font"][1], background=PRIMARY_COLOR[1],
                        foreground=HEADER["Color"][0])
        style.configure("Header1Bk2.TLabel", font=HEADER["Font"][1], background=PRIMARY_COLOR[2],
                        foreground=HEADER["Color"][0])
        style.configure("Header2Bk3.TLabel", font=HEADER["Font"][2], background=PRIMARY_COLOR[2],
                        foreground=HEADER["Color"][1])
        style.configure("Custom_Header.TLabel", font=HEADER["Font"][2], background=PRIMARY_COLOR[1])
        style.configure("Default_Background.TFrame", background=PRIMARY_COLOR[0])
        style.configure("Default_Background.TNotebook", background=PRIMARY_COLOR[0])
        style.configure("Inner_1.TFrame", background=PRIMARY_COLOR[1])
        style.configure("Inner_2.TFrame", background=PRIMARY_COLOR[2])
        style.configure("Inner_3.TFrame", background=PRIMARY_COLOR[3])
        style.configure("Innter_2List.TFrame", background=PRIMARY_COLOR[2], relief="ridge")
        style.configure("Normal_Entry.TEntry", fieldbackground=PRIMARY_COLOR[4], foreground=ENTRY_TEXT_COLOR,
                        selectbackground=SECONDARY_BTN_COLOR)

        style.configure("Main_Btn.TButton", font=HEADER["Font"][1], background=MAIN_BTN_COLOR)
        style.configure("Secondary_Btn.TButton", background=SECONDARY_BTN_COLOR, font=HEADER["Font"][2])
        style.configure("Secondary_Btn_MainColor.TButton", background=MAIN_BTN_COLOR, font=HEADER["Font"][2])

        style.configure("TCheckbutton", background=PRIMARY_COLOR[1], font=HEADER["Font"][2],
                        foreground=HEADER["Color"][0], indicatorcolor="black")
        style.configure("TMenubutton", background=PRIMARY_COLOR[3], font=HEADER["Font"][2], foreground=ENTRY_TEXT_COLOR)
        style.map("TMenubutton", background=[("active", PRIMARY_COLOR[4])])

# -------------------------------------------------- EXTERNAL SETUP -------------------------------------------------- #
    def show_something_else(self, widget_id):
        if widget_id == "show_sign_in":
            self.sign_in_frame.show(False)
        elif widget_id == "show_sign_up":
            self.sign_up_frame.show(False)

        self.si_email_cw.hide_error()
        self.si_password_cw.hide_error()
        self.su_email_cw.hide_error()
        self.su_password_cw.hide_error()
        self.first_name_cw.hide_error()
        self.last_name_cw.hide_error()
        self.username_cw.hide_error()

    def read_book_pressed(self):
        try:
            e1, e2 = int(self.start_page_entry.get()), int(self.end_page_entry.get())
            if 0 <= e1 < e2 <= self.viewing_book[2]:
                self.page_number_error.pack_forget()
                read_book(self.viewing_book_component.id, e1, e2)
                return
        except ValueError:
            pass
        self.page_number_error.pack(side=tkinter.LEFT)

    def rate_book_pressed(self):
        try:
            rating = float(self.rating_text_entry.get_text())
            if 1 <= rating <= 5:
                self.rating_error_label.pack_forget()
                rate_book(self.viewing_book_component.id, rating)
                return
        except ValueError:
            pass
        self.rating_error_label.pack(side=tkinter.LEFT)

    def close_save_frame(self):
        self.new_collection_lower_frame.hide()
        self.save_collection_frame.hide()
        self.view_user_frame.hide()
        self.save_frame.hide()

    def save_book_pressed(self):
        self.close_save_frame()
        self.save_frame_var.set("Save To...")
        self.save_collection_frame.show()
        self.new_collection_btn.show()
        self.save_frame.show(anchor=tkinter.NW, relx=.5, rely=.5, x=-120, y=-300, width=280, height=420)

    def create_new_collection_pressed(self):
        self.new_collection_btn.hide()
        self.new_collection_lower_frame.show()

    def create_collection_pressed(self):
        collection_name = self.collection_name_entry.get_text()
        if len(collection_name) > 0 and collection_name != "Enter Collection name...":  # Nice
            self.close_save_frame()
            add_to_collection(self.viewing_book_component.id, create_collection(collection_name))
            self.refresh_collections()
        else:
            self.collection_name_error_var.set(COLLECTION_ERROR_TEXT)

    def back_pressed(self):
        self.close_save_frame()
        if self.removed_from_collection and self.viewing_collection_component is not None:
            self.main_procedural.delete_component(self.viewing_book_component)
            self.removed_from_collection = False
        self.book_view_frame.hide()
        self.main_procedural.show()

    def delete_collection_pressed(self):
        delete_collection(self.viewing_collection_component.id)
        self.collection_checks_procedural.delete_component(
            self.collection_checks_procedural.get_by_id(self.viewing_collection_component.id))
        self.collection_procedural.delete_component(self.viewing_collection_component)
        self.viewing_collection_component = None
        self.main_procedural.hide()

    def view_random_pressed(self):
        if len(self.main_procedural.components) > 0:
            self.view_book(random.choice(self.main_procedural.components))

    def sort_books(self, _):
        if self.viewing_collection_component is None:
            self.search_pressed(True)
        else:
            self.refresh_collections()

    def follow_pressed(self):
        follow_text = self.following_friend_entry.get_text()
        if len(follow_text) > 0:
            result = try_follow_user(follow_text)
            self.following_error_var.set(FOLLOWING_ERROR_TEXTS[result])
            if result == 0:
                self.following_friend_entry.set_text("")
                self.refresh_following()


ERROR_LABEL_CLASS = "errorlabel"
GRID_INFO_MANAGER = "grid"
PACK_INFO_MANAGER = "pack"
PLACEHOLDER_COLOR = "#968e83"

LIST_PAD_X = 10
LIST_PAD_Y = 3

MOUSE_1 = "<Button-1>"
RETURN = "<Return>"

COLLECTION_COMPONENTS = ("Name: ", "Total Books: ", "Total Pages: ")
BOOK_COMPONENTS = (
    "Title: ", "Genre: ", "Pages: ", "Rating: ", "Author: ", "Publisher: ", "Audience: ", "Released Date: ")
USER_COMPONENTS = ("Username: ", "UID: ", "First Name: ", "Last Name: ", "Email: ", "Creation Date: ")

SEARCH_RESULT_TEXT = "Results: "
COLLECTION_CONTENT_TEXT = "Viewing Collection"

COLLECTION_ERROR_TEXT = "Name Required"

PASSWORD_INVALID_TEXT = "Your password must contain at least 1 special character."

FOLLOWING_ERROR_TEXTS = (
    "Successfully followed the user.", "No users associated with this email.", "Already following this user.")

PRIMARY_COLOR = [
    "#0d0f14",
    "#212733",
    "#323a4d",
    "#424d66",
    "#536180"
]

HEADER = {
    "Font": [
        ("Cascadia Code", 14),
        ("Cascadia Code SemiBold", 10),
        ("Cascadia Code SemiBold", 8)
    ],
    "Color": [
        "white",
        "#e6e6e6",
        "#cccccc"
    ]
}


class CWidget:
    last_shown = None

    def __init__(self, widget_name: str, variable=None, layout_method=tkinter.Pack, **kw):
        self.widget = self.builder.get_object(widget_name)
        self.variable = variable
        self.tkinter_method = layout_method
        self.layout_method = None
        self.bind_show_args(**kw)
        if variable:
            for child in self.widget.winfo_children():
                if child.winfo_class() == ERROR_LABEL_CLASS:
                    self.error_label = child
                    self.error_label.pack_forget()
                    break

    def hide(self):
        if self.widget.winfo_manager() == PACK_INFO_MANAGER:
            self.widget.pack_forget()
        elif self.widget.winfo_manager() == GRID_INFO_MANAGER:
            self.widget.grid_forget()
        else:
            self.widget.place_forget()

    def show(self, dont_hide_last: bool = True, **kw):
        if dont_hide_last:
            if len(kw) > 0:
                self.bind_show_args(**kw)
            self.layout_method()
        else:
            CWidget.set_last_shown(self, True)

    def value(self):
        return self.variable.get()

    def show_error(self):
        self.error_label.pack(anchor=tkinter.NW)

    def hide_error(self):
        self.error_label.pack_forget()

    def set_error_text(self, text, show: bool = True):
        self.error_label.config(text=text)
        if show:
            self.show_error()

    def bind_show_args(self, **kw):
        if self.tkinter_method == tkinter.Pack:
            self.layout_method = lambda: self.widget.pack(**kw)
        elif self.tkinter_method == tkinter.Place:
            self.layout_method = lambda: self.widget.place(**kw)

    @classmethod
    def set_builder(cls, builder: pygubu.Builder):
        cls.builder = builder

    @classmethod
    def set_last_shown(cls, new_to_show, hide_last: bool = False):
        if hide_last and cls.last_shown:
            cls.last_shown.hide()
        new_to_show.show()
        cls.last_shown = new_to_show


class ListComponent:
    def __init__(self, master=None, label_texts=None, cur_texts: list = None, identifier=None,
                 selected_method=None,
                 height=0, width=235, cursor="hand2", show=True):
        self.texts = label_texts
        self.id = identifier
        self.cur_texts = cur_texts if cur_texts else ["" for _ in range(len(label_texts))]
        self.cursor = cursor
        self.height = height
        self.width = width
        self.labels = list()
        self.selected_method = selected_method
        self.frame = None
        self.auto_show = show

        if master:
            self.master_init(master)

    def _selected(self, *_):
        self.selected_method(self)

    def master_init(self, master):
        self.frame = frame = ttk.Frame(master, borderwidth=1, style="Innter_2List.TFrame", cursor=self.cursor)
        ttk.Frame(frame, height=self.height, width=self.width, style="Inner_2.TFrame").pack()

        idx = 0
        for txt in self.texts:
            self.labels.append(ttk.Label(frame, text=txt + str(self.cur_texts[idx]), style="Header2Bk3.TLabel", wraplength=self.width*2))
            if self.selected_method:
                self.labels[-1].bind(MOUSE_1, self._selected)
            self.labels[-1].pack(anchor=tkinter.NW, fill=tkinter.X)
            idx += 1

        if self.auto_show:
            self.show()

    def update_label_text(self, idx: int, text):
        self.cur_texts[idx] = text
        self.labels[idx].config(text=self.texts[idx] + str(text))

    def update_cur_texts(self, new_texts: list):
        self.cur_texts = new_texts
        for i in range(len(new_texts)):
            self.update_label_text(i, new_texts[i])

    def get_label_text(self, idx):
        return self.cur_texts[idx]

    def show(self):
        self.frame.pack(padx=LIST_PAD_X, pady=LIST_PAD_Y)

    def hide(self):
        self.frame.pack_forget()


class CheckboxComponent:
    def __init__(self, master=None, text=None, identifier=None, selected_method=None, checked=False, show=True):
        self.variable = tkinter.IntVar(value=1 if checked else 0)
        self.id = identifier
        self.selected_method = selected_method
        self.init_text = text
        self.check_btn = None
        self.auto_show = show

        if master:
            self.master_init(master)

    def _selected(self, *_):
        self.variable.set(1 if self.variable.get() == 1 else 0)
        self.selected_method(self)

    def master_init(self, master):
        self.check_btn = ttk.Checkbutton(master, text=self.init_text, variable=self.variable, command=self._selected)
        if self.auto_show:
            self.show()

    def update_text(self, text):
        self.check_btn.config(text=text)

    def is_checked(self):
        return self.variable.get() == 1

    def force_state(self, checked):
        self.variable.set(1 if checked else 0)

    def show(self):
        self.check_btn.pack(fill=tkinter.X)

    def hide(self):
        self.check_btn.pack_forget()


class PlaceholderEntry:
    def __init__(self, entry: ttk.Entry, text: str = None):
        self.entry = entry
        text = text if text else entry.get()
        self.placed_holder = False
        self.default_color = entry["foreground"]

        def focused(*_):
            if self.placed_holder:
                self.placed_holder = False
                entry.delete("0", "end")
                entry["foreground"] = self.default_color

        def unfocused(*args):
            if not entry.get() or args[0] is True:
                self.placed_holder = True
                entry.insert(0, text)
                entry["foreground"] = PLACEHOLDER_COLOR

        entry.bind("<FocusIn>", focused)
        entry.bind("<FocusOut>", unfocused)
        entry.delete("0", "end")
        unfocused(True)

    def get_text(self):
        return self.entry.get() if not self.placed_holder else ""

    def set_text(self, text):
        self.placed_holder = False
        self.entry["foreground"] = self.default_color
        self.entry.delete("0", "end")
        self.entry.insert(0, text)

    def bind(self, sequence: str, callback):
        self.entry.bind(sequence, callback)


class ProceduralScroller(CWidget):
    """
    Tkinter sucks and will die if we pack too many widgets at a time. Nice. This was cool to make at least.
    Turns pygubu ScrolledFrame into procedural scroll frames so they'll render as the user scrolls to a certain point.
    """
    RENDER_AMOUNT = 25  # How many books to render at a time
    INITIAL_RENDER = RENDER_AMOUNT * 2  # The starting render amount (bigger than render amount)

    def __init__(self, widget_name, component_master=None, variable=None, layout_method=tkinter.Pack, **kw):
        CWidget.__init__(self, widget_name, variable, layout_method, **kw)
        self.scrolled_frame = self.widget
        self.render_amount = ProceduralScroller.RENDER_AMOUNT
        self.render_difference = ProceduralScroller.INITIAL_RENDER - self.render_amount
        self.components = []
        self._last_idx = 0
        self._next_render_threshold = 0
        self._rendering = False
        self._component_frame = ttk.Frame()
        self._component_master = component_master if component_master else self.scrolled_frame.innerframe

        def reposition():
            self.scrolled_frame._scrollBothNow()
            if self._should_render():
                threading.Thread(target=self._render_next, args=[self.render_amount]).start()

        self.scrolled_frame.reposition = reposition

    def _should_render(self):
        return not self._rendering and self.scrolled_frame._getyview()[1] >= self._next_render_threshold

    def _render_next(self, to_add: int):
        self._rendering = True
        last_index = self._last_idx
        self._last_idx += min(len(self.components) - last_index, to_add)
        for i in range(last_index, self._last_idx):
            self.components[i].master_init(self._component_frame)
            self.components[i].show()
        self._next_render_threshold = 1 - self.render_amount / self._last_idx if self._last_idx != len(
            self.components) else 10  # Never will reach 10
        self._rendering = False

    def set_components(self, components):
        self._next_render_threshold = 0
        self._last_idx = 0
        self._rendering = False
        self.components = components
        self._component_frame.pack_forget()
        self._component_frame = ttk.Frame(self._component_master, style="Inner_2.TFrame")
        self._component_frame.pack(fill=tkinter.BOTH)
        self._render_next(ProceduralScroller.INITIAL_RENDER)

    def get_by_id(self, identifier):
        for component in self.components:
            if component.id == identifier:
                return component

    def delete_component(self, component):
        location = self.components.index(component)
        if location <= self._last_idx:
            self._last_idx -= 1
        self.components.pop(location)
        component.hide()


def count_total_pages(books):
    total = 0
    for book in books:
        total += book.pages
    return total


def db_result_to_str(results: list[tuple]):
    final_str = ""
    for result in results:
        final_str += (", " if len(final_str) > 0 else "") + str(result[0])
    return final_str


def main(self: AverageReadsPygubuApp):
    CWidget.set_builder(self.builder)
    self.sign_in_frame = CWidget("sign_in_frame", expand=True)
    self.sign_up_frame = CWidget("sign_up_frame", expand=True)
    self.results_frame = CWidget("results_frame")
    self.book_view_frame = CWidget("book_view_frame")
    self.collection_info_frame = CWidget("collection_info_frame")
    self.new_collection_btn = CWidget("new_collection_btn", fill=tkinter.X, padx=15, pady=10)
    self.new_collection_lower_frame = CWidget("new_collection_lower_frame", fill=tkinter.X, padx=15, pady=10)
    self.save_frame = CWidget("save_frame", layout_method=tkinter.Place)
    self.main_frame = CWidget("main_frame", layout_method=tkinter.Place, relwidth=1, relheight=1)
    self.prompt_frame = CWidget("prompt_frame", layout_method=tkinter.Place, relwidth=1, relheight=1)
    self.save_collection_frame = CWidget("save_collection_frame", expand=tkinter.TRUE, fill=tkinter.BOTH)
    self.view_user_frame = CWidget("view_user_frame", expand=tkinter.TRUE, fill=tkinter.BOTH)

    self.book_search_entry = PlaceholderEntry(self.builder.get_object("book_search_entry"))
    self.collection_name_entry = PlaceholderEntry(self.builder.get_object("collection_name_entry"))
    self.collection_view_name_entry = PlaceholderEntry(self.builder.get_object("collection_view_name_entry"))
    self.following_friend_entry = PlaceholderEntry(self.builder.get_object("following_friend_entry"))
    self.rating_text_entry = PlaceholderEntry(self.builder.get_object("rating_text_entry"))

    self.main_procedural = ProceduralScroller("main_scroller", component_master=self.results_frame.widget,
                                              side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)
    self.following_procedural = ProceduralScroller("following_scroller",
                                                   component_master=self.builder.get_object("inner_following_frame"))
    self.collection_procedural = ProceduralScroller("collection_scroller",
                                                    component_master=self.builder.get_object("collection_quick_frame"))
    self.collection_checks_procedural = ProceduralScroller("save_scroller", expand=tkinter.TRUE, fill=tkinter.BOTH,
                                                           padx=10)

    self.start_page_entry = self.builder.get_object("start_page_entry")
    self.end_page_entry = self.builder.get_object("end_page_entry")
    self.page_number_error = self.builder.get_object("page_number_error")
    self.rating_error_label = self.builder.get_object("rating_error_label")

    self.si_email_cw = CWidget("si_email_frame", variable=self.email_var)
    self.si_password_cw = CWidget("si_pw_frame", variable=self.password_var)
    self.su_email_cw = CWidget("su_email_frame", variable=self.email_var)
    self.su_password_cw = CWidget("su_pw_frame", variable=self.password_var)
    self.first_name_cw = CWidget("su_fn_frame", variable=self.first_name_var)
    self.last_name_cw = CWidget("su_ln_frame", variable=self.last_name_var)
    self.username_cw = CWidget("su_un_frame", variable=self.username_var)

    self.details_lc = ListComponent(self.builder.get_object("details_frame"), BOOK_COMPONENTS, width=500, cursor="")
    self.user_details_lc = ListComponent(self.builder.get_object("user_contents_scrolled").innerframe, USER_COMPONENTS,
                                         width=200, cursor="")

    self.viewing_book_component = None
    self.viewing_book = None
    self.removed_from_collection = False
    self.viewing_user_component = None
    self.viewing_collection_component = None
    self.previous_query = ""
    self.previous_search_sort = self.search_sort_var.get()

    def view_book(component):
        # Set Previous Rating by the user in rating_text_entry spot
        self.viewing_book_component = component
        book_data, genre_data, rating, author_data, publisher_data, audience_data, release_date = get_book(component.id)
        self.viewing_book = book_data
        self.details_lc.update_cur_texts(
            [book_data[1], db_result_to_str(genre_data), book_data[2], rating,
             db_result_to_str(author_data), db_result_to_str(publisher_data),
             db_result_to_str(audience_data), release_date])
        self.removed_from_collection = False

        self.rating_text_entry.set_text(get_rating_on_book(component.id))

        for checkbox in self.collection_checks_procedural.components:
            checkbox.force_state(book_in_collection(self.viewing_book_component.id, checkbox.id))

        self.main_procedural.hide()
        self.book_view_frame.show()

    def view_collection(component: ListComponent):
        self.viewing_collection_component = component
        self.main_procedural.show()
        self.book_view_frame.hide()
        self.close_save_frame()
        self.collection_info_frame.show()
        collection_name, collection_books = get_collection_view_data(component.id, self.sort_by_var.get(),
                                                                     self.sort_order_var.get())
        self.results_text_var.set(COLLECTION_CONTENT_TEXT)
        self.collection_view_name_entry.set_text(collection_name)

        self.main_procedural.set_components([ListComponent(label_texts=BOOK_COMPONENTS, width=500,
                                                           selected_method=view_book, identifier=book_data[0],
                                                           cur_texts=[book_data[1], db_result_to_str(genre_data),
                                                                      book_data[2], rating,
                                                                      db_result_to_str(author_data),
                                                                      db_result_to_str(publisher_data),
                                                                      db_result_to_str(audience_data), release_date])
                                             for
                                             book_data, genre_data, rating, author_data, publisher_data, audience_data, release_date
                                             in
                                             collection_books])

    def toggle_book_in_collection_state(checkbox_component: CheckboxComponent):
        if checkbox_component.is_checked():
            add_to_collection(self.viewing_book_component.id, checkbox_component.id)
            self.removed_from_collection = False
        else:
            remove_from_collection(self.viewing_book_component.id, checkbox_component.id)
            self.removed_from_collection = True
        self.refresh_collections(True)

    def refresh_collections(toggled_state=False):
        collections = get_collections()

        collection_components = []
        checkbox_components = []

        for name, c_id in collections:
            num_books, pages = get_num_books_and_pages(c_id)
            collection_components.append(ListComponent(label_texts=COLLECTION_COMPONENTS,
                                                       identifier=c_id,
                                                       cur_texts=[name, num_books, pages],
                                                       selected_method=view_collection))
            if not toggled_state:
                checkbox_components.append(
                    CheckboxComponent(identifier=c_id, text=name,
                                      checked=False if not self.viewing_book_component else book_in_collection(
                                          self.viewing_book_component.id, c_id),
                                      selected_method=toggle_book_in_collection_state))

        self.collection_procedural.set_components(collection_components)
        if not toggled_state:
            self.collection_checks_procedural.set_components(checkbox_components)

    def attempt_collection_name_change(*_):
        new_name = self.collection_view_name_entry.get_text()
        if len(new_name) > 0:
            change_collection_name(self.viewing_collection_component.id, new_name)
            self.viewing_collection_component.update_label_text(0, new_name)
            self.collection_checks_procedural.get_by_id(self.viewing_collection_component.id).update_text(new_name)
            self.main_procedural.show()

    def search_for_book(search_text, search_sort):
        self.previous_query = search_text
        self.previous_search_sort = search_sort
        self.viewing_book_component = None
        self.viewing_book = None
        self.viewing_collection_component = None

        results = query_search(search_text, search_sort, self.sort_by_var.get(), self.sort_order_var.get())
        self.results_text_var.set(SEARCH_RESULT_TEXT + str(len(results)))

        self.main_procedural.set_components([ListComponent(label_texts=BOOK_COMPONENTS, width=500,
                                                           selected_method=view_book, identifier=book_data[0],
                                                           cur_texts=[book_data[1], db_result_to_str(genre_data),
                                                                      book_data[2], rating,
                                                                      db_result_to_str(author_data),
                                                                      db_result_to_str(publisher_data),
                                                                      db_result_to_str(audience_data), release_date])
                                             for
                                             book_data, genre_data, rating, author_data, publisher_data, audience_data, release_date
                                             in
                                             results])

        self.book_view_frame.hide()
        self.collection_info_frame.hide()
        self.close_save_frame()
        self.main_procedural.show()

    def search_pressed(last=False, *args):
        if last is True:
            search_text = self.previous_query
            search_sort = self.previous_search_sort
        else:
            search_text = self.book_search_entry.get_text()
            search_sort = self.search_sort_var.get()

        search_for_book(search_text, search_sort)

    def sign_in(params):
        if type(params) != str:  # signing up
            sign_up_new_user(*params)
            sign_in_user(params[0])
        else:
            sign_in_user(params)
        self.show_something_else("show_sign_in")

        self.email_var.set("")
        self.password_var.set("")
        self.email_var.set("")
        self.password_var.set("")
        self.first_name_var.set("")
        self.last_name_var.set("")
        self.username_var.set("")
        self.prompt_frame.hide()
        self.main_frame.show()

        refresh_collections()
        refresh_following()

    def sign_out_pressed():
        sign_out_user()
        self.prompt_frame.show()
        self.main_frame.hide()
        self.save_frame.hide()

    def display_user(component: ListComponent):
        self.close_save_frame()
        self.viewing_user_component = component
        user_id, username, _, f_name, l_name, email, creation_date, _ = get_user(self.viewing_user_component.id)

        self.user_details_lc.update_cur_texts(
            [username, user_id, f_name, l_name, email, creation_date])
        self.view_user_frame.show()
        self.save_frame.show(anchor=tkinter.NW, relx=.5, rely=.5, x=-120, y=-300, width=280, height=250)

    def unfollow_pressed():
        unfollow_user(self.viewing_user_component.id)
        self.view_user_frame.hide()
        self.save_frame.hide()
        refresh_following()

    def refresh_following():
        # Note, usernames don't automatically refresh
        self.following_procedural.set_components([ListComponent(label_texts=[""], cur_texts=[username],
                                                                identifier=user_id, selected_method=display_user)
                                                  for user_id, username in get_following()])

    def request_sign_in():
        results = validate_sign_in(self.si_email_cw.value(), self.si_password_cw.value())
        if results[0] == States.INVALID:
            self.si_email_cw.show_error()
        else:
            self.si_email_cw.hide_error()

        if results[1] == States.VALID:
            self.si_password_cw.hide_error()
        elif results[1] == States.INVALID_PASSWORD:
            self.si_password_cw.set_error_text("Invalid email or password.")
        else:
            self.si_password_cw.set_error_text(PASSWORD_INVALID_TEXT)

        if results[0] == States.EXISTS and results[1] == States.VALID:
            sign_in(self.si_email_cw.value())

    def request_sign_up():
        results = validate_sign_up(self.su_email_cw.value(), self.su_password_cw.value(), self.first_name_cw.value(),
                                   self.last_name_cw.value(), self.username_cw.value())
        if results[0] == States.INVALID:
            self.su_email_cw.set_error_text("Please enter a valid email address.")
        elif results[0] == States.EXISTS:
            self.su_email_cw.set_error_text("This email is already in use.")
        else:
            self.su_email_cw.hide_error()

        if results[1] == States.VALID:
            self.si_password_cw.hide_error()
        else:
            self.si_password_cw.show_error()

        if results[2] == States.INVALID:
            self.first_name_cw.show_error()
        else:
            self.first_name_cw.hide_error()

        if results[3] == States.INVALID:
            self.last_name_cw.show_error()
        else:
            self.last_name_cw.hide_error()

        if results[4] == States.INVALID:
            self.username_cw.set_error_text("Please enter a valid username.")
        elif results[4] == States.EXISTS:
            self.username_cw.set_error_text("This username is already in use.")
        else:
            self.username_cw.hide_error()

        if results[0] == States.VALID and results[1] == States.VALID and results[2] == States.VALID and results[
            3] == States.VALID and results[4] == States.VALID:
            sign_in((self.si_email_cw.value(), self.si_password_cw.value(), self.first_name_cw.value(),
                     self.last_name_cw.value(), self.username_cw.value()))

    self.setup_collections = refresh_collections
    self.refresh_collections = refresh_collections
    self.view_book = view_book
    self.search_pressed = search_pressed
    self.refresh_following = refresh_following
    self.unfollow_pressed = unfollow_pressed
    self.sign_out_pressed = sign_out_pressed

    self.request_sign_in = request_sign_in
    self.request_sign_up = request_sign_up

    self.collection_view_name_entry.bind(RETURN, attempt_collection_name_change)
    self.book_search_entry.bind(RETURN, search_pressed)

    PlaceholderEntry(self.start_page_entry)
    PlaceholderEntry(self.end_page_entry)

    self.collection_name_error_var.set("")

    # Forget lots of stuff
    self.page_number_error.pack_forget()
    self.rating_error_label.pack_forget()
    self.save_collection_frame.hide()
    self.view_user_frame.hide()
    self.sign_in_frame.hide()
    self.sign_up_frame.hide()
    self.main_procedural.hide()
    self.prompt_frame.hide()
    self.new_collection_lower_frame.hide()
    self.book_view_frame.hide()
    self.collection_info_frame.hide()
    self.save_frame.hide()
    self.main_frame.hide()

    self.show_something_else("show_sign_in")
    self.prompt_frame.show()


# -------------------------------------------------------------------------------------------------------------------- #


if __name__ == "__main__":
    app = AverageReadsPygubuApp()
    try:
        app.run()
    except KeyboardInterrupt:
        pass
    finally:
        process_finished()
