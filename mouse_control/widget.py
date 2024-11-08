import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import FuncFormatter
import asyncio
import config
import controller
from abc import ABC, abstractmethod

class Widget(ABC):

    @abstractmethod
    def __call__(self):
        pass

    @abstractmethod
    def draw(self):
        pass

class NullWidget(Widget):

    def __init__(self, controllers: list, max_history: int = 40):
        pass

    def __call__(self):
        pass

    def draw(self):
        pass

class ActionWidget(Widget):

    def __init__(self, controllers: list, max_history: int = 40):
        self.controllers = controllers

        self.max_history = max(max_history, 3) # needed to ensure correctness later on
        self.history = {controller.name: [] for controller in self.controllers}

        # populate history with minimal possible action values:
        for controller in self.controllers:
            action = int(min([key for key in controller.formatter]))
            self.history[controller.name] = [action] * self.max_history

        self.root = tk.Tk()
        self.root.title("action_plot")

        self.root.geometry("800x600")
        self.root.resizable(True, True)

        self.frame = tk.Frame(self.root)
        self.frame.pack(expand=True, fill=tk.BOTH)

        self.figure, self.axes = plt.subplots(len(self.controllers), 1, figsize=(5, 12))

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.frame)
        self.canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)

    def __call__(self):
        x = np.linspace(0, self.max_history, self.max_history)

        for controller, axis in zip(self.controllers, self.axes):
            signal_values = [key for key in controller.formatter]
            y_min, y_max = min(signal_values), max(signal_values)

            # update history
            current_action = controller.action_values[controller.current_action] if controller.current_action is not None else self.history[controller.name][-1]
            self.history[controller.name] = self.history[controller.name][1:] + [current_action]

            def y_formatter(target, pos):
                closest_key = int(min(signal_values, key=lambda x: abs(x - target)))
                return controller.formatter[closest_key]

            # plot historical actions of each controller
            y = self.history[controller.name]

            axis.clear()
            axis.plot(x, y)
            axis.set_title(f"{controller.name}")
            axis.set_ylim(y_min, y_max)
            axis.set_xticks([])
            axis.set_xticklabels([])

            axis.yaxis.set_major_formatter(FuncFormatter(y_formatter))

        self.canvas.draw()

    def draw(self):
        self.root.update()

# this allows us to update canvas
async def widget_update_loop(widget: Widget):
    widget_update_every = config.Config().get_or("widget_update_every", 0.01)

    try:
        while True:
            await asyncio.sleep(widget_update_every)
            widget.draw()
    except KeyboardInterrupt:
        pass

# this just updates internal data
async def async_update(widget: Widget):
    widget_update_every = config.Config().get_or("widget_update_every", 0.1)
    try:
        while True:
            await asyncio.sleep(widget_update_every)
            widget()
    except KeyboardInterrupt:
        pass
