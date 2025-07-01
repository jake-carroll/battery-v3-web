import pandas as pd
import plotly.graph_objs as go

def generate_plot(
    file,
    custom_label="Battery 1",
    x_column='Test_Time(s)',
    left_y_columns=['Current(A)'],
    right_y_columns=['Voltage(V)'],
    color_pair=('blue', 'red'),
    plot_modes=None,
):
    if plot_modes is None:
        plot_modes = {
            "Voltage(V)": "lines",
            "Current(A)": "lines",
            "Charge_Capacity(Ah)": "markers",
            "Discharge_Capacity(Ah)": "markers",
            "Cycle_Index": "markers"
        }

    # Detect correct sheet
    sheet_prefix = "Statistics_1-" if x_column == "Cycle_Index" else "Channel_1-"
    sheet_names = pd.ExcelFile(file).sheet_names
    target_sheets = [s for s in sheet_names if s.startswith(sheet_prefix)]

    if not target_sheets:
        raise ValueError(f"No matching sheet with prefix '{sheet_prefix}' found")

    sheet_to_use = target_sheets[0]
    df = pd.read_excel(file, sheet_name=sheet_to_use)

    # Check required columns
    required = [x_column] + left_y_columns + right_y_columns
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    # Auto-scale micro units
    def scale_columns(df, columns):
        new_cols = []
        for col in columns:
            max_val = df[col].abs().max()
            if max_val < 0.01:
                df[col] = df[col] * 1e6
                new_col = f"{col} (µ)"
                df.rename(columns={col: new_col}, inplace=True)
                new_cols.append(new_col)
            else:
                new_cols.append(col)
        return new_cols

    scaled_left_y = scale_columns(df, left_y_columns)
    scaled_right_y = scale_columns(df, right_y_columns)

    fig = go.Figure()

    current_color, voltage_color = color_pair

    for col in scaled_left_y:
        fig.add_trace(go.Scatter(
            x=df[x_column],
            y=df[col],
            mode=plot_modes.get(col, "lines" if x_column != "Cycle_Index" else "markers"),
            name=f"{custom_label}: {col}",
            line=dict(color=current_color),
            yaxis='y1',
            marker=dict(size=10) if x_column == 'Cycle_Index' else None
        ))

    for col in scaled_right_y:
        fig.add_trace(go.Scatter(
            x=df[x_column],
            y=df[col],
            mode=plot_modes.get(col, "lines" if x_column != "Cycle_Index" else "markers"),
            name=f"{custom_label}: {col}",
            line=dict(color=voltage_color),
            yaxis='y2',
            marker=dict(size=10) if x_column == 'Cycle_Index' else None
        ))

    # Configure layout with dual y-axes
    fig.update_layout(
        title=custom_label,
        xaxis=dict(title=x_column, rangeslider=dict(visible=False)),
        yaxis=dict(
            title=dict(
                text=' / '.join(scaled_left_y),
                font=dict(color=current_color)
            ),
            tickfont=dict(color=current_color)
        ),
        yaxis2=dict(
            title=dict(
                text=' / '.join(scaled_right_y),
                font=dict(color=voltage_color)
            ),
            tickfont=dict(color=voltage_color),
            overlaying='y',
            side='right'
        ),

        legend=dict(x=0.01, y=0.99),
        hovermode='x unified',
        height=600,
    )

    return fig
