from uuid import uuid4
from .session import Session
import uix
class Element:
    def __init__(self, value = None, id = None):
        self.session = None
        self.tag = "div"
        self.id = id
        self._value = value
        self.children = []
        self.events = {}
        self.styles = {}
        self.classes = []
        self.attrs = {}
        self.parent = None
        self.old_parent = None
        self.value_name = "value"
        self.has_content = True
        
        if uix.ui_root is None:
            uix.ui_root = self

        self.parent = uix.app.ui_parent
        if self.parent is not None:
            self.parent.children.append(self)
    
    def bind(self,session,only_children=False):
        self.session = session
        if not only_children:
            if self.id is not None:
                self.session.elements[self.id] = self
        for child in self.children:
            child.bind(session)

    def unbind(self):
        if self.id is not None:
            del self.session.elements[self.id]
        for child in self.children:
            child.unbind()
    # WITH ENTRY - EXIT -------------------------------------------------------------------------------
    def __enter__(self):
        self.old_parent = uix.app.ui_parent
        uix.app.ui_parent = self
        for child in self.children:
            child.unbind()
        self.children = []
        return self

    def __exit__(self, type, value, traceback):
        uix.app.ui_parent = self.old_parent
        if(self.session is not None):
            self.bind(self.session,only_children=True)

    def __str__(self):
        return self.render()
    
    # RUNTIME UPDATE ELEMENT ------------------------------------------------------------------------
    def update(self):
        self.session.send(self.id, self.render(), "init-content")
        self.session.flush_message_queue()

    # VALUE -----------------------------------------------------------------------------------------
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self.send_value(value)

    def send_value(self, value):
        self.session.send(self.id, value, "change"+self.value_name)

    def set_value(self, value):
        self.value = value

    # SCRIPT PROPERTIES -----------------------------------------------------------------------------
    def add_header_item(self, id, item):
        header_items = self.session.index.header_items
        if id not in header_items:
            header_items[id] = item

    # def add_script_source(self, id, script):
    #     script_sources = self.session.index.script_sources
    #     if id in scripts:
    #         return
    #     script_sources[id] = script

    # def add_script(self, id, script):
    #     if id in scripts:
    #         return
    #     scripts[id] = script

    # def add_css(self, id, style):
    #     if id in styles:
    #         return
    #     styles[id] = style

    # RUNTIME JAVASCRIPT -------------------------------------------------------------------------------  
    def toggle_class(self, class_name):
        self.session.send(self.id, class_name, "toggle-class")

    def add_class(self, class_name):
        self.session.send(self.id, class_name, "add-class")

    def remove_class(self, class_name):
        self.session.send(self.id, class_name, "remove-class")

    def set_attr(self, attr_name, attr_value):
        self.session.send(self.id, attr_value, "change-"+attr_name)

    def set_style(self, attr_name, attr_value):
        self.session.send(self.id, attr_value, "set-"+attr_name)

    def focus(self):
        self.session.send(self.id, None, "focus")

    # RENDER -----------------------------------------------------------------------------------------
    def cls(self, class_names):
        if isinstance(class_names, str):
            classes = class_names.split()
            self.classes.extend([cls.strip() for cls in classes])
        return self

    def style(self,style,value):
        self.styles[style] = value
        return self

    # PYTHON EVENTS ----------------------------------------------------------------------------------
    def on(self,event_name,action):
        self.events[event_name] = action
        return self

    # JAVASCRIPT EMIT --------------------------------------------------------------------------------
    def get_client_handler_str(self, event_name):
        return f" on{event_name}='clientEmit(this.id,this.{self.value_name},\"{event_name}\")'"

    # RENDER -----------------------------------------------------------------------------------------
    def render(self):
        str = f"<{self.tag}"
        if self.id is not None:
            str += f" id='{self.id}'"
        class_str = " ".join(self.classes)
        if(len(class_str) > 0):
            str += f" class='{class_str}'"
        if(len(self.styles) > 0):
            style_str = " style='"
            for style_name, style_value in self.styles.items():
                style_str += f" {style_name}:{style_value};"
            str += style_str + "'"
        for attr_name, attr_value in self.attrs.items():
            str += f" {attr_name}='{attr_value}'"
        for event_name, action in self.events.items():
            str += self.get_client_handler_str(event_name)
        if self.has_content:
            str +=">"
            str +=f"{self.value if self.value is not None and self.value_name is not None else ''}"
            for child in self.children:
                str += child.render()
            str += f"</{self.tag}>"
        else:
            if self.value is not None:
                if(self.value_name is not None):
                    str +=f' {self.value_name} ="{self.value}"'
            str += "/>"
        return str