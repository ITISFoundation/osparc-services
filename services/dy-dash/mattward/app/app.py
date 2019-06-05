# -*- coding: utf-8 -*-
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

import random
# import pandas as pd
# import matplotlib.pyplot as plt
import plotly.graph_objs as go
from plotly import tools

import pandas as pd
import numpy as np

app = dash.Dash(__name__)
app.css.append_css({
	"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
})

osparc_style = {
	'color': '#bfbfbf',
	'backgroundColor': '#202020',
	'gridColor': '#444',
}

three_columns = {
	'display': 'flex'
}
input_output_plots_layout = {
	'flex': 1,
	'min-width': 0
}
controls_layout = {
	'flex': 0,
	'min-width': '220px',
	'color': osparc_style['color'],
	'backgroundColor': osparc_style['backgroundColor']
}

centered_text = {
	'text-align': 'center',
	'color': osparc_style['color'],
	'backgroundColor': osparc_style['backgroundColor']
}

tab_style = {
	'padding': '5px',
	'color': osparc_style['color'],
	'backgroundColor': osparc_style['backgroundColor']
}
options_layout = {
	# 'border': '1px solid',
	# 'border-radius': '5px',
	'margin-top': '50px'
}

hidden = {
	'display': 'none'
}

dcc_input = {
	'color': osparc_style['color'],
	'backgroundColor': osparc_style['gridColor']
}
dcc_input_button = {
	'height': '40px',
	'width': '100%',
	'color': dcc_input['color'],
	'backgroundColor': dcc_input['backgroundColor']
}
dcc_input_label = {
	'width': '120px',
	'float': 'left'
}
dcc_input_number = {
	'height': '30px',
	'width': '100px',
	'color': dcc_input['color'],
	'backgroundColor': dcc_input['backgroundColor']
}
dcc_input_pair = {
	'overflow': 'hidden',
	'margin-top': '2px',
	'margin-bottom': '2px',
	'color': osparc_style['color'],
	'backgroundColor': osparc_style['backgroundColor']
}

app.layout = html.Div(children=[
	html.H1(
		children='MattWard solver',
		style=centered_text
	),

	html.Div([
		# Four input graphs on the left
		html.Div([
			html.H4(
				children='Learned Model Input Parameters',
				style=centered_text
			),

			# Hidden div inside the app that stores the input data
			html.Div(id='input-data', style=hidden),

			dcc.Graph(id='graph-ins')
		], style=input_output_plots_layout),


		# Controls in the middle
		html.Div([
			html.Div(
				children='Minimal description of how the solver works.',
				style=centered_text
			),

			html.Div([
				html.H5('Input options'),
				html.Label('Select a Nerve Profile'),
				dcc.Dropdown(
					id='input-nerve-profile',
					options=[
						{'label': 'Subject 1: Cervical Vagus', 'value': 0},
						{'label': 'Subject 2: Cervical Vagus', 'value': 1},
						{'label': 'Subject 2: Gastric Vagus', 'value': 2}
					],
					value=0,
					style=dcc_input
				),

				html.Label('Plot Options'),
				dcc.Checklist(
					id='input-plot-options',
					options=[
						{'label': 'Plot against Charge-Phase', 'value': 'Plot against Charge-Phase'},
						{'label': 'Plot CNAP versus Time (ms)', 'value': 'Plot CNAP versus Time (ms)'}
					],
					values=['Plot against Charge-Phase']
				),

				html.Button('Load', id='load-input-button', style=dcc_input_button)
			], style=options_layout),

			html.Div([
				html.H5('Sweep Pulse'),
				dcc.Tabs(
					id="sweep-pulse-tabs", 
					value='current',
					children=[
						dcc.Tab(
							label='Current',
							value='current',
							style=tab_style,
							selected_style=tab_style,
							children=[
								html.Div([
									html.Div([
										html.Label('Starting tst (mA):')
									], style=dcc_input_label),
									dcc.Input(
										id='current_in_1',
										type='number',
										value=0,
										style=dcc_input_number
									)
								], style=dcc_input_pair),

								html.Div([
									html.Div([
										html.Label('Ending tst (mA):'),
									], style=dcc_input_label),
									dcc.Input(
										id='current_in_2',
										type='number',
										value=1,
										style=dcc_input_number
									)
								], style=dcc_input_pair),

								html.Div([
									html.Div([
										html.Label('Step Size (mA):')
									], style=dcc_input_label),
									dcc.Input(
										id='current_in_3',
										type='number',
										value=0.01,
										style=dcc_input_number
									)
								], style=dcc_input_pair),

								html.Div([
									html.Div([
										html.Label('Fixed Ist (ms):')
									], style=dcc_input_label),
									dcc.Input(
										id='current_in_4',
										type='number',
										value=0.4,
										style=dcc_input_number
									)
								], style=dcc_input_pair),

								html.Button('Predict CNAPs', id='predict-current-button', style=dcc_input_button),
							]
						),
						dcc.Tab(
							label='Duration',
							value='duration',
							style=tab_style,
							selected_style=tab_style,
							children=[
								html.Div([
									html.Div([
										html.Label('Starting Ist (mA):')
									], style=dcc_input_label),
									dcc.Input(
										id='duration_in_1',
										type='number',
										value=0,
										style=dcc_input_number
									)
								], style=dcc_input_pair),

								html.Div([
									html.Div([
										html.Label('Ending Ist (mA):'),
									], style=dcc_input_label),
									dcc.Input(
										id='duration_in_2',
										type='number',
										value=1,
										style=dcc_input_number
									)
								], style=dcc_input_pair),

								html.Div([
									html.Div([
										html.Label('Step Size (mA):')
									], style=dcc_input_label),
									dcc.Input(
										id='duration_in_3',
										type='number',
										value=0.01,
										style=dcc_input_number
									)
								], style=dcc_input_pair),

								html.Div([
									html.Div([
										html.Label('Fixed tst (ms):')
									], style=dcc_input_label),
									dcc.Input(
										id='duration_in_4',
										type='number',
										value=0.4,
										style=dcc_input_number
									)
								], style=dcc_input_pair),

								html.Button('Predict CNAPs', id='predict-duration-button', style=dcc_input),
							]
						)
					],
				),
				html.Div(id='tabs-content')
			], style=options_layout)
		], style=controls_layout),


		# Two output graphs on the right
		html.Div([
			html.H4(
				id='output-label',
				children='Predicted Compund Nerve Action Potentials',
				style=centered_text
			),
			
			# Hidden div inside the app that stores the output data
			html.Div(id='output-data', style=hidden),

			dcc.Graph(id='graph-out1'),
			dcc.Graph(id='graph-out2')
		], style=input_output_plots_layout),
	], style=three_columns)
], style=osparc_style)


def create_learned_model_input(path, plot_vs_tcnap):
	column_names = ['t_ms', 'CV', 'Vmax','M_mod', 'B_mod', 'tauSD']
	data = pd.read_csv(path, sep=',', names=column_names)

	# dpi = 96
	# height = 1024
	# width = 1024
	# fontsize = 16
	# plt.figure(figsize=(width / dpi, height / dpi), dpi=dpi)

	x_axis = data.CV
	if plot_vs_tcnap:
		x_axis = data.t_ms

	return {
		"plot_vs_tcnap": plot_vs_tcnap,
		"x_axis": x_axis,
		"y_axis": {
			"Vmax": [i*-1e12 for i in data.Vmax],
			"M_mod": data.M_mod,
			"B_mod": data.B_mod,
			"tauSD": data.tauSD,
		}
	}

# When pressing 'Load' this callback will be triggered.
# Also, its output will trigger the rebuilding of the four input graphs.
@app.callback(
	Output('input-data', 'children'),
	[Input('load-input-button', 'n_clicks')],
	state=[
		State(component_id='input-nerve-profile', component_property='value'),
		State(component_id='input-plot-options', component_property='values')
	]
)
def read_input_file(n_clicks, input_nerve_profile, input_plot_options):
	# TODO: MaG
	# print("Load clicked.", nerve_profile.value)
	# model_id = nerve_profile.index + 1
	# !execute_cnap.sh $model_id 0 0.0 1.0 0.5 0.4
	# path = '/home/jovyan/outputs/input.csv'
	path = 'input.csv'
	return create_learned_model_input(path, input_plot_options)


@app.callback(
	Output('graph-ins', 'figure'),
	[Input('input-data', 'children')]
)
def build_input_graphs(data):
	marker_size = 2
	line_width = 1
	plot_vs_tcnap = data["plot_vs_tcnap"]
	trace1 = go.Scatter(
		x=data["x_axis"],
		y=data["y_axis"]["Vmax"],
		mode='lines+markers',
		marker = dict(
			size = marker_size
		),
		line = dict(
			width = line_width
		)
	)
	trace2 = go.Scatter(
		x=data["x_axis"],
		y=data["y_axis"]["M_mod"],
		mode='lines+markers',
		marker = dict(
			size = marker_size
		),
		line = dict(
			width = line_width
		)
	)
	trace3 = go.Scatter(
		x=data["x_axis"],
		y=data["y_axis"]["B_mod"],
		mode='lines+markers',
		marker = dict(
			size = marker_size
		),
		line = dict(
			width = line_width
		)
	)
	trace4 = go.Scatter(
		x=data["x_axis"],
		y=data["y_axis"]["tauSD"],
		mode='lines+markers',
		marker = dict(
			size = marker_size
		),
		line = dict(
			width = line_width
		)
	)
	fig = tools.make_subplots(rows=4,
														cols=1,
														# specs=[[{}], [{}], [{}], [{}]],
														shared_xaxes=True,
														# shared_yaxes=True,
														vertical_spacing=0.05
	)
	fig.append_trace(trace1, 1, 1)
	fig.append_trace(trace2, 2, 1)
	fig.append_trace(trace3, 3, 1)
	fig.append_trace(trace4, 4, 1)

	if (plot_vs_tcnap):
		fig['layout']['xaxis'].update(
			range=[0, max(data["x_axis"])]
		)
	else:
		fig['layout']['xaxis'].update(
			range=[min(data.CV), 100],
			type='log'
		)

	fig['layout']['xaxis'].update(
		title='Conduction Velocity (m/s)',
		gridcolor=osparc_style['gridColor']
	)
	fig['layout']['yaxis'].update(
		title='Vmax(uV)',
		gridcolor=osparc_style['gridColor']
	)
	fig['layout']['yaxis2'].update(
		title='M coeff',
		gridcolor=osparc_style['gridColor']
	)
	fig['layout']['yaxis3'].update(
		title='B coeff (mA)',
		gridcolor=osparc_style['gridColor']
	)
	fig['layout']['yaxis4'].update(
		title='tau_SD(ms)',
		gridcolor=osparc_style['gridColor']
	)
	margin = 10
	y_label_padding = 50
	x_label_padding = 30
	fig['layout']['margin'].update(
		l=margin+y_label_padding,
		r=margin,
		b=margin+x_label_padding,
		t=margin,
	)
	fig['layout'].update(
		autosize=True,
		height=800,
		# title='Learned Model Input Parameters',
		showlegend=False,
		plot_bgcolor=osparc_style['backgroundColor'],
		paper_bgcolor=osparc_style['backgroundColor'],
		font=dict(
			color=osparc_style['color']
		)
	)
	return fig


def predict_current(in1, in2, in3, in4):
	print('current', in1, in2, in3, in4)
	return {
		"3d_data": {
			"x_axis": [random.randint(1,10), random.randint(1,10), random.randint(1,10), random.randint(1,10)],
			"y_axis": [random.randint(1,10), random.randint(1,10), random.randint(1,10), random.randint(1,10)],
			"z_axis": [random.randint(1,10), random.randint(1,10), random.randint(1,10), random.randint(1,10)],
		},
		"histogram": {
			"x_axis": [random.randint(1,10), random.randint(1,10), random.randint(1,10), random.randint(1,10)],
			"y_axis": [random.randint(1,10), random.randint(1,10), random.randint(1,10), random.randint(1,10)],
			"z_axis": [random.randint(1,10), random.randint(1,10), random.randint(1,10), random.randint(1,10)],
		}
	}

def predict_duration(in1, in2, in3, in4):
	print('duration', in1, in2, in3, in4)
	return {
		"3d_data": {
			"x_axis": [random.randint(1,10), random.randint(1,10), random.randint(1,10), random.randint(1,10)],
			"y_axis": [random.randint(1,10), random.randint(1,10), random.randint(1,10), random.randint(1,10)],
			"z_axis": [random.randint(1,10), random.randint(1,10), random.randint(1,10), random.randint(1,10)],
		},
		"histogram": {
			"x_axis": [random.randint(1,10), random.randint(1,10), random.randint(1,10), random.randint(1,10)],
			"y_axis": [random.randint(1,10), random.randint(1,10), random.randint(1,10), random.randint(1,10)],
			"z_axis": [random.randint(1,10), random.randint(1,10), random.randint(1,10), random.randint(1,10)],
		}
	}

# When pressing 'Predict' this callback will be triggered.
# Also, its output will trigger the rebuilding of the four input graphs.
@app.callback(
	Output('output-label', 'children'),
	[
		Input('predict-current-button', 'n_clicks_timestamp'),
		Input('predict-duration-button', 'n_clicks_timestamp')
	]
)
def update_output_label(button_current_ts, button_duration_ts):
	if button_current_ts is None:
		button_current_ts = 0
	if button_duration_ts is None:
		button_duration_ts = 0

	base_text = 'Predicted Compund Nerve Action Potentials'
	if button_current_ts<button_duration_ts:
		return base_text + ' (Duration)'
	else:
		return base_text + ' (Current)'


@app.callback(
	Output('output-data', 'children'),
	[
		Input('predict-current-button', 'n_clicks_timestamp'),
		Input('predict-duration-button', 'n_clicks_timestamp')
	],
	state=[
		State(component_id='current_in_1', component_property='value'),
		State(component_id='current_in_2', component_property='value'),
		State(component_id='current_in_3', component_property='value'),
		State(component_id='current_in_4', component_property='value'),
		State(component_id='duration_in_1', component_property='value'),
		State(component_id='duration_in_2', component_property='value'),
		State(component_id='duration_in_3', component_property='value'),
		State(component_id='duration_in_4', component_property='value')
	]
)
def predict(
	button_current_ts, button_duration_ts,
	current_1, current_2, current_3, current_4,
	duration_1, duration_2, duration_3, duration_4):
	if button_current_ts is None:
		button_current_ts = 0
	if button_duration_ts is None:
		button_duration_ts = 0

	if button_current_ts>button_duration_ts:
		model_id = nerve_profile.index + 1
		# sweep_param = 1
		# with out2:
		# 	print("Current clicked.", charge_phase_cb.value, time_cb.value, start_ist.value, end_ist.value, step_size_current.value, fixed_tst.value)
		# 	!execute_cnap.sh $model_id $sweep_param $start_ist.value $end_ist.value $step_size_current.value $fixed_tst.value
		# 	cv_path='/home/jovyan/outputs/CV_plot.csv'
		# 	t_path='/home/jovyan/outputs/t_plot.csv'
		# 	ist_path='/home/jovyan/outputs/Ist_plot.csv'
		# 	tst_path='/home/jovyan/outputs/tst_plot.csv'
		# 	qst_path='/home/jovyan/outputs/CAP_plot.csv'
		# 	vpred_path='/home/jovyan/outputs/V_pred_plot.csv'
		# 	lpred_path='/home/jovyan/outputs/Lpred_plot.csv'
		# 	create_predicted_compound_nerve_action(cv_path=cv_path, t_path=t_path, ist_path=ist_path, tst_path=tst_path, qst_path=qst_path, vpred_path=vpred_path, lpred_path=lpred_path, fixed_tst=True, plot_vs_qst=charge_phase_cb.value, plot_vs_tCNAP=time_cb.value), 
		return predict_current(current_1, current_2, current_3, current_4)
	else:
		return predict_duration(duration_1, duration_2, duration_3, duration_4)


@app.callback(
	Output('graph-out1', 'figure'),
	[Input('output-data', 'children')]
)
def build_graph_out_1(data):
	x = np.linspace(-5, 5, 50)
	y = np.linspace(-5, 5, 50)
	xGrid, yGrid = np.meshgrid(y, x)
	R = np.sqrt(xGrid ** 2 + yGrid ** 2)
	z = np.sin(R)

	# Creating the plot
	lines = []
	line_marker = dict(color='#0066FF', width=2)
	for i, j, k in zip(xGrid, yGrid, z):
		lines.append(go.Scatter3d(x=i, y=j, z=k, mode='lines', line=line_marker))

	margin = 10
	label_padding = 30
	layout = go.Layout(
		# title='Wireframe Plot',
		scene=dict(
			xaxis=dict(
				title='CV (m/s)',
				gridcolor=osparc_style['gridColor'],
				zerolinecolor='rgb(255, 255, 255)',
				showbackground=True,
				backgroundcolor=osparc_style['backgroundColor']
			),
			yaxis=dict(
				title='I_st (mA)',
				gridcolor=osparc_style['gridColor'],
				zerolinecolor='rgb(255, 255, 255)',
				showbackground=True,
				backgroundcolor=osparc_style['backgroundColor']
			),
			zaxis=dict(
				title='V_pred (uV)',
				gridcolor=osparc_style['gridColor'],
				zerolinecolor='rgb(255, 255, 255)',
				showbackground=True,
				backgroundcolor=osparc_style['backgroundColor']
			)
		),
		showlegend=False,
		margin=dict(
			l=margin+label_padding,
			r=margin,
			b=margin,
			t=margin
		),
		height=400,
		plot_bgcolor=osparc_style['backgroundColor'],
		paper_bgcolor=osparc_style['backgroundColor'],
		font=dict(
			color=osparc_style['color']
		)
	)

	return {
		'data': lines,
		'layout': layout
	}


@app.callback(
	Output('graph-out2', 'figure'),
	[Input('output-data', 'children')]
)
def build_graph_out_2(data):
	data = go.Heatmap(z=[data["histogram"]["x_axis"],
											data["histogram"]["y_axis"],
											data["histogram"]["z_axis"]])

	margin = 10
	label_padding = 30
	layout = go.Layout(
		# title='Heatmap Plot',
		margin=dict(
			l=margin+label_padding,
			r=margin,
			b=margin+label_padding,
			t=margin
		),
		height=400,
		plot_bgcolor=osparc_style['backgroundColor'],
		paper_bgcolor=osparc_style['backgroundColor'],
		font=dict(
			color=osparc_style['color']
		)
	)

	return {
		'data': [data],
		'layout': layout
	}


if __name__ == '__main__':
	app.run_server(debug=True, port=8051)