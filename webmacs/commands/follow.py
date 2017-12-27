# This file is part of webmacs.
#
# webmacs is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# webmacs is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with webmacs.  If not, see <http://www.gnu.org/licenses/>.

from PyQt5.QtCore import QEvent, Qt

from ..minibuffer import Prompt, KEYMAP as MKEYMAP
from ..keymaps import Keymap
from ..commands import define_command
from .. import current_minibuffer, current_buffer
from ..application import app
from .prompt_helper import PromptNewBuffer


KEYMAP = Keymap("hint", MKEYMAP)

# took from conkeror
SELECTOR_CLICKABLE = (
    "//*[@onclick or @onmouseover or @onmousedown or @onmouseup or "
    "@oncommand or @role='link' or @role='button' or @role='menuitem']"
    " | //input[not(@type='hidden')] | //a[@href] | //area"
    " | //iframe | //textarea | //button | //select"
    " | //*[@contenteditable = 'true']"
    " | //xhtml:*[@onclick or @onmouseover or @onmousedown or"
    " @onmouseup or @oncommand or @role='link' or @role='button' or"
    " @role='menuitem'] | //xhtml:input[not(@type='hidden')]"
    " | //xhtml:a[@href] | //xhtml:area | //xhtml:iframe"
    " | //xhtml:textarea | //xhtml:button | //xhtml:select"
    " | //xhtml:*[@contenteditable = 'true'] | //svg:a"
)

SELECTOR_LINK = "//a[@href]"


class HintPrompt(Prompt):
    keymap = KEYMAP
    hint_selector = ""

    def enable(self, minibuffer):
        Prompt.enable(self, minibuffer)
        self.page = current_buffer()
        self.page.start_select_browser_objects(self.hint_selector)
        self.numbers = ""
        minibuffer.input().textChanged.connect(self.on_text_edited)
        self.browser_object_activated = {}
        self.page.content_handler.browserObjectActivated.connect(
            self.on_browser_object_activated
        )
        minibuffer.input().installEventFilter(self)

    def on_browser_object_activated(self, bo):
        self.browser_object_activated = bo
        self.minibuffer.input().set_right_italic_text(bo.get("url", ""))

    def on_text_edited(self, text):
        self.page.filter_browser_objects(text)

    def _update_label(self):
        label = self.label
        if self.numbers:
            label = label + (" #%s" % self.numbers)
        self.minibuffer.label.setText(label)

    def eventFilter(self, obj, event):
        numbers = ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0")
        if event.type() == QEvent.KeyPress:
            text = event.text()
            if text in numbers:
                self.numbers += text
                self.page.select_visible_hint(self.numbers)
                self._update_label()
                return True
            elif not event.key() in (Qt.Key_Control, Qt.Key_Shift, Qt.Key_Alt,
                                     Qt.Key_Meta, Qt.Key_unknown):
                self.numbers = ""
                self._update_label()
        return Prompt.eventFilter(self, obj, event)


class FollowPrompt(HintPrompt):
    label = "follow:"
    hint_selector = SELECTOR_CLICKABLE

    def enable(self, minibuffer):
        self.new_buffer = PromptNewBuffer()
        if self.new_buffer:
            self.hint_selector = SELECTOR_LINK
        HintPrompt.enable(self, minibuffer)
        self.new_buffer.enable(minibuffer)
        if self.new_buffer:
            self.label = minibuffer.label.text()


class CopyLinkPrompt(HintPrompt):
    label = "copy link:"
    hint_selector = SELECTOR_LINK


@define_command("follow", prompt=FollowPrompt)
def follow(prompt):
    """
    Hint links in the buffer and follow them on selection.
    """
    buff = prompt.page
    if not prompt.new_buffer:
        buff.focus_active_browser_object()
        buff.stop_select_browser_objects()
    elif "url" in prompt.browser_object_activated:
        buff.stop_select_browser_objects()
        prompt.new_buffer.get_buffer().load(
            prompt.browser_object_activated["url"]
        )


@define_command("copy-link", prompt=CopyLinkPrompt)
def copy_link(prompt):
    """
    Hint links in the buffer to copy them.
    """
    buff = prompt.page
    bo = prompt.browser_object_activated
    if "url" in bo:
        app().clipboard().setText(bo["url"])
        prompt.minibuffer.show_info("Copied: {}".format(bo["url"]))
    buff.stop_select_browser_objects()


@KEYMAP.define_key("C-g")
@KEYMAP.define_key("Esc")
def cancel():
    current_buffer().stop_select_browser_objects()
    current_minibuffer().close_prompt()


@KEYMAP.define_key("C-n")
@KEYMAP.define_key("Down")
def next_completion():
    current_buffer().select_nex_browser_object()


@KEYMAP.define_key("C-p")
@KEYMAP.define_key("Up")
def previous_completion():
    current_buffer().select_nex_browser_object(False)
