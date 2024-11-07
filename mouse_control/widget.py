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

    def __init__(self, sensors: list, max_history: int = 40):
        pass

    def __call__(self):
        pass

    def draw(self):
        pass

class ActionWidget(Widget):

    def __init__(self, sensors: list, max_history: int = 40):
        self.sensors = sensors
        self.max_history = max_history

        self.root = tk.Tk()
        self.root.title("action_plot")

        self.root.geometry("800x600")
        self.root.resizable(True, True)

        self.frame = tk.Frame(self.root)
        self.frame.pack(expand=True, fill=tk.BOTH)

        self.figure, self.axes = plt.subplots(3, 1, figsize=(5, 12))

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.frame)
        self.canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)

    def __call__(self):
        x = np.linspace(0, 10, 100)

        def y_formatter(x, pos):
            if x == 0.0:
                return 'Low'
            elif x == 0.5:
                return 'Medium'
            elif x == 1.0:
                return 'High'
            else:
                return ''

        for index, axis in enumerate(self.axes):
            y = np.random.random(100)
            y_min, y_max = 0, 1

            axis.clear()
            axis.plot(x, y)
            axis.set_title(f"Controller: {index}")
            axis.set_ylim(y_min, y_max)
            axis.set_xticks([])
            axis.set_xticklabels([])

            axis.yaxis.set_major_formatter(FuncFormatter(y_formatter))

        self.canvas.draw()

    def draw(self):
        self.root.update()

# this allows us to update canvas
async def widget_update_loop(widget: Widget):
    widget_update_every = config.Config().get_or("widget_update_every", 0.1)

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
