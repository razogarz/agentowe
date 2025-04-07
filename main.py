import mesa
from matplotlib.pyplot import title

from models.simulation import PPModel

def run_simulation():
    model = PPModel()
    while True:
        model.step()
        data = model.datacollector.get_model_vars_dataframe()
        print(data)
        # plot data
        g = data.plot(
            title="Herbivore Population Over Time",
            xlabel="Time",
            ylabel="Population",
            legend=True,
        )
        g.set_ylim(0, model.num_agents)
        g.set_xlim(0, model.steps)
        g.set_title("Herbivore Population Over Time")
        g.figure.show()



if __name__ == "__main__":
    run_simulation()

