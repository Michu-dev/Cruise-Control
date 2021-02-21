from flask import Flask, render_template, request

from bokeh.client import pull_session
from bokeh.embed import server_session, components
from bokeh.plotting import figure, output_file, show

import math
import random

vs = 0
b = False
app = Flask(__name__)

@app.route('/')
def show_dashboard():
    global vs
    vs = 0
    plot = figure(title="Zaleznosc predkosci od czasu", x_axis_label='t[s]', y_axis_label='v(t)[m/s]', plot_height=300,
                  plot_width=800)
    plot1 = figure(title="Zaleznosc sily ciagu silnika od czasu", x_axis_label='t[s]', y_axis_label='F(t)[kN]',
                   plot_height=300, plot_width=800, margin=(75, 0, 0, 0))
    plot2 = figure(title="Zaleznosc sily oporu powietrza od czasu", x_axis_label='t[s]', y_axis_label='F(t)[kN]',
                   plot_height=300, plot_width=800, margin=(75, 0, 0, 0))
    plot3 = figure(title="Zaleznosc sily spadku (grawitacji) od czasu", x_axis_label='t[s]', y_axis_label='F(t)[kN]',
                   plot_height=300, plot_width=800, margin=(75, 0, 0, 0))
    plot4 = figure(title="Zaleznosc sily wypadkowej od czasu", x_axis_label='t[s]', y_axis_label='F(t)[kN]',
                   plot_height=300, plot_width=800, margin=(80, 0, 0, 0))
    plot5 = figure(title="Zaleznosc odzyskiwanej energii w funkcji czasu", x_axis_label='t[s]', y_axis_label='E(t)[MJ]',
                   plot_height=300, plot_width=800, margin=(75, 0, 0, 0))





    plots = []
    plots.append(components(plot))
    plots.append(components(plot1))
    plots.append(components(plot2))
    plots.append(components(plot3))
    plots.append(components(plot4))
    plots.append(components(plot5))
    return render_template('dashboard.html', plot_width=800, plots=plots)

@app.route('/send', methods=['POST'])
def make_plot():
    global vs, b
    M = 1500
    bw =  0.25
    g = 9.81
    Tp = 0.15
    Ti = 0.05
    Td = 0.05
    kp = 0.0015

    bb = random.random()
    if (bb > 0.5):
        bb = 1
    else:
        bb = -1
    alfa = random.uniform(0, math.pi / 200)

    angle = math.degrees(alfa) * 10

    if not b:
        vp = 0
        b = True
    else:
        vp = vs

    if request.method == 'POST':
        vs = int(request.form['new-speed1'])
        kp = float(request.form['new-kp'])
        Ti = float(request.form['ki'])
        Td = float(request.form['kd'])
    else:
        vs = 0


    a = 0
    Fs = M * g * math.sin(alfa) * bb
    Fo = bw * pow((vs - vp)//2, 2)
    Fd = 0

    Fop = Fo
    tsim = 30
    N = int(tsim / Tp)
    list_n = []
    Kolejne = 0
    Aprev = a
    energy = 0
    Tiii = 10000000
    rand = 0
    for i in range(N):
        list_n.append(Kolejne)
        Kolejne += Tp
    list_h = []
    list_e = []
    list_f = []
    list_fs = []
    list_fo = []
    list_fc = []
    list_h.append(vp)
    for i in range(1, N):
        prev = list_h[i - 1]

        adder = ((((-1) * Fs) + ((-1) * Fo) + Fd) * Tp / M) + prev
        if adder < vs and bb == -1:
            a += (1 + kp) * abs(((adder - prev)) / Tp + (Ti / Tiii * adder) + (Td / Tiii * (adder - prev)))
        elif adder < vs and bb == 1:
            a += (1 + kp/10) * abs(((adder - prev)) / Tp + (Ti / Tiii * adder) + (Td / Tiii * (adder - prev)))
        elif adder > vs + 0.001:
            a -= (1 + kp) * abs(((adder - prev)) / Tp + (Ti / Tiii * adder) + (Td / Tiii * (adder - prev)))
        else:
            a -= abs(((adder - prev)) / Tp + (Ti / Tiii * adder) + (Td / Tiii * (adder - prev)))

        if i < 30:
            rand = rand + random.random()

        #sila wypadkowa
        list_f.append((Fd - Fo - Fs) / 1000)
        list_fs.append(Fs)
        list_fo.append(Fo * (rand + 1))
        list_fc.append(Fd / 1000)
        #energia odzyskiwana
        if adder < prev:
            energy = M * pow((a - Aprev)/Tp, 2) / 2
        else:
            energy = 0

        Fo = bw * pow((adder - prev)//2, 2)
        if Fo < Fop:
            Fo = Fop
        Fd = M * a
        Aprev = a
        list_h.append(adder)
        list_e.append(energy / 1000000)

    plot = figure(title="Zaleznosc predkosci od czasu", x_axis_label='t[s]', y_axis_label='v(t)[m/s]', plot_height=300,
                  plot_width=800)
    plot1 = figure(title="Zaleznosc sily ciagu silnika od czasu", x_axis_label='t[s]', y_axis_label='F(t)[kN]',
                   plot_height=300, plot_width=800, margin=(75, 0, 0, 0))
    plot2 = figure(title="Zaleznosc sily oporu powietrza od czasu", x_axis_label='t[s]', y_axis_label='F(t)[kN]',
                   plot_height=300, plot_width=800, margin=(75, 0, 0, 0))
    plot3 = figure(title="Zaleznosc sily spadku (grawitacji) od czasu", x_axis_label='t[s]', y_axis_label='F(t)[kN]',
                   plot_height=300, plot_width=800, margin=(75, 0, 0, 0))
    plot4 = figure(title="Zaleznosc sily wypadkowej od czasu", x_axis_label='t[s]', y_axis_label='F(t)[kN]',
                   plot_height=300, plot_width=800, margin=(80, 0, 0, 0))
    plot5 = figure(title="Zaleznosc odzyskiwanej energii w funkcji czasu", x_axis_label='t[s]', y_axis_label='E(t)[MJ]',
                   plot_height=300, plot_width=800, margin=(75, 0, 0, 0))
    plot.line(list_n, list_h, line_width=4)
    plot1.line(list_n, list_fc, line_width=4)
    plot2.line(list_n, list_fo, line_width=4)
    plot3.line(list_n, list_fs, line_width=4)
    plot4.line(list_n, list_f, line_width=4)
    plot5.line(list_n, list_e, line_width=4)
    script, div = components(plot)

    if vs == 0:
        return script, div
    else:
        plots = []
        plots.append(components(plot))
        plots.append(components(plot1))
        plots.append(components(plot2))
        plots.append(components(plot3))
        plots.append(components(plot4))
        plots.append(components(plot5))

        return render_template('dashboard.html', plot_width=800, plots=plots, speed=round(list_h[N - 1],2), b=bb, angle=round(angle, 2))



if __name__ == "__main__":
    # HOST = '1.1.1.1'
    app.run(debug = True)