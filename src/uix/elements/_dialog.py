import uix
from ..core.element import Element
print("Imported: dialog")

uix.html.add_script("dialog", beforeMain = False, script =
'''
    event_handlers["dialog-open"] = function(id, value, event_name){
        isClickableAnywhere = value;
        const dialog = document.getElementById(id);
        const closeButton = dialog.querySelector("button");
        
        dialog.showModal();

        closeButton.addEventListener("click", function() {
            dialog.close();
        });
        
        if (isClickableAnywhere) {
            window.onclick = function(event) {
                if (event.target === dialog) {
                    dialog.close();
                }
            };
        }
        
    }
''')

uix.html.add_css("dialog_css", style = '''
dialog {
    background: var(--background);
    color:white;
    border-radius: 3px;
    border:1px solid gray;
}
        
::backdrop {
  background: black;
  opacity: 0.3;
}''')

class dialog(Element):
    def __init__(self,value = None,id = None, is_clickable_anywhere = True):
        super().__init__(value, id = id)
        self.tag = "dialog"
        self.has_content = True
        self.is_clickable_anywhere = is_clickable_anywhere

    def open(self):
        self.session.send(self.id, self.is_clickable_anywhere, "dialog-open")
        return self
        
        

title = "Dialog"

description = '''
# dialog(value,id = None, is_clickable_anywhere = True)

1. Dialog elementi. Bir dialog penceresi açar.

    | attr                  | desc                                              |
    | :-------------------- | :------------------------------------------------ |
    | id                    | Dialog elementinin id'si                          |
    | value                 | Dialog elementinin içeriği                       |
    | is_clickable_anywhere | Dialog elementinin dışına tıklandığında kapanıp kapanmayacağı |
'''

sample = """
def dialog_example1():
    with dialog(id="dialog_example",is_clickable_anywhere=True) as dialog1:
        with container("",):
            text("Dialog Example 1")
            text("Click anywhere to close")
        button("Close")
    button("Dialog 1").on("click", lambda ctx, id, value: dialog.open(dialog1))
    return dialog1

def dialog_example2():
    with dialog(id="dialog1", is_clickable_anywhere=False) as dialog2:
        with container("",):
            text("Dialog Example 2")
            text("Click the close button to close")
        button("Close")
    button("Dialog 2").on("click", lambda ctx, id, value: dialog.open(dialog2))
    return dialog2

def dialog_example():
    dialog_example1()
    dialog_example2()
"""