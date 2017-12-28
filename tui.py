from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, \
    Button, TextBox, Widget
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError, NextScene, StopApplication
import data
import sys
import sqlite3

class SettingsView(Frame):
    def __init__(self, screen):
        super(SettingsView, self).__init__(screen,
                                          screen.height,
                                          screen.width,
                                          hover_focus=True,
                                          title="Keys setup",
                                          reduce_cpu=True)
        
        self.data = data.settings
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(Text("token:", "token"))
        layout.add_widget(Text("token_secret:", "token_secret"))
        layout.add_widget(Text("consumer_key:", "consumer_key"))
        layout.add_widget(Text("consumer_secret", "consumer_secret"))
        layout2 = Layout([1, 1])
        self.add_layout(layout2)
        layout2.add_widget(Button("Quit", self._quit), 0)
        layout2.add_widget(Button("Next", self._next), 1)
        self.fix()      

    def _next(self):
        self.save()
        data.cursor.execute('delete from settings')
        data.cursor.execute("insert into settings values("
                            "'{consumer_key}','{consumer_secret}',"
                            "'{token}','{token_secret}')".format(**self.data))
        data.data.commit()
        raise NextScene("Subs")

    @staticmethod
    def _quit():
        raise StopApplication("User pressed quit")

class SubsView(Frame):
    def __init__(self, screen):
        super(SubsView, self).__init__(screen,
                                          screen.height,
                                          screen.width,
                                          hover_focus=True,
                                          title="Subscriptions",
                                          reduce_cpu=True)
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        self.data = dict(
            names = '\n'.join(
                [
                    name[0] for name in
                    data.cursor.execute('select name from tweeples').fetchall()
                ]
            )
        )
        self.loaded = self.data['names'].split('\n')
        layout.add_widget(TextBox(
            Widget.FILL_FRAME, "Current:", "names", as_string=True))
        layout2 = Layout([1, 1])
        self.add_layout(layout2)
        layout2.add_widget(Button("Back", self._back), 0)
        layout2.add_widget(Button("Save", self._save), 1)        
        self.fix()
        
    def _back(self):
        raise NextScene("Main")
    
    def _save(self):
        self.save()
        names = self.data['names'].split('\n')
        if names != self.loaded:
            data.remove_list(
                [item for item in self.loaded if item not in names]
            )
            data.add_list(names)
        raise StopApplication("Finish")
        
def demo(screen, scene):
    scenes = [
        Scene([SettingsView(screen)], -1, name="Main"),
        Scene([SubsView(screen)], -1, name="Subs")
    ]

    screen.play(scenes, stop_on_resize=True, start_scene=scene)

last_scene = None
while True:
    try:
        Screen.wrapper(demo, catch_interrupt=True, arguments=[last_scene])
        sys.exit(0)
    except ResizeScreenError as e:
        last_scene = e.scene