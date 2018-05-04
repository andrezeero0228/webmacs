function clickLike(elem) {
    elem.focus();
    var doc = elem.ownerDocument;
    var view = doc.defaultView;

    var evt = doc.createEvent("MouseEvents");
    evt.initMouseEvent("mousedown", true, true, view, 1, 0, 0, 0, 0, /*ctrl*/ 0, /*event.altKey*/0,
                       /*event.shiftKey*/ 0, /*event.metaKey*/ 0, 0, null);
    elem.dispatchEvent(evt);

    evt = doc.createEvent("MouseEvents");
    evt.initMouseEvent("click", true, true, view, 1, 0, 0, 0, 0, /*ctrl*/ 0, /*event.altKey*/0,
                       /*event.shiftKey*/ 0, /*event.metaKey*/ 0, 0, null);
    elem.dispatchEvent(evt);

    evt = doc.createEvent("MouseEvents");
    evt.initMouseEvent("mouseup", true, true, view, 1, 0, 0, 0, 0, /*ctrl*/ 0, /*event.altKey*/0,
                       /*event.shiftKey*/ 0, /*event.metaKey*/ 0, 0, null);
    elem.dispatchEvent(evt);
}

function rectElementInViewport(elem, w) {  // eslint-disable-line complexity
    var win = elem.ownerDocument.defaultView;
    var rect = elem.getBoundingClientRect();
    w = w || window;

    if (!rect ||
        rect.top > w.innerHeight ||
        rect.bottom < 0 ||
        rect.left > w.innerWidth ||
        rect.right < 0) {
        return null;
    }

    rect = elem.getClientRects()[0];
    if (!rect) {
        return null;
    }

    var style = win.getComputedStyle(elem, null);
    if (style.getPropertyValue("visibility") !== "visible" ||
        style.getPropertyValue("display") === "none" ||
        style.getPropertyValue("opacity") === "0") {
        return null;
    }
    return rect;
}

function escapeRegExp(str) {
    return str.replace(/[\-\[\]\/\{\}\(\)\*\+\?\.\\\^\$\|]/g, "\\$&");
}

function Hint(obj, manager, left, top, index) {
    this.obj = obj;
    this.objBackground = obj.style.background;
    this.objColor = obj.style.color;
    obj.style.background = manager.options.background;
    obj.style.color = manager.options.text_color;
    this.index = index;
    var hint = document.createElement("span");
    hint.textContent = this.index;
    hint.style.background = manager.options.hint_background;
    hint.style.color = manager.options.hint_color;
    hint.style.position = "absolute";
    hint.style.zIndex = "2147483647";
    hint.style.left = left;
    hint.style.top = top;
    this.hint = hint;
    this.manager = manager;
}

Hint.prototype.text = function() {
    if (this.obj.textContent) {
        return this.obj.textContent;
    }
    return null;
}

Hint.prototype.url = function() {
    if (this.obj.href) {
        return this.obj.href;
    }
    return null;
}

Hint.prototype.remove = function() {
    this.obj.style.background = this.objBackground;
    this.obj.style.color = this.objColor;
    this.hint.parentNode.removeChild(this.hint);
}

Hint.prototype.setVisible = function(on) {
    this.hint.style.display = on ? "initial" : "none";
    this.refresh();
}

Hint.prototype.refresh = function() {
    if (this.isVisible()) {
        if (this.manager.activeHint == this) {
            this.obj.style.background = this.manager.options.background_active;
        } else {
            this.obj.style.background = this.manager.options.background;
        }
        this.obj.style.color = this.manager.options.text_color;
    } else {
        this.obj.style.background = this.objBackground;
        this.obj.style.color = this.objColor;
    }
}

Hint.prototype.isVisible = function() {
    return this.hint.style.display != "none";
}

Hint.prototype.serialize = function() {
    return JSON.stringify({
        nodeName: this.obj.nodeName,
        text: this.text(),
        id: this.hint.textContent,
        url: this.url()
    });
}

class HintFrame {
    constructor(frame) {
        this.frame = frame
    }

    remove() {
        post_message(this.frame.contentWindow, "hints.clearBrowserObjects", null);
    }
}

class Hinter {
    init(selector) {
        this.selector = selector;
        this.xres = document.evaluate(selector, document, xpath_lookup_namespace,
                                      XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,
                                      null);
        this.fragment = document.createDocumentFragment();
        this.index = 0;
        this.iframes_ranges = [];
        this.hints = {};
    }

    next(hint_index) {
        // has been cleared.
        if (this.hints === null) {
            return;
        }

        if (this.iframes_ranges.length > 0) {
            this.iframes_ranges[this.iframes_ranges.length - 1].end = hint_index;
        }
        for (; this.index < this.xres.snapshotLength; this.index++) {
            let obj = this.xres.snapshotItem(this.index);
            let rect = rectElementInViewport(obj, window);
            if (!rect) {
                continue;
            }
            if (obj.tagName == "IFRAME") {
                // console.log(window.frames[0].frames[0]);
                this.iframes_ranges.push({frame: obj, start: hint_index});
                post_message(obj.contentWindow, "hints.select_in_iframe_start",
                             {selector: this.selector, hint_index: hint_index});
                this.index+=1;
                return;
            }
            hint_index += 1;
            var hint = new Hint(obj, hints,
                                (rect.left + window.scrollX) + "px",
                                (rect.top + window.scrollY) + "px",
                                hint_index
                               );
            this.hints[hint_index] = hint;
            this.fragment.appendChild(hint.hint);
        }
        document.documentElement.appendChild(this.fragment);

        if (self !== top) {
            post_message(parent, "hints.select_in_iframe_end", hint_index)
        }
        console.log(this.iframes_ranges)
    }

    clear() {
        // has been cleared.
        if (this.hints === null) {
            return;
        }

        for (var name in this.hints) {
            this.hints[name].remove();
        }
        for (var iframe of this.iframes_ranges) {
            post_message(iframe.frame.contentWindow, "hints.select_clear", null);
        }
        this.hints = null;
        this.iframes_ranges = null;
    }
}

var hinter = new Hinter();

function HintManager() {
    this.hints = [];
    this.options = {
        hint_background: "red",
        hint_color: "white",
        background: "yellow",
        background_active: "#88FF00",
        text_color: "black"
    };
    this.activeHint = null;
}

// took from conkeror
XHTML_NS = "http://www.w3.org/1999/xhtml";
XUL_NS = "http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul";
MATHML_NS = "http://www.w3.org/1998/Math/MathML";
XLINK_NS = "http://www.w3.org/1999/xlink";
SVG_NS = "http://www.w3.org/2000/svg";

function xpath_lookup_namespace (prefix) {
    return {
        xhtml: XHTML_NS,
        m: MATHML_NS,
        xul: XUL_NS,
        svg: SVG_NS
    }[prefix] || null;
}

HintManager.prototype.selectBrowserObjects = function(selector, hint_index) {
    // Object.assign(this.options, options || {});
    hinter.init(selector);
    hinter.next(hint_index || 0);
    // this.setActiveHint((this.hints.length > 0) ? this.hints[0] : null);
}

HintManager.prototype.setActiveHint = function(hint) {
    var prevActive = this.activeHint;
    this.activeHint = hint;
    if (prevActive) { prevActive.refresh(); }
    if (hint) {
        hint.refresh();
        __webmacsHandler__._browserObjectActivated(hint.serialize());
    }
}

HintManager.prototype.visibleHints = function() {
    let visibles = [];
    for (let hint of this.hints) {
        if (hint.isVisible()) {
            visibles.push(hint);
        }
    }
    return visibles;
}

HintManager.prototype.selectVisibleHint = function(index) {
    for (let hint of this.visibleHints()) {
        if (hint.hint.textContent == index) {
            this.setActiveHint(hint);
            return;
        }
    }
    this.setActiveHint(null);
}

HintManager.prototype.activateNextHint = function(backward) {
    let visibles = this.visibleHints();
    if (visibles.length == 0) {
        return;
    }
    let pos = visibles.indexOf(this.activeHint);
    if (pos == -1) {
        this.setActiveHint(visibles[backward ? visibles.length - 1 : 0]);
        return;
    }
    pos = pos + (backward ? -1 : 1);
    if (pos < 0) {
        pos = visibles.length - 1;
    } else if (pos >= visibles.length) {
        pos = 0;
    }
    this.setActiveHint(visibles[pos]);
}

HintManager.prototype.filterSelection = function(text) {
    let i = 0;
    if (!text) {
        for (let hint of this.hints) {
            i = i+1;
            hint.setVisible(true);
            hint.hint.textContent = i;
        }
        return;
    }
    let activeHintRemoved = false;
    let firstHint = null;
    var parts = text.split(/\s+/).map(escapeRegExp);
    var re = new RegExp(".*" + parts.join(".*") + ".*", "i");
    for (let hint of this.hints) {
        let matched = false;
        text = hint.text();
        if (text !== null) {
            matched = (text.match(re) !== null);
        }

        if (matched) {
            i = i+1;
            hint.setVisible(true);
            hint.hint.textContent = i;
            if (! firstHint) {
                firstHint = hint;
            }
        } else {
            hint.setVisible(false);
            if (hint == this.activeHint) {
                activeHintRemoved = true;
            }
        }
    }
    if (activeHintRemoved && firstHint) {
        this.setActiveHint(firstHint);
    }
}

HintManager.prototype.clearBrowserObjects = function() {
    hinter.clear();
}

var hints = new HintManager();

if (self === top) {
    // var all_hints = [];

    // function register_hints() {};

    // window.addEventListener("load", function() {
    //     register_message_handler("hints.register_hints", register_hints);
    // });
} else {
    register_message_handler("hints.select_in_iframe_start",
                             args => hints.selectBrowserObjects(args.selector,
                                                                args.hint_index));
    register_message_handler("hints.select_clear",
                             _ => hinter.clear())
}
register_message_handler("hints.select_in_iframe_end",
                         hint_index => hinter.next(hint_index));
