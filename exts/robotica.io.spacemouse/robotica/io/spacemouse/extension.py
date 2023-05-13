import carb
import omni.ext
import omni.ui as ui
import keyboard
import mouse
import platform
if platform.system() == 'Windows':
    omni.kit.pipapi.install("pywinusb")
import spacenavigator
import time


# Functions and vars are available to other extension as usual in python: `example.python_ext.some_public_function(x)`
def some_public_function(x: int):
    print("[robotica.io.spacemouse] some_public_function was called with x: ", x)
    return x ** x


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class RoboticaIoSpacemouseExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        print("[robotica.io.spacemouse] robotica io spacemouse startup")

        self._count = 0

        self._window = ui.Window("Spacemouse debug", width=300, height=300)
        with self._window.frame:
            with ui.VStack():
                self._label_msg = ui.Label("")
                self._label_msg2 = ui.Label("")
                self._label_buttons = ui.Label("")
                self._label_connected = ui.Label("")

        # Note1: It is possible to have multiple 3D mice connected.
        # We should use the per-device API rather than the module API
        # if we want to support this.
        # See: https://github.com/johnhw/pyspacenavigator/blob/master/spacenavigator.py

        # Note2: spacenavigator supports a callback method being passed to open().
        # For production, we should use that rather than our while loop and time.sleep()
        success = spacenavigator.open()
        if success:
            if success.connected:
                self._label_connected.text = "Connected"
            else:
                self._label_connected.text = "Not Connected"
            while 1:
                state = spacenavigator.read()
                msg = f"{state.x}, {state.y}, {state.z}"
                msg2 = f"roll: {state.roll}, pitch: {state.pitch}, yaw: {state.yaw}"
                # Note1: The number of buttons varies with the type of 3DConnexion product we have
                # Note2: The mappings of buttons is user-configurable so not guaranteed - we have to account for this
                buttons = f"buttons: {state.button}"
                carb.log_warn(msg)
                self._label_msg.text = msg
                self._label_msg2.text = msg2
                self._label_buttons.text = buttons
                self._label_connected.text = state.t

                if False:
                    key = "ctrl+L"
                    keyboard.press_and_release(key)
                    mouse.click(button=mouse.LEFT)

                time.sleep(0.5)
        else:
            msg = "No spacemouse detected"
            carb.log_warn(msg)
            self._label_connected.text = msg

    def on_shutdown(self):
        print("[robotica.io.spacemouse] robotica io spacemouse shutdown")
