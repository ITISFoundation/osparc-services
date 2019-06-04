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

tabs_styles = {
	'height': '44px',
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
	'margin-top': '20px'
}

hidden = {
	'display': 'none'
}

dcc_input_label = {
	'width': '120px',
	'float': 'left'
}
dcc_input = {
	'color': osparc_style['color'],
	'backgroundColor': osparc_style['gridColor']
}
dcc_input_number = {
	'height': '30px',
	'width': '100px',
	'color': dcc_input['color'],
	'backgroundColor': dcc_input['backgroundColor']
}
dcc_input_pair = {
	'overflow': 'hidden',
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
						{'label': 'Subject 1: Cervical Vagus', 'value': 'Subject 1: Cervical Vagus'},
						{'label': 'Subject 2: Cervical Vagus', 'value': 'Subject 2: Cervical Vagus'},
						{'label': 'Subject 2: Gastric Vagus', 'value': 'Subject 2: Gastric Vagus'}
					],
					value='Subject 1: Cervical Vagus',
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

				html.Button('Load', id='load-input-button', style=dcc_input)
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
										html.Label('Ending tst  (mA):'),
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

								html.Button('Predict CNAPs', id='predict-current-button', style=dcc_input),
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
	# column_names = ['t_ms', 'CV', 'Vmax','M_mod', 'B_mod', 'tauSD']
	# data = pd.read_csv(path, sep=',', names=column_names)
	# return [random.randint(1,10), random.randint(1,10), random.randint(1,10)]
	return {
		"x_axis": [1, 2, 3, 4],
		"y_axis": {
			"Vmax": [random.randint(1,10), random.randint(1,10), random.randint(1,10), random.randint(1,10)],
			"M_mod": [random.randint(1,10), random.randint(1,10), random.randint(1,10), random.randint(1,10)],
			"B_mod": [random.randint(1,10), random.randint(1,10), random.randint(1,10), random.randint(1,10)],
			"tauSD": [random.randint(1,10), random.randint(1,10), random.randint(1,10), random.randint(1,10)],
		}
	}

@app.callback(
	Output('graph-ins', 'figure'),
	[Input('input-data', 'children')]
)
def build_input_graphs(data):
	trace1 = go.Scatter(
		x=data["x_axis"],
		y=data["y_axis"]["Vmax"],
		mode='lines+markers'
	)
	trace2 = go.Scatter(
		x=data["x_axis"],
		y=data["y_axis"]["M_mod"],
		mode='lines+markers'
	)
	trace3 = go.Scatter(
		x=data["x_axis"],
		y=data["y_axis"]["B_mod"],
		mode='lines+markers'
	)
	trace4 = go.Scatter(
		x=data["x_axis"],
		y=data["y_axis"]["tauSD"],
		mode='lines+markers'
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
	fig['layout']['xaxis'].update(
		title='Time (ms)',
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
	label_padding = 30
	fig['layout']['margin'].update(
		l=margin+label_padding,
		r=margin,
		b=margin+label_padding,
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


# When pressing 'Predict' this callback will be triggered.
# Also, its output will trigger the rebuilding of the four input graphs.
@app.callback(
	Output('output-data', 'children'),
	[Input('predict-current-button', 'n_clicks')],
	state=[
		State(component_id='current_in_1', component_property='value'),
		State(component_id='current_in_2', component_property='value'),
		State(component_id='current_in_3', component_property='value'),
		State(component_id='current_in_4', component_property='value')
	]
)
def predict_current(n_clicks, in1, in2, in3, in4):
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

'''
# When pressing 'Predict_duration' this callback will be triggered.
# Also, its output will trigger the rebuilding of the four input graphs.
@app.callback(
	Output('output-data', 'children'),
	[Input('predict-duration-button', 'n_clicks')],
	state=[
		State(component_id='pulse_in_1', component_property='value'),
		State(component_id='pulse_in_2', component_property='value'),
		State(component_id='pulse_in_3', component_property='value'),
		State(component_id='pulse_in_4', component_property='value')
	]
)
def predict_duration(n_clicks, in1, in2, in3, in4):
	return {
		"3d_data": {
			"x_axis": [1, 2, 3, 4],
			"y_axis": [random.randint(1,10), random.randint(1,10), random.randint(1,10), random.randint(1,10)],
			"z_axis": [random.randint(1,10), random.randint(1,10), random.randint(1,10), random.randint(1,10)],
		},
		"histogram": {
			"x_axis": [1, 2, 3, 4],
			"y_axis": [random.randint(1,10), random.randint(1,10), random.randint(1,10), random.randint(1,10)],
		}
	}
'''
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