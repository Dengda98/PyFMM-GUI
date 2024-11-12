"""
    :file:     subwidget.py  
    :author:   Zhu Dengda (zhudengda@mail.iggcas.ac.cn)  
    :date:     2024-11

    主图框中绘制走时场的画布

"""

from PyQt5.QtWidgets import QWidget
import matplotlib as mpl
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
import os, sys
from typing import List, Any
import pyfmm


class MatplotlibWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 创建 Figure 和 Canvas
        self.figure, self.axes = plt.subplots(1,1, constrained_layout=True)
        self.axes.set_aspect('equal')
        self.canvas = FigureCanvas(self.figure)

        # 绑定鼠标移动事件
        self.canvas.mpl_connect("motion_notify_event", self.on_mouse_move)
        # 绑定鼠标点击事件
        self.canvas.mpl_connect("button_press_event", self.on_mouse_click)

        # 绘图元素保留
        self.plot_handle = {}
        self.plot_handle['rays'] = []
        self.plot_handle['rcvdots'] = []

        # 其余成员变量
        self.xarr:np.ndarray 
        self.yarr:np.ndarray 
        self.zarr:np.ndarray = np.array([0.0])
        self.TT:np.ndarray
        self.srcloc:List[float]
        self.contour_set:Any
        self.colorbar:Any

    def canvas_redraw(self):
        self.canvas.draw()

    def on_mouse_move(self, event):
        # 检查鼠标是否在坐标轴区域内
        if event.inaxes:
            x, y = event.xdata, event.ydata
            # 在状态栏或其他地方显示坐标
            self.parent().statusBar().showMessage(f"X: {x:.2f}, Y: {y:.2f}")
        else:
            self.parent().statusBar().showMessage("")

    def on_mouse_click(self, event):
        # 检查鼠标是否在坐标轴区域内
        if not event.inaxes or self.TT is None:
            return 
        
        x, y = event.xdata, event.ydata  

        # 如果现在是鼠标选择震源，则需另外处理 
        if self.parent().mouse_choose_source:
            self.parent().clear_rcv()
            self.parent().write_lineEdit_src(x, y)
            self.plot([x,y], self.xarr, self.yarr, self.vel2d)
            return
        
        # 射线追踪
        rcvloc = [x, y, 0]

        travt, rays = pyfmm.raytracing(
            self.TT, [*self.srcloc, 0.0], rcvloc, self.xarr, self.yarr, self.zarr, 0.1)
        rays_hdl, = self.axes.plot(rays[:,0], rays[:,1], c='b', lw=1, ls='--')

        # 在图形上标记点击点
        dots_hdl, = self.axes.plot(x, y, 'ro', markersize=3.0)
        self.axes.set_xlim([self.xarr[0], self.xarr[-1]])
        self.axes.set_ylim([self.yarr[0], self.yarr[-1]])

        self.canvas.draw()

        self.plot_handle['rays'].append(rays_hdl)
        self.plot_handle['rcvdots'].append(dots_hdl)

        self.parent().textBrowser_rcv.append(f"{x:8.4f} {y:8.4f} {travt:6.2f}")

    def plot_velocity(self, xarr, yarr, vel2d):
        self.TT = None

        # 移除旧的 contour 和 clabel
        if hasattr(self, "contour_set"):
            self.contour_set.remove()
            delattr(self, "contour_set")

        pcm = self.axes.pcolorfast(xarr, yarr, vel2d.T, cmap='jet_r')
        self.axes.set_xlim([xarr[0], xarr[-1]])
        self.axes.set_ylim([yarr[0], yarr[-1]])
        if hasattr(self, "colorbar"):
            self.colorbar.remove()
            delattr(self, "colorbar")

        self.colorbar = self.figure.colorbar(pcm, shrink=0.5, pad=0.05)
        self.canvas.draw()


    def plot(self, srcloc, xarr, yarr, vel2d):
        self.srcloc = srcloc
        self.xarr = xarr
        self.yarr = yarr
        self.vel2d = vel2d

        # 慢度场
        slw  = 1.0/vel2d[:,:,None]

        srcloc = [*srcloc, 0.0]

        # FMM解
        self.TT = pyfmm.travel_time_source(
            srcloc,
            self.xarr, self.yarr, self.zarr, slw)
        

        # 移除旧的 contour 和 源点
        if hasattr(self, "contour_set"):
            self.contour_set.remove()
            delattr(self, "contour_set")
        if hasattr(self, "src_dots_hdl"):
            self.src_dots_hdl.remove()
            delattr(self, "src_dots_hdl")

        # 在图形上标记点击点
        self.src_dots_hdl, = self.axes.plot(srcloc[0], srcloc[1], 'ko', markersize=3.0)
        self.contour_set = self.axes.contour(self.xarr, self.yarr, self.TT[:, :, 0].T, levels=20, linewidths=0.5, colors='k')
        self.axes.clabel(self.contour_set)
        self.axes.set_xlim([self.xarr[0], self.xarr[-1]])
        self.axes.set_ylim([self.yarr[0], self.yarr[-1]])

        self.canvas.draw()

