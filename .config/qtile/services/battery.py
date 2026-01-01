from libqtile import widget

def get_battery_info():
    try:
        with open("/sys/class/power_supply/BAT1/capacity") as f:
            battery_percentage = f.read().strip()

        with open("/sys/class/power_supply/ACAD/online") as f:
            charger_status = f.read().strip()

        charger_icon = "󰚥" if charger_status == "1" else ""
        return f"{battery_percentage} {charger_icon}"

    except Exception:
        return " N/A"


class BatteryWidget(widget.base.InLoopPollText):
    defaults = [
        ("update_interval", 1, "Update interval in seconds"),
    ]

    def __init__(self, **config):
        super().__init__(**config)
        self.add_defaults(BatteryWidget.defaults)

    def poll(self):
        return get_battery_info()