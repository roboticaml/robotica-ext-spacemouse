import carb
from datetime import datetime, timedelta
import omni.ext
import omni.ui as ui
import keyboard
import mouse
import platform
if platform.system() == 'Windows':
    omni.kit.pipapi.install("pywinusb")
# import pywinusb
import spacenavigator

UPDATE_TIME_MILLIS = 100


class RoboticaIoSpacemouseExtension(omni.ext.IExt):
    def __init__(self):
        self._count = 0
        self.previous_time = None

    def on_startup(self, ext_id):
        print("[robotica.io.spacemouse] robotica io spacemouse startup")

        self._window = ui.Window("Spacemouse debug", width=300, height=300)
        with self._window.frame:
            with ui.VStack():
                self._label_msg = ui.Label("")
                self._label_msg2 = ui.Label("")
                self._label_buttons = ui.Label("")
                self._label_connected = ui.Label("")

        # Note1: It is possible to have multiple 3D mice connected.
        # See: https://github.com/johnhw/pyspacenavigator/blob/master/spacenavigator.py

        self._nav1 = spacenavigator.open(callback=self.on_spacemouse,button_callback=self.on_spacemouse_buttons, DeviceNumber=0)
        self._nav2 = spacenavigator.open(callback=self.on_spacemouse,button_callback=self.on_spacemouse_buttons, DeviceNumber=1)

        if self._nav1 or self._nav2:
            if self._nav1.connected or self._nav2.connected:
                self._label_connected.text = "Connected"
            else:
                self._label_connected.text = "Not Connected"
        else:
            self._label_connected.text = "No spacemouse detected"

    def on_spacemouse(self, state: spacenavigator):
        current_time = datetime.now()
        if self.previous_time:
            if current_time - self.previous_time < timedelta(milliseconds=UPDATE_TIME_MILLIS):
                return
            
        self.previous_time = current_time
        return self.update_state(state)

    def on_spacemouse_buttons(self, state: spacenavigator, buttons: spacenavigator.ButtonState):
        return self.update_state(state)

    def update_state(self, state: spacenavigator):
        msg = f"{state.x:.03f}, {state.y:.03f}, {state.z:.03f}"
        msg2 = f"roll: {state.roll:.03f}, pitch: {state.pitch:.03f}, yaw: {state.yaw:.03f}"
        # Note1: The number of buttons varies with the type of 3DConnexion product we have
        # Note2: The mappings of buttons is user-configurable so not guaranteed order - we have to account for this
        buttons = f"buttons: {state.buttons}"
        self._label_msg.text = msg
        self._label_msg2.text = msg2
        self._label_buttons.text = buttons
        self._label_connected.text = f"{state.t}"


    def on_shutdown(self):
        if self._nav1:
            self._nav1.close()
        if self._nav2:
            self._nav2.close()
        self._nav1 = None
        self._nav2 = None
        self.previous_time = None
        if self._label_msg:
            self._label_msg.text = ""
        if self._label_msg2:
            self._label_msg2.text = ""
        if self._label_buttons:
            self._label_buttons.text = ""
        if self._label_connected:
            self._label_connected.text = "Not connected"
        print("[robotica.io.spacemouse] robotica io spacemouse shutdown")
