import sys
import socket
import os
import dask.dataframe as dd
import panel as pn
from dask.distributed import LocalCluster, Client

# Enable Panel extension
pn.extension()

# Function to find a free port
def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]

# Main function to encapsulate the Dask setup and dashboard
def main(provenance_file):
    # Validate file input
    if not os.path.exists(provenance_file) or "provenance" not in provenance_file:
        print("Error: File must contain 'provenance' in its name and exist.")
        sys.exit(1)

    # Extract DOID from the file name
    doid_numeric_part = provenance_file.split("_")[0].split("/")[-1]

    # Initialize Dask Client with LocalCluster
    free_port = find_free_port()
    cluster = LocalCluster(n_workers=2, threads_per_worker=2, dashboard_address=f":{free_port}")
    client = Client(cluster)
    print(f"Dask dashboard is running on: {client.dashboard_link}")

    # Load the data with Dask
    print(f"Loading data from {provenance_file}...")
    columns_to_load = ["nct_id", "reference_type", "pmid", "citation"]
    df = dd.read_parquet(provenance_file, columns=columns_to_load)

    # Drop duplicates
    df = df.drop_duplicates()

    # Get unique filter values
    unique_nct_id = df['nct_id'].drop_duplicates().compute().tolist()
    unique_pmid = df['pmid'].drop_duplicates().compute().astype(str).str.rstrip('.0').tolist()
    unique_reference_type = df['reference_type'].drop_duplicates().compute().tolist()

    # Example dynamic header information
    disease_name = f"DOID:{doid_numeric_part}"

    # Set up Panel widgets
    filter_selector = pn.widgets.Select(
        name="Filter by NCT ID or PMID",
        options=["None"] + unique_nct_id + unique_pmid
    )
    reference_type_selector = pn.widgets.Select(
        name="Filter by Reference Type",
        options=["None"] + unique_reference_type
    )
    page_size = pn.widgets.IntSlider(name='Page Size', start=10, end=100, step=10, value=20)
    page_number = pn.widgets.IntSlider(name='Page Number', start=1, end=10, step=1, value=1)

    # Function to filter data based on the dropdown selections
    def filter_data(filter_value, reference_type):
        filtered_df = df
        if filter_value != "None":
            filtered_df = filtered_df[
                (filtered_df['nct_id'] == filter_value) | (filtered_df['pmid'].astype(str).str.rstrip('.0') == filter_value)
            ]
        if reference_type != "None":
            filtered_df = filtered_df[filtered_df['reference_type'] == reference_type]
        return filtered_df

    # Function to update the table
    @pn.depends(filter_selector.param.value, reference_type_selector.param.value, page_number.param.value, page_size.param.value)
    def update_table(filter_selector, reference_type_selector, page_number, page_size):
        filtered_df = filter_data(filter_selector, reference_type_selector)
        pandas_df = filtered_df.compute()

        # Convert `pmid` to string and clean up trailing decimals
        pandas_df['pmid'] = pandas_df['pmid'].astype(str).str.rstrip('.0')

        # Apply pagination
        total_rows = len(pandas_df)
        start = (page_number - 1) * page_size
        end = start + page_size

        # Adjust page number if out of range
        if start >= total_rows:
            return pn.pane.Markdown("No data available for the selected page.")

        paginated_df = pandas_df.iloc[start:end]

        # Display table with adjusted column widths
        html_table = (
            "<div style='overflow-x: auto; width: 100%;'>"
            "<table style='border-collapse: collapse; width: 100%;'>"
            "<thead>"
            + "".join(
                f'<th style="padding: 8px; text-align: left; border: 1px solid #ddd;">{col}</th>'
                for col in paginated_df.columns
            )
            + "</thead>"
            "<tbody>"
            + "".join(
                "<tr>"
                + "".join(
                    f'<td style="padding: 8px; border: 1px solid #ddd; '
                    f'{"width: 70%;" if col == "citation" else ""}">{value}</td>'
                    for col, value in zip(paginated_df.columns, row)
                )
                + "</tr>"
                for row in paginated_df.values
            )
            + "</tbody>"
            "</table></div>"
        )
        return pn.pane.HTML(html_table, width=1200, height=500)

    # Function to generate a descriptive header
    @pn.depends()
    def update_header():
        return pn.pane.HTML(
            f"""
            <div style="background-color: #f9f9f9; padding: 15px; border: 1px solid #ddd; width: 100%;">
                <h1 style="text-align: center; margin: 0; font-size: 24px;">TICTAC Provenance Dashboard</h1>
                <h2 style="text-align: center; margin: 0; font-size: 20px;">{disease_name}</h2>
            </div>
            """,
            width=1200
        )

    # Layout for the dashboard
    dashboard = pn.Column(
        update_header,
        pn.Row(filter_selector, reference_type_selector),
        pn.Row(page_size, page_number),
        update_table,
        width=1200,
        sizing_mode='stretch_width'
    )

    # Serve the dashboard
    dashboard.show()

    # Close the Dask client when done
    @pn.depends()
    def close_client():
        client.close()

# Run the main function in a protected block
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python general_provenance_dashboard.py <provenance_file>")
        sys.exit(1)

    provenance_file = sys.argv[1]
    main(provenance_file)

