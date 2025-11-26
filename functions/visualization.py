from lida import llm, Manager, TextGenerationConfig
from logger import logger
import plotly.express as px
import pandas as pd
import plotly.io as pio

lida = Manager(text_gen=llm("openai"))
textgen_config = TextGenerationConfig(n=1, temperature=0.2, use_cache=True)
library ="seaborn"
def visualizer(dataframe, query):
    summary = lida.summarize(dataframe, summary_method="llm", textgen_config=textgen_config, n_samples=3)
    try:
        charts = lida.visualize(summary=summary, goal=query, textgen_config=textgen_config, library=library)
        if charts and hasattr(charts[0], 'raster'):
            return charts[0], summary
        else:
            raise AttributeError("No raster attribute found in charts")
    except Exception as e:
        repaired_charts, repaired_summary = repair(charts, query, summary, error=str(e))
        if repaired_charts and hasattr(repaired_charts[0], 'raster'):
            return repaired_charts[0], repaired_summary
        else:
            return "Error in visualizing data: " + str(repaired_charts), repaired_summary


# def visualizer(dataframe):
#     try:
#         # Select numeric columns
#         numeric_cols = dataframe.select_dtypes(include='number').columns
#         print(len(numeric_cols))
#         # Plot scatter matrix if there are at least two numeric columns
#         if len(numeric_cols) >= 2:
#             print("making scatter")
#             fig = px.scatter_matrix(dataframe, dimensions=numeric_cols, title='Scatter Matrix of Numeric Columns')
            
#         elif len(numeric_cols) == 1:
#             # Plot histogram for single numeric column
#             fig = px.histogram(dataframe, x=numeric_cols[0], title=f'Distribution of {numeric_cols[0]}')
#         else:
#             # Plot a default bar chart using the first categorical column
#             categorical_cols = dataframe.select_dtypes(exclude='number').columns
#             if len(categorical_cols) > 0:
#                 fig = px.bar(dataframe, x=categorical_cols[0], title=f'Distribution of {categorical_cols[0]}')
#             else:
#                 # Empty figure if there's nothing to plot
#                 fig = px.Figure()
#                 fig.update_layout(title="No suitable data to plot")

#         # Convert the Plotly figure to an interactive HTML div
#         fig_html = fig.to_html(full_html=False)

#         return fig_html

#     except Exception as e:
#         return f"Error in visualizing data: {str(e)}"
# def visualizer(dataframe):
#     try:
#         # Select the first two columns of the dataframe for plotting
#         if dataframe.shape[1] < 2:
#             return "Dataframe does not have enough columns to plot."

#         # Create a new dataframe with the first two columns
#         df_plot = dataframe.iloc[:, :2]
#         df_plot = df_plot.melt(var_name='Variable', value_name='Value')

#         # Plot a bar chart using the first two columns
#         fig = px.bar(df_plot, x='Variable', y='Value', title='Bar Chart of First Two Columns')

#         # Convert the Plotly figure to an interactive HTML div
#         fig_html = pio.to_html(fig,full_html=False)

#         return fig_html

#     except Exception as e:
#         return f"Error in visualizing data: {str(e)}"

def repair(charts, query, summary, error):
    print("REPAIRING")
    try:
        feedback = f"""
        You are a helpful assistant highly skilled in revising visualization code to improve the quality of the code and visualization based on feedback. Assume that data in plot(data) contains a valid dataframe.
        You MUST return a full program. DO NOT include any preamble text. Do not include explanations or prose. Make background dark and not white.The error given was {error}.
        """
        repaired_code = lida.repair(
            code=charts,
            feedback=feedback,
            goal=query,
            summary=summary,
            textgen_config=textgen_config,
            library=library,
            return_error=True
        )
        if repaired_code and 'error' not in repaired_code:
            return repaired_code, summary  # Return repaired code if successful and no errors
        else:
            error_msg = "Failed to repair code: " + str(repaired_code)
            logger.error(error_msg)
            return "Error in visualizing data: " + error_msg, summary
    except Exception as e:
        error_msg = "Error in repairing visualization code: " + str(e)
        logger.error(error_msg)
        return error_msg, summary

def edit(charts, specifications, summary):
    textgen_config = TextGenerationConfig(n=1, temperature=0, use_cache=True)
    try:
        print("editing")
        edited_charts = lida.edit(
            code=charts,
            summary=summary,
            instructions=specifications,
            textgen_config=textgen_config,
            library=library
        )
        if edited_charts and hasattr(edited_charts[0], 'raster'):
            return edited_charts[0], summary
        else:
            raise AttributeError("No raster attribute found in edited charts")
    except Exception as e:
        print("going to repair edited code")
        return repair(charts, specifications, summary, error=str(e))

