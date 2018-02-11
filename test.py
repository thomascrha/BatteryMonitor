import uinput

with uinput.Device([uinput.KEY_E, uinput.KEY_H,
                    uinput.KEY_L, uinput.KEY_O]) as device:
    device.emit_click(uinput.KEY_H)
    device.emit_click(uinput.KEY_E)
    device.emit_click(uinput.KEY_L)
    device.emit_click(uinput.KEY_L)
    device.emit_click(uinput.KEY_O)
