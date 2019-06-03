# -*- coding: utf-8 -*-
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

import random
# import pandas as pd
# import matplotlib.pyplot as plt
import plotly.graph_objs as go

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

	html.Div(
		children='Minimal description of how the solver works.',
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

			dcc.Graph(id='graph-in1'),
			dcc.Graph(id='graph-in2'),
			dcc.Graph(id='graph-in3'),
			dcc.Graph(id='graph-in4')
		], style={'width': '41%', 'float': 'left'}),


		# Controls in the middle
		html.Div([
			html.H4(
				children='Controls',
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
			], style={'border': '1px solid', 'border-radius': '5px'}),

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
									html.Label('Starting Ist (mA):'),
									dcc.Input(
										placeholder='Enter a value...',
										type='number',
										value=0
									)
								], style={'float': 'left'}),

								html.Div([
									html.Label('Ending Ist (mA):'),
									dcc.Input(
										placeholder='Enter a value...',
										type='number',
										value=1
									)
								], style={'float': 'left'}),

								html.Div([
									html.Label('Step Size (mA):'),
									dcc.Input(
										placeholder='Enter a value...',
										type='number',
										value=0.01
									)
								], style={'float': 'left'}),

								html.Div([
									html.Label('Fixed tst (ms):'),
									dcc.Input(
										placeholder='Enter a value...',
										type='number',
										value=0.4
									)
								], style={'float': 'left'}),

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
		], style={'width': '15%', 'float': 'left', 'max-width': '340px', 'min-width': '220px'}),


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
		], style={'width': '41%', 'float': 'left'}),
	], style={'margin': '5px 0'})
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
	Output('graph-in1', 'figure'),
	[Input('input-data', 'children')]
)
def build_graph_1(data):
	return {
		'layout': {
			'title': 'Vmax(uV)'
		},
		'data': [
			go.Scatter(
				x=data["x_axis"],
				y=data["y_axis"]["Vmax"],
				mode='lines+markers'
			)
		]
	}

@app.callback(
	Output('graph-in2', 'figure'),
	[Input('input-data', 'children')]
)
def build_graph_2(data):
	return {
		'layout': {
			'title': 'M coeff'
		},
		'data': [
			go.Scatter(
				x=data["x_axis"],
				y=data["y_axis"]["M_mod"],
				mode='lines+markers'
			)
		]
	}

@app.callback(
	Output('graph-in3', 'figure'),
	[Input('input-data', 'children')]
)
def build_graph_3(data):
	return {
		'layout': {
			'title': 'B coeff (mA)'
		},
		'data': [
			go.Scatter(
				x=data["x_axis"],
				y=data["y_axis"]["B_mod"],
				mode='lines+markers'
			)
		]
	}

@app.callback(
	Output('graph-in4', 'figure'),
	[Input('input-data', 'children')]
)
def build_graph_4(data):
	return {
		'layout': {
			'title': 'tau_SD(ms)'
		},
		'data': [
			go.Scatter(
				x=data["x_axis"],
				y=data["y_axis"]["tauSD"],
				mode='lines+markers'
			)
		]
	}


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
	return {
		'layout': {
			'title': 'tau_SD(ms)'
		},
		'data': [
			go.Scatter(
				x=data["3d_data"]["x_axis"],
				y=data["3d_data"]["y_axis"],
				mode='lines+markers'
			)
		]
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
			go.Scatter(
				x=data["histogram"]["x_axis"],
				y=data["histogram"]["y_axis"],
				mode='lines+markers'
			)
		]
	}



if __name__ == '__main__':
    app.run_server(debug=True, port=8051)