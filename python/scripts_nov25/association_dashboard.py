import socket
import dask.dataframe as dd
import panel as pn
import holoviews as hv
from dask.distributed import LocalCluster, Client
from holoviews import opts
import hvplot.pandas  # Enables .hvplot for Pandas DataFrames
import sys
import re

# Enable Holoviews and Panel extensions
hv.extension('bokeh')
pn.extension()

# Function to find a free port
def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]

# Main function to encapsulate the Dask setup and dashboard
def main(input_file, output_file):
    # Extract DOID numeric part from the input filename
    match = re.search(r'DOID_(\d+)', input_file)
    if not match:
        raise ValueError("Input file name must contain 'DOID_xxxx' format.")
    doid_number = match.group(1)
    dashboard_title = f"Interactive TICTAC Disease-Target Dashboard: DOID:{doid_number}"

    # Initialize Dask Client with LocalCluster
    free_port = find_free_port()
    cluster = LocalCluster(n_workers=2, threads_per_worker=2, dashboard_address=f":{free_port}")
    client = Client(cluster)
    print(f"Dask dashboard is running on: {client.dashboard_link}")

    # Load the data with Dask
    columns_to_load = [
        "doid_uniprot", "nDiseases", "nDrug", "nStud", "nPub", 
        "nStudyNewness", "nPublicationWeighted", "meanRankScore", 
        "disease_term", "drug_name", "idgTDL", "gene_symbol"
    ]
    df = dd.read_parquet(input_file, columns=columns_to_load)

    # Get unique idgTDL values for the filter options
    unique_tdl = df['idgTDL'].drop_duplicates().compute().tolist()

    # Set up Panel widgets for filtering and pagination
    tdl_filter = pn.widgets.MultiChoice(name='idgTDL Filter', options=unique_tdl, value=[])
    gene_filter = pn.widgets.TextInput(name='Gene Filter', placeholder="Enter gene name (e.g., ABCB11)")
    y_axis_choice = pn.widgets.Select(name='Y-axis Variable', options=['nPub', 'nDiseases', 'nDrug'], value='nPub')
    page_size = pn.widgets.IntSlider(name='Page Size', start=10, end=100, step=10, value=20)
    page_number = pn.widgets.IntSlider(name='Page Number', start=1, end=10, step=1, value=1)

    # Filter function for data
    def filter_data(tdl_filter, gene_filter, score_threshold=0):
        filtered_df = df
        if tdl_filter:
            filtered_df = filtered_df[filtered_df['idgTDL'].isin(tdl_filter)]
        if gene_filter:
            filtered_df = filtered_df[filtered_df['gene_symbol'].str.contains(gene_filter, case=False, na=False)]
        filtered_df = filtered_df[filtered_df['meanRankScore'] >= score_threshold]
        filtered_df = filtered_df.drop_duplicates(subset='doid_uniprot')
        return filtered_df

    # Function to create scatter plot
    @pn.depends(tdl_filter, gene_filter, y_axis_choice)
    def scatter_plot(tdl_filter, gene_filter, y_axis_choice):
        filtered_df = filter_data(tdl_filter, gene_filter)
        pandas_df = filtered_df.compute()
        
        # Create scatter plot with tooltips
        scatter = pandas_df.hvplot.scatter(
            x='meanRankScore', y=y_axis_choice, c='idgTDL', 
            hover_cols=['disease_term', 'gene_symbol', 'nPub', 'drug_name'],
            title="Disease-Target Association", xlabel="Evidence (meanRankScore)",
            ylabel=y_axis_choice, width=800, height=400
        )
        scatter.opts(colorbar=True, size=8)
        return scatter

    # Function to update table based on filters
    @pn.depends(tdl_filter, gene_filter, page_number, page_size)
    def update_table(tdl_filter, gene_filter, page_number, page_size):
        filtered_df = filter_data(tdl_filter, gene_filter)
        pandas_df = filtered_df.compute()
        start = (page_number - 1) * page_size
        end = start + page_size
        paginated_df = pandas_df.iloc[start:end]
        return hv.Table(paginated_df).opts(width=1000, height=600)

    # Function for exporting data
    def export_data():
        filtered_df = filter_data(tdl_filter.value, gene_filter.value)
        pandas_df = filtered_df.compute()
        return pandas_df.to_parquet(output_file, engine='pyarrow', index=False)

    # FileDownload widget
    export_button = pn.widgets.Button(name="Export Data", button_type="success")
    export_button.on_click(lambda event: export_data())

    # Layout for the dashboard
    dashboard = pn.Column(
        f"## {dashboard_title}",
        pn.Row(tdl_filter, gene_filter, y_axis_choice),
        pn.Row(page_size, page_number),
        pn.Row(update_table, scatter_plot),  # Display table and scatter plot side by side
        export_button  # Add export button below the table and plot
    )

    # Serve the dashboard
    dashboard.show()

    # Close the Dask client when done
    @pn.depends()
    def close_client():
        client.close()

# Run the main function in a protected block
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python script_name.py <input_file> <output_file>")
        sys.exit(1)

    # Get input and output filenames from command line arguments
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    main(input_file, output_file)
