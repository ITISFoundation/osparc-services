# -*- coding: utf-8 -*-
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
	html.H1(
		children='MattWard solver',
		style={'text-align': 'center'}
	),

	html.Div(
		children='Minimal description of how the solver works.',
		style={'textAlign': 'center'}
	),

	html.Div([
		# Four input graphs on the left
		html.Div([
			html.H4('Inputs'),

			dcc.Graph(
				id='graph-in1',
				figure={
					'data': [
						{'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
						{'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
					],
					'layout': {
						'title': 'Graph input 1'
					}
				}
			),

			dcc.Graph(
				id='graph-in2',
				figure={
					'data': [
						{'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
						{'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
					],
					'layout': {
						'title': 'Graph input 2'
					}
				}
			),

			dcc.Graph(
				id='graph-in3',
				figure={
					'data': [
						{'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
						{'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
					],
					'layout': {
						'title': 'Graph input 3'
					}
				}
			),

			dcc.Graph(
				id='graph-in4',
				figure={
					'data': [
						{'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
						{'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
					],
					'layout': {
						'title': 'Graph input 4'
					}
				}
			)
		], style={'width': '38%', 'float': 'left'}),


		# Controls in the middle
		html.Div([
			html.H4('Controls'),

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
					value='Subject 1: Cervical Vagus'
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

				html.Button('Load', id='load-input-button'),
				html.Div(id='output-container-button',
								children='Enter a value and press submit')
			], style={'border': '1px solid', 'border-radius': '5px'}),

			html.Div([
				html.H5('Output options'),
				dcc.Tabs(id="sweep-pulse-tabs", value='current', children=[
					dcc.Tab(label='Sweep Pulse Current', value='current'),
					dcc.Tab(label='Sweep Pulse Duration', value='duration'),
				]),
				html.Div(id='tabs-content')
			], style={'border': '1px solid', 'border-radius': '5px'})
		], style={'width': '24%', 'float': 'left', 'min-width': '410px'}),

		# Two output graphs on the right
		html.Div([
			html.H4('Outputs'),

			dcc.Graph(
				id='graph-out1',
				figure={
					'data': [
						{'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
						{'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
					],
					'layout': {
						'title': 'Graph output 1'
					}
				}
			),

			dcc.Graph(
				id='graph-out2',
				figure={
					'data': [
						{'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
						{'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
					],
					'layout': {
						'title': 'Graph output 2'
					}
				}
			)
		], style={'width': '38%', 'float': 'left'}),
	], style={'margin': '5px 0'})
])


@app.callback(Output('tabs-content', 'children'),
							[Input('sweep-pulse-tabs', 'value')])
def render_content(tab):
	if tab == 'current':
		return html.Div(children=[
			html.Div([
				html.Label('Starting Ist (mA):'),
				dcc.Input(
					placeholder='Enter a value...',
					name='balh',
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
			], style={'float': 'left'})
		])
	else:
		return html.Div([
			html.H3('Duration props')
		])


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


if __name__ == '__main__':
    app.run_server(debug=True, port=8051)