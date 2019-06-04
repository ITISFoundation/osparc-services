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

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

centered_text = {
	'text-align': 'center'
}
tabs_styles = {
	'height': '44px'
}
tab_style = {
	'padding': '5px'
}

tab_selected_style = {
	'padding': '5px'
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
			html.Div(id='input-data', style={'display': 'none'}),

			dcc.Graph(id='graph-ins')
		], style={'width': '42%', 'float': 'left'}),


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
					value='Subject 1: Cervical Vagus'),

				html.Label('Plot Options'),
				dcc.Checklist(
					id='input-plot-options',
					options=[
						{'label': 'Plot against Charge-Phase', 'value': 'Plot against Charge-Phase'},
						{'label': 'Plot CNAP versus Time (ms)', 'value': 'Plot CNAP versus Time (ms)'}
					],
					values=['Plot against Charge-Phase']
				),

				html.Button('Load', id='load-input-button'),
				html.Div(id='output-container-button')
			], style={'border': '1px solid', 'border-radius': '5px', 'margin-bottom': '10px'}),

			html.Div([
				html.H5('Output options'),
				dcc.Tabs(
					id="sweep-pulse-tabs", 
					value='current',
					children=[
						dcc.Tab(
							label='Sweep Pulse Current',
							value='current',
							style=tab_style,
							selected_style=tab_selected_style,
							children=[
								html.Div([
									html.Div([
										html.Label('Starting Ist (mA):')
									], style={'width': '120px', 'float': 'left'}),
									dcc.Input(
										type='number',
										value=0,
										style={'width': '100px'}
									)
								], style={'overflow': 'hidden'}),

								html.Div([
									html.Div([
										html.Label('Ending Ist (mA):'),
									], style={'width': '120px', 'float': 'left'}),
									dcc.Input(
										type='number',
										value=1,
										style={'width': '100px'}
									)
								], style={'overflow': 'hidden'}),

								html.Div([
									html.Div([
										html.Label('Step Size (mA):')
									], style={'width': '120px', 'float': 'left'}),
									dcc.Input(
										type='number',
										value=0.01,
										style={'width': '100px'}
									)
								], style={'overflow': 'hidden'}),

								html.Div([
									html.Div([
										html.Label('Fixed tst (ms):')
									], style={'width': '120px', 'float': 'left'}),
									dcc.Input(
										type='number',
										value=0.4,
										style={'width': '100px'}
									)
								], style={'overflow': 'hidden'}),

								html.Button('Predict CNAPs', id='predict-current-button'),
							]
						),
						dcc.Tab(
							label='Sweep Pulse Duration',
							value='duration',
							style=tab_style,
							selected_style=tab_selected_style,
							children=[
								html.H3('Duration props'),
								html.Button('Predict CNAPs', id='predict-duration-button'),
							]
						)
					],
				),
				html.Div(id='tabs-content')
			], style={'border': '1px solid', 'border-radius': '5px'})
		], style={'width': '15%', 'float': 'left', 'max-width': '340px', 'min-width': '230px'}),


		# Two output graphs on the right
		html.Div([
			html.H4(
				children='Predicted Compund Nerve Action Potentials',
				style=centered_text
			),
			
			# Hidden div inside the app that stores the output data
			html.Div(id='output-data', style={'display': 'none'}),

			dcc.Graph(id='graph-out1'),
			dcc.Graph(id='graph-out2')
		], style={'width': '42%', 'float': 'left'}),
	])
])

# When pressing 'Load' this callback will be triggered.
# Also, its output will trigger the rebuilding of the four input graphs.
@app.callback(
	Output('input-data', 'children'),
	[Input('load-input-button', 'n_clicks')]
)
def read_input_file(n_clicks):
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
	fig['layout']['xaxis'].update(title='Time (ms)')
	fig['layout']['yaxis'].update(title='Vmax(uV)')
	fig['layout']['yaxis2'].update(title='M coeff')
	fig['layout']['yaxis3'].update(title='B coeff (mA)')
	fig['layout']['yaxis4'].update(title='tau_SD(ms)')
	margin = 10
	label_padding = 30
	fig['layout']['margin'].update(
		l=margin+label_padding,
		r=margin,
		b=margin+label_padding,
		t=margin
	)
	fig['layout'].update(height=800,
											# width=600,
											# title='Learned Model Input Parameters'
											showlegend=False
	)
	return fig

@app.callback(
	Output('output-container-button', 'children'),
	[Input('load-input-button', 'n_clicks')],
	state=[
		State(component_id='input-nerve-profile', component_property='value'),
		State(component_id='input-plot-options', component_property='values')
	]
)
def load_input(n_clicks, input_nerve_profile, input_plot_options):
	return 'Input options: {} in1 {} in2'.format(
		input_nerve_profile,
		input_plot_options
	)


# When pressing 'Predict' this callback will be triggered.
# Also, its output will trigger the rebuilding of the four input graphs.
@app.callback(
	Output('output-data', 'children'),
	[Input('predict-current-button', 'n_clicks')]
)
def predict_current(n_clicks):
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
	[Input('predict-duration-button', 'n_clicks')]
)
def predict_duration(n_clicks):
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

	layout = go.Layout(
		title='Wireframe Plot',
		scene=dict(
			xaxis=dict(
				title='CV (m/s)',
				gridcolor='rgb(255, 255, 255)',
				zerolinecolor='rgb(255, 255, 255)',
				showbackground=True,
				backgroundcolor='rgb(230, 230,230)'
			),
			yaxis=dict(
				title='I_st (mA)',
				gridcolor='rgb(255, 255, 255)',
				zerolinecolor='rgb(255, 255, 255)',
				showbackground=True,
				backgroundcolor='rgb(230, 230,230)'
			),
			zaxis=dict(
				title='V_pred (uV)',
				gridcolor='rgb(255, 255, 255)',
				zerolinecolor='rgb(255, 255, 255)',
				showbackground=True,
				backgroundcolor='rgb(230, 230,230)'
			)
		),
		showlegend=False,
	)

	return {
		'layout': layout,
		'data': lines
	}

@app.callback(
	Output('graph-out2', 'figure'),
	[Input('output-data', 'children')]
)
def build_graph_out_2(data):
	return {
		'layout': {
			'title': 'tau_SD(ms)'
		},
		'data': [
			go.Heatmap(z=[data["histogram"]["x_axis"],
										data["histogram"]["y_axis"],
										data["histogram"]["z_axis"]])
		]
	}


if __name__ == '__main__':
	app.run_server(debug=True, port=8051)