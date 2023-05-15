# import asyncio
# import carb
from datetime import datetime, timedelta
import omni.ext
import omni.ui.scene
import omni.ui as ui
import omni.usd
import omni.kit.viewport.window
import omni.kit.app
import omni.kit.viewport
import omni.kit.viewport.utility as vp_utility
# from omni.kit.viewport.utility.legacy_viewport_api import LegacyViewportAPI
# from omni.kit.viewport.utility.legacy_viewport_window import LegacyViewportWindow
from omni.kit.manipulator.camera import ViewportCameraManipulator
from omni.kit.manipulator.camera.model import CameraManipulatorModel
# import omni.kit.property.camera
from pxr import UsdGeom, Gf
import platform
if platform.system() == 'Windows':
    omni.kit.pipapi.install("pywinusb")
# import pywinusb
import spacenavigator
import time

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

                with ui.HStack():
                    ui.Button("Move", clicked_fn=lambda: self.on_click)

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

    def on_click(self, _):
        self.update_state({"t": 255.0, "x": 30.0, "y": 30.0, "z": 30.0, "roll": 0.0, "pitch": 0.0, "yaw": 0.0, "buttons": [0,0]})

    def on_spacemouse(self, state: spacenavigator.SpaceNavigator):
        current_time = datetime.now()
        if self.previous_time:
            if current_time - self.previous_time < timedelta(milliseconds=UPDATE_TIME_MILLIS):
                return
            
        self.previous_time = current_time
        self.update_state(state)

    def on_spacemouse_buttons(self, state: spacenavigator.SpaceNavigator, buttons: spacenavigator.ButtonState):
        self.update_state(state)

    def get_projection_matrix(self, fov, aspect_ratio, z_near, z_far):
        """
        Calculate the camera projection matrix.

        Args:
            fov (float): Field of View (in radians)
            aspect_ratio (float): Image aspect ratio (Width / Height)
            z_near (float): distance to near clipping plane
            z_far (float): distance to far clipping plane

        Returns:
            (numpy.ndarray): View projection matrix with shape `(4, 4)`
        """
        import math
        import numpy as np
        a = -1.0 / math.tan(fov / 2)
        b = -a * aspect_ratio
        c = z_far / (z_far - z_near)
        d = z_near * z_far / (z_far - z_near)
        return np.array([[a, 0.0, 0.0, 0.0], [0.0, b, 0.0, 0.0], [0.0, 0.0, c, 1.0], [0.0, 0.0, d, 0.0]])

    def gfmatrix_to_matrix44(self, matrix: Gf.Matrix4d) -> omni.ui.scene.Matrix44:
        """
        A helper method to convert Gf.Matrix4d to omni.ui.scene.Matrix44

        Args:
            matrix (Gf.Matrix): Input matrix

        Returns:
            UsdGeom.Matrix4d: Output matrix
        """
        matrix44 = omni.ui.scene.Matrix44(
            matrix[0][0], matrix[0][1], matrix[0][2], matrix[0][3],
            matrix[1][0], matrix[1][1], matrix[1][2], matrix[1][3],
            matrix[2][0], matrix[2][1], matrix[2][2], matrix[2][3],
            matrix[3][0], matrix[3][1], matrix[3][2], matrix[3][3]
        )
        return matrix44
    
    def gfmatrix_to_array(self, matrix: Gf.Matrix4d) -> list:
        """
        A helper method to convert Gf.Matrix4d to omni.ui.scene.Matrix44

        Args:
            matrix (Gf.Matrix): Input matrix

        Returns:
            UsdGeom.Matrix4d: Output matrix
        """
        return (
            matrix[0][0], matrix[0][1], matrix[0][2], matrix[0][3],
            matrix[1][0], matrix[1][1], matrix[1][2], matrix[1][3],
            matrix[2][0], matrix[2][1], matrix[2][2], matrix[2][3],
            matrix[3][0], matrix[3][1], matrix[3][2], matrix[3][3]
        )

    def update_state(self, state: spacenavigator.SpaceNavigator):
        msg = f"{state.x:.03f}, {state.y:.03f}, {state.z:.03f}"
        msg2 = f"roll: {state.roll:.03f}, pitch: {state.pitch:.03f}, yaw: {state.yaw:.03f}"
        # Note1: The number of buttons varies with the type of 3DConnexion product we have
        # Note2: The mappings of buttons is user-configurable so not guaranteed order - we have to account for this
        buttons = f"buttons: {state.buttons}"
        self._label_msg.text = msg
        self._label_msg2.text = msg2
        self._label_buttons.text = buttons
        self._label_connected.text = f"{state.t}"

        ctx = omni.usd.get_context()
        stage = ctx.get_stage()
        root_layer = stage.GetRootLayer()
        scene_root_prim = stage.GetPrimAtPath(root_layer.defaultPrim)
        scene = UsdGeom.Xform(scene_root_prim)

        vp_window = omni.kit.viewport.window.ViewportWindow.active_window
        viewport_api = vp_window.viewport_api

        # active_camera_path = viewport_api.get_active_camera()
        active_viewport = vp_utility.get_active_viewport()
        if active_viewport:
            time = active_viewport.time
            active_camera_path = active_viewport.camera_path

        active_camera: UsdGeom.Camera = stage.GetPrimAtPath(active_camera_path)
        active_camera_xform = UsdGeom.Xformable(active_camera)

        model = CameraManipulatorModel()

        projection = self.gfmatrix_to_array(active_camera_xform.GetLocalTransformation())

        model.set_floats('projection', values=projection)

        sceneview = omni.ui.scene.SceneView(model=model, projection=projection)
        model.set_floats('projection', values=projection)

        with sceneview.scene:
            camera_manip = ViewportCameraManipulator(viewport_api)
            camera_manip.model.set_floats('projection', values=projection)

            sceneview.model = camera_manip.model


            if (
                state.x != 0
                or state.y != 0
                or state.z != 0
            ):

                sceneview.model.set_ints('disable_pan', [0])
                sceneview.model.set_ints('disable_fly', [0])

                pan_speed_x = 0.5
                pan_speed_y = 0.5
                zoom_speed_z = 0.5
                sceneview.model.set_floats('world_speed', [pan_speed_x, pan_speed_y, zoom_speed_z])

                fly_speed = 1.0
                sceneview.model.set_floats('fly_speed', [fly_speed])

                sceneview.model.set_floats('move', [30.0, 0.0, 0.0])
                sceneview.model.set_floats('fly', [1000.0, 0.0, 0.0])
            


    def on_shutdown(self):
        if self._nav1:
            self._nav1.close()
            self._nav1.callback = None
            self._nav1.button_callback = None
        if self._nav2:
            self._nav2.close()
            self._nav2.callback = None
            self._nav2.button_callback = None
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
