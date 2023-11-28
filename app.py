import pandas as pd
import dash
import plotly.express as px
from dash import html,dcc
from dash.dependencies import Input,Output

file_path = 'Arranged_data.xlsx'
sheet_names = ['Hotels', 'NGOs', 'Gas', 'NITAs', 'Faith', 'Schools']
data = {sheet_name: pd.read_excel(file_path, sheet_name=sheet_name) for sheet_name in sheet_names}


data_frames = []
# Read data from each sheet and append to the list
for sheet_name in sheet_names:
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    df['Class'] = sheet_name
    data_frames.append(df)
# Concatenate all DataFrames into a single DataFrame
combined_data = pd.concat(data_frames, ignore_index=True)
def combined_graph(data,color_column=None):
    df = data
    fig =px.scatter_mapbox(
        df,
        lat='Latitude',
        lon='Longitude',
        text='Name',
        hover_data=['Class','Name'],
        color=color_column,
        mapbox_style='open-street-map'
    )
    fig.update_traces(hovertemplate='<b>Name:%{customdata[1]}</b>')
    fig.update_traces(
        marker=dict(
            size=10,  # Set the marker size
        )
    )
    return fig


colors = {
    'background': '#111111',
    'text': '#7FDBFF',
    'gray':'#CCCCCC'
}
def make_break(num_breaks):
    br_list = [html.Br()] * num_breaks
    return br_list


def style_drop():
    layout_style = {'width':'98%','margin': '0 auto'}
    return layout_style
def bar_graph(data,color_column=None):
    grouped = data.groupby('Class')['Class'].agg('count').reset_index(name='Count')
    fig = px.bar(grouped,x='Class',y='Count',color=color_column)
    fig.update_traces(texttemplate='%{y}', textposition='outside',showlegend=False)
    fig.update_yaxes(title_text="Count")
    fig.update_xaxes(title_text=None)
    return fig


# Creating a lam object
lam = dash.Dash(__name__)


# Creating the application (lam) layout
lam.layout = html.Div(
    children=[
        # Adding a Title
        html.Div(html.H1('Potential Clients Dashboard'),style={'text-align':'center'}),
        *make_break(1),
        html.Div(
            children=[
                html.Div(children=[
                    html.H3('Selections'),
                    #*make_break(1),
                    dcc.Input(id='location_search',type='text', placeholder='Search by location',style={'width':'94%','margin': '0 auto','height':'30px'}),
                    *make_break(1),
                    html.H4('Business Region'),
                    dcc.Dropdown(id='business_region',style=style_drop()),
                    *make_break(1),
                    html.Button("Download", id="btn-download-txt",style={'width':'94%','margin': '0 auto','height':'35px','vertical-align':"bottom"}),
                    dcc.Download(id="download-text"),
                    ],
                         style={'width':'20%','display':'inline-block','background-color':colors['text'],'height':'600px'}),
                html.Div(children=[
                    html.H3('Location on the map'),
                                        #*make_break(1),
                    html.Div(
                        dcc.Graph(id='location_map',style={'vertical-align':'top',"height":"100%"}),
                        style={'width':'70%',"height":"100%",'display':'inline-block'}
                    ),
                   
                    html.Div(
                        children=[
                            dcc.Graph(id = 'categories',style={'vertical-align':'top',"height":"100%"}),
                        ],
                        style={'width':'30%',"height":"100%",'display':'inline-block'}
                    ),
                   
                    ],
                         style={'width':'80%','display':'inline-block','background-color':colors['gray'],'vertical-align':'top','height':'600px'})
            ],
            style={'text-align':'center', 'display':'inline-block', 'width':'100%'}
        )
    ]
)


# Creating callbacks

# Callback for updating Scatter map and Category bar graph
@lam.callback(
    Output('categories','figure'),
    Output('location_map','figure'),
    Input('location_search','value')
)
def update_output(search_text):
    fig2 = bar_graph(combined_data,color_column=None)
    global data
    # Replace this with your data retrieval logic
    data = combined_data
    fig = combined_graph(combined_data,color_column='Class')
    # Filter data based on search_text (you need to define your own filter logic)
    if search_text:
        data['Area Location'] = data['Area Location'].str.lower()
        data = data[data['Area Location'].astype(str).str.contains(search_text,case=False)]
        fig = combined_graph(data,color_column='Class')
        fig2 = bar_graph(data,color_column=None)
           
    return fig2,fig


# Callback for downloading a CSV file
@lam.callback(
    Output('download-text', 'data'),
    Input('btn-download-txt', 'n_clicks'),
    prevent_initial_call=True
)
def update_download_link(n_clicks):
    if n_clicks:
        #print(combined_data)
        selected = data[['Name','Area Location','Class','Latitude','Longitude']]
        csv_string = selected.to_csv(index=False, encoding='utf-8')
        return {
            'content': csv_string,
            'filename': 'data.csv'
        }
    return ""
       


# Running the server


if __name__=='__main__':
    lam.run_server(debug=True)










"""import pandas as pd
import dash
import plotly.express as px
from dash import html, dcc
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import io
import urllib.parse

# Define the path to the Excel file and sheet names
file_path = 'Arranged_data.xlsx'
sheet_names = ['Hotels', 'NGOs', 'Gas', 'NITAs', 'Faith', 'Schools']

# Read data from each sheet and store it in a dictionary
data = {sheet_name: pd.read_excel(file_path, sheet_name=sheet_name) for sheet_name in sheet_names}

# Create an empty list to store data frames
data_frames = []

# Read data from each sheet, add a 'Class' column, and append to the list
for sheet_name in sheet_names:
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    df['Class'] = sheet_name
    data_frames.append(df)

# Concatenate all DataFrames into a single DataFrame
combined_data = pd.concat(data_frames, ignore_index=True)

# Define a function to create a scatter map
def combined_graph(data):
    df = data
    fig = px.scatter_mapbox(
        df,
        lat='Latitude',
        lon='Longitude',
        text='Name',
        color='Class',
        mapbox_style='open-street-map'
    )
    fig.update_traces(
        marker=dict(
            size=10,  # Set the marker size
        )
    )
    return fig

# Define a function to create a filtered scatter map based on the search text
def filtered_combined_graph(data, search_text):
    if search_text:
        data['Area Location'] = data['Area Location'].str.lower()
        data = data[data['Area Location'].astype(str).str.contains(search_text, case=False)]
    return combined_graph(data)

# Count the number of classes selected from the Business Category dropdown
def count_selected_classes(data, class_name):
    return len(data[data['Class'] == class_name])

# Define colors for styling
colors = {
    'background': '#111111',
    'text': '#7FDBFF',
    'gray': '#CCCCCC'
}

# Create a function to generate line breaks
def make_break(num_breaks):
    br_list = [html.Br()] * num_breaks
    return br_list

# Create a function to style the dropdowns
def style_drop():
    layout_style = {'width': '98%', 'margin': '0 auto'}
    return layout_style

# Create a Dash application
app = dash.Dash(__name__)

# Define the application layout
app.layout = html.Div(
    children=[
        html.Div(html.H1('Potential Clients Dashboard'), style={'text-align': 'center'}),
        *make_break(1),
        html.Div(
            children=[
                html.Div(children=[
                    html.H3('Selections'),
                    html.H4('Business Category'),
                    dcc.Dropdown(id='business_category', options=[{'label': sheet_name, 'value': sheet_name} for sheet_name in sheet_names],
                        value='Schools', style=style_drop()),
                    *make_break(1),
                    html.H4('Business Region'),
                    dcc.Dropdown(id='business_region', style=style_drop()),
                    *make_break(2),
                    dcc.Input(id='location_search', type='text', placeholder='Search by location',
                              style={'width': '94%', 'margin': '0 auto', 'height': '30px'})
                ],
                    style={'width': '20%', 'display': 'inline-block', 'background-color': colors['text'], 'height': '600px'}),
                html.Div(children=[
                    html.H3('Location on the map'),
                    dcc.Graph(id='location_map', style={'width': '95%', "height": "90%", 'margin': '0 auto'}),
                    html.Div(id='class_count', style={'text-align': 'center', 'color': colors['text']}),
                ],
                    style={'width': '80%', 'display': 'inline-block', 'background-color': colors['gray'],
                           'vertical-align': 'top', 'height': '600px'})
            ],
            style={'text-align': 'center', 'display': 'inline-block', 'width': '100%'}
        )
    ]
)

# Define a callback function to update the map based on location search
'''@app.callback(
    [Output('location_map', 'figure'), Output('class_count', 'children')],
    [Input('business_category', 'value'), Input('location_search', 'value')]
)
def update_output(selected_category, search_text):
    if selected_category is None:
        raise PreventUpdate

    data = combined_data[combined_data['Class'] == selected_category]

    fig = filtered_combined_graph(data, search_text)

    # Count the number of selected classes
    class_count = count_selected_classes(combined_data, selected_category)

    return fig, f'Count of {selected_category}: {class_count}' '''

@app.callback(
    [Output('location_map', 'figure'), Output('class_count', 'children')],
    [Input('business_category', 'value'), Input('location_search', 'value')]
)

def update_output(selected_category, search_text):
    if selected_category is None:
        raise PreventUpdate

    data = combined_data[combined_data['Class'] == selected_category]

    fig = filtered_combined_graph(data, search_text)

    # Count the number of selected classes
    class_count = count_selected_classes(combined_data, selected_category)

    if search_text:
        data['Area Location'] = data['Area Location'].str.lower()
        data = data[data['Area Location'].astype(str).str.contains(search_text, case=False)]
        class_count = len(data)

    return fig, f'Count of {selected_category}: {class_count}'

# Run the server
if __name__ == '__main__':
    app.run_server(debug=True)"""

