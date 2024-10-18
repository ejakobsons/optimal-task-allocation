import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


class TaskAllocation:
    def __init__(self, agents, products, languages, capacity):
        self.agents = agents
        self.products = products
        self.languages = languages
        self.capacity = capacity

    def get_allocation_df(self, prob, x, groupby=None):
        """
        Extract the task allocation as a DataFrame.
        """
        if prob.status != 1:
            raise ValueError(f"Optimization status: {prob.status}")

        allocation_df = pd.DataFrame(
            [
                (agent, product, language, int(n_tasks))
                for agent in self.agents
                for product in self.products
                for language in self.languages
                if (n_tasks := x[agent, product, language].value()) > 0
            ],
            columns=["agent", "product", "language", "tasks"],
        )

        # handle aggregation
        output_cols_dict = {"product": self.products, "language": self.languages}
        if groupby in output_cols_dict.keys():
            allocation_df = allocation_df.pivot_table(
                index="agent", columns=groupby, values="tasks", aggfunc="sum"
            )[output_cols_dict[groupby]]
            allocation_df = allocation_df.reindex(self.agents)
            allocation_df = allocation_df.fillna(0).astype(int)
        elif groupby is not None:
            raise ValueError(f"Unknown groupby option: {groupby}")

        return allocation_df

    def plot_allocation(self, allocation_df, add_capacity=True):
        """
        Plot a stacked chart of tasks assigned per agent (aggregated over languages)
        """

        axe = allocation_df.plot.bar(stacked=True, figsize=(8, 5))

        if add_capacity:
            # add markers for capacities
            axe.plot(self.capacity, "v", color="gray", label="capacity")

        # legend under the plot
        n_col = len(allocation_df.columns) + int(add_capacity)
        plt.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=n_col)

        return axe

    @staticmethod
    def plot_allocation_vs_target(
        df1, df2, labels=["target", "actual"], title="Target vs Actual Allocation", **kwargs
    ):
        """
        Create a clustered stacked bar plot for two dataframes with identical columns and index.
        Source: https://stackoverflow.com/questions/22787209/how-to-have-clusters-of-stacked-bars
        """

        n_col = len(df1.columns)
        n_ind = len(df1.index)
        axe = plt.subplot(111)
        hatches = ["///", ""]
        plt.rcParams.update({"hatch.color": "gray"})

        for i, df in enumerate([df1, df2]):
            axe = df.plot(
                kind="bar", linewidth=0, stacked=True, ax=axe, legend=False, grid=False, **kwargs
            )
            h, L = axe.get_legend_handles_labels()
            for j, pa in enumerate(h[i * n_col : (i + 1) * n_col]):
                for rect in pa.patches:
                    rect.set_x(rect.get_x() + 1 / 3.0 * i)
                    rect.set_hatch(hatches[i])
                    rect.set_width(1 / 3.0)

        axe.set_xticks((np.arange(0, 2 * n_ind, 2) + 1 / 3.0) / 2.0)
        axe.set_xticklabels(df1.index, rotation=0)
        axe.set_title(title)

        n = [axe.bar(0, 0, color="white", hatch=hatch) for hatch in hatches]

        #  column names legend
        l1 = axe.legend(
            h[n_col:], L[n_col:], loc="lower center", bbox_to_anchor=(0.5, -0.2), ncol=n_col
        )
        #  dataframe names legend
        if labels is not None:
            plt.legend(n, labels, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2)

        axe.add_artist(l1)
        return axe
