import carb
import omni.ext
import omni.ui as ui
import keyboard
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
                self._label = ui.Label("")

        success = spacenavigator.open()
        if success:
            while 1:
                state = spacenavigator.read()
                msg = f"{state.x}, {state.y}, {state.z}"
                carb.log_warn(msg)
                self._label.text = msg
                time.sleep(0.5)
        else:
            msg = "No spacemouse detected"
            carb.log_warn(msg)
            self._label.text = msg

    def on_shutdown(self):
        print("[robotica.io.spacemouse] robotica io spacemouse shutdown")
