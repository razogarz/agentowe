import mesa
from models.simulation import PPModel

def run_simulation():
    model = PPModel()
    for i in range(100):
        model.step()

if __name__ == "__main__":
    run_simulation()

